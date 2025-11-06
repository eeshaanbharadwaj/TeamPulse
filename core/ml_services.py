# core/ml_services.py
import os
from joblib import load
import pandas as pd
from django.conf import settings
from core.models import Developer, Commit, JiraTicket, ChatData
from datetime import datetime, timedelta
import pytz
from django.db.models import Avg, Sum, Q, Count

# Path to the saved model file
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_scripts/burnout_risk_model.joblib')
PROD_MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_scripts/productivity_score_model.joblib')
COLLAB_MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_scripts/collaboration_score_model.joblib')

# Define standard work hours for features
TIMEZONE = pytz.timezone('UTC')  # Adjust this to your local timezone if needed
START_HOUR = 9
END_HOUR = 18
WEEKENDS = [5, 6]  # 5=Saturday, 6=Sunday


def calculate_single_developer_features(developer_id):
    """Calculates all ML features for a specific developer."""
    try:
        dev = Developer.objects.get(pk=developer_id)
    except Developer.DoesNotExist:
        return None  # Return None if developer isn't found

    analysis_start_date = datetime.now(TIMEZONE) - timedelta(days=30)
    
    # --- FEATURE 1: WORK-LIFE BALANCE (Commits outside work hours) ---
    recent_commits = dev.commit_set.filter(timestamp__gte=analysis_start_date)
    after_hours_commits = 0
    weekend_commits = 0
    total_commits = recent_commits.count()

    for commit in recent_commits:
        commit_hour = commit.timestamp.astimezone(TIMEZONE).hour
        commit_day = commit.timestamp.astimezone(TIMEZONE).weekday()

        if commit_hour < START_HOUR or commit_hour >= END_HOUR:
            after_hours_commits += 1
        
        if commit_day in WEEKENDS:
            weekend_commits += 1

    after_hours_ratio = after_hours_commits / total_commits if total_commits > 0 else 0
    weekend_ratio = weekend_commits / total_commits if total_commits > 0 else 0

    # --- FEATURE 2: CURRENT LOAD (Open Tickets & Avg Time) ---
    open_tickets = dev.assigned_tickets.exclude(status__in=['Done', 'Closed']).count()
    
    closed_tickets = dev.assigned_tickets.filter(status__in=['Done', 'Closed'], closed_at__gte=analysis_start_date)
    # Use Django's Avg aggregation here (requires models.py import)
    avg_time_spent = closed_tickets.aggregate(Avg('time_spent_hours'))['time_spent_hours__avg'] or 0.0

    # Ensure avg_time_spent is a float, not Decimal or None
    if avg_time_spent is None:
        avg_time_spent = 0.0
    avg_time_spent = float(avg_time_spent)
    
    # Return features dictionary
    return {
        'after_hours_ratio': after_hours_ratio,
        'weekend_ratio': weekend_ratio,
        'open_tickets': open_tickets,
        'avg_time_spent': avg_time_spent,
    }

def get_burnout_risk(developer_data_dict):
    """Loads the model and predicts the burnout risk for a single developer."""

    try:
        # 1. Load the model
        model = load(MODEL_PATH)
    except FileNotFoundError:
        return {'error': 'ML model not found. Run the training script first.'}, 500

    # 2. Prepare the input data (must match the features used for training!)
    # The input data should be a dictionary from the developer view
    try:
        input_df = pd.DataFrame([developer_data_dict])

        # Ensure columns are in the exact order the model expects
        features = ['after_hours_ratio', 'weekend_ratio', 'open_tickets', 'avg_time_spent']

        # Select and reorder the required columns
        X_predict = input_df[features]

    except KeyError as e:
        return {'error': f'Missing feature in input data: {e}'}, 400


    # 3. Predict the result
    prediction = model.predict(X_predict)[0]
    # Get the probability (optional, but gives a score)
    probability = model.predict_proba(X_predict)[0][1] # Probability of risk (class 1)

    # 4. Return the results
    return {
        'risk_level': 'High' if prediction == 1 else 'Low',
        'risk_score': round(float(probability) * 100, 2)
    }, 200


def calculate_productivity_features(developer_id):
    """Calculates all ML features for a specific developer for Productivity."""
    try:
        dev = Developer.objects.get(pk=developer_id)
    except Developer.DoesNotExist:
        return None

    analysis_start_date = datetime.now(TIMEZONE) - timedelta(days=30) 
    
    # --- FEATURE 1: COMMIT VOLUME ---
    commit_metrics = dev.commit_set.filter(timestamp__gte=analysis_start_date).aggregate(
        total_added=Sum('lines_added'), 
        total_removed=Sum('lines_removed')
    )
    total_lines_changed = (commit_metrics.get('total_added') or 0) + \
                          (commit_metrics.get('total_removed') or 0)

    # --- FEATURE 2: TICKET THROUGHPUT (High-Value) ---
    high_value_tickets_closed = dev.assigned_tickets.filter(
        Q(status='Done') | Q(status='Closed'), 
        closed_at__gte=analysis_start_date,
        story_points__gt=5  # Focus on high-value tickets
    ).count()

    # Return features dictionary
    return {
        'total_lines_changed': total_lines_changed,
        'high_value_tickets_closed': high_value_tickets_closed,
    }


def get_productivity_score(developer_data_dict):
    """Loads the productivity model and predicts the score."""
    try:
        model = load(PROD_MODEL_PATH)
    except FileNotFoundError:
        return {'error': 'Productivity model not found. Run training script.'}, 500

    try:
        input_df = pd.DataFrame([developer_data_dict])
        features = ['total_lines_changed', 'high_value_tickets_closed']
        X_predict = input_df[features]
    except KeyError as e:
        return {'error': f'Missing feature: {e}'}, 400

    # Prediction returns a raw value
    raw_prediction = model.predict(X_predict)[0]
    
    # Normalize the score to a 0-100 scale (simple clipping for demo)
    normalized_score = max(0, min(100, int(raw_prediction / 100)))  # Divide by 100 to keep it manageable

    return {
        'score': normalized_score,
        'status': 'High' if normalized_score >= 80 else 'Medium' if normalized_score >= 50 else 'Low'
    }, 200


def calculate_collaboration_features(developer_id):
    """Calculates all ML features for a specific developer for Collaboration."""
    try:
        dev = Developer.objects.get(pk=developer_id)
    except Developer.DoesNotExist:
        return None

    analysis_start_date = datetime.now(TIMEZONE) - timedelta(days=30) 
    
    # --- FEATURE 1: AVERAGE SENTIMENT ---
    sent_messages = dev.sent_messages.filter(timestamp__gte=analysis_start_date)
    
    # FIX: Use get() and set a default of 0.0 before casting
    avg_sentiment_value = sent_messages.aggregate(Avg('sentiment_score'))['sentiment_score__avg']
    avg_sentiment = float(avg_sentiment_value) if avg_sentiment_value is not None else 0.0

    # --- FEATURE 2: RESPONSE RATIO ---
    received_messages = dev.received_messages.filter(timestamp__gte=analysis_start_date)
    
    total_received = received_messages.count()
    quick_responses = received_messages.filter(is_quick_response=True).count()
    
    response_ratio = quick_responses / total_received if total_received > 0 else 0.0
    
    # Return features dictionary
    return {
        'avg_sentiment': avg_sentiment, # Now guaranteed to be float
        'response_ratio': response_ratio,
    }


def get_collaboration_score(developer_data_dict):
    """Loads the collaboration model and predicts the score."""
    try:
        model = load(COLLAB_MODEL_PATH)
    except FileNotFoundError:
        return {'error': 'Collaboration model not found. Run training script.'}, 500

    try:
        input_df = pd.DataFrame([developer_data_dict])
        features = ['avg_sentiment', 'response_ratio']
        X_predict = input_df[features]
    except KeyError as e:
        return {'error': f'Missing feature: {e}'}, 400

    # Prediction returns a class (0, 1, or 2)
    prediction_class = model.predict(X_predict)[0]
    
    # Map class index to a meaningful label and score
    label_map = {
        2: {'status': 'High', 'score': 90},
        1: {'status': 'Medium', 'score': 60},
        0: {'status': 'Low', 'score': 30},
    }
    
    result = label_map.get(prediction_class, {'status': 'Error', 'score': 0})
    
    return result, 200