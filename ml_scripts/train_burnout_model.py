# ml_scripts/train_burnout_model.py

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(PROJECT_ROOT)

import django
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- Django Setup (Crucial for external scripts) ---
# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teampulse_backend.settings')
django.setup()

# Now we can import our models
from core.models import Developer, Commit, JiraTicket 
from django.db.models import Avg
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from joblib import dump

# Define standard work hours for features
TIMEZONE = pytz.timezone('UTC') # Adjust this to your local timezone if needed
START_HOUR = 9
END_HOUR = 18
WEEKENDS = [5, 6] # 5=Saturday, 6=Sunday
# --- End Django Setup ---

print("Django environment successfully loaded.")


def generate_developer_features():
    """Pulls and aggregates features for each developer."""
    developers = Developer.objects.all()
    feature_list = []
    
    # Define a window (e.g., last 30 days) for current burnout analysis
    analysis_start_date = datetime.now(TIMEZONE) - timedelta(days=30) 

    for dev in developers:
        # --- FEATURE 1: WORK-LIFE BALANCE (Commits outside work hours) ---
        recent_commits = dev.commit_set.filter(timestamp__gte=analysis_start_date)
        
        after_hours_commits = 0
        weekend_commits = 0
        total_commits = recent_commits.count()

        for commit in recent_commits:
            commit_hour = commit.timestamp.astimezone(TIMEZONE).hour
            commit_day = commit.timestamp.astimezone(TIMEZONE).weekday() # Monday is 0, Sunday is 6

            # Check for after-hours
            if commit_hour < START_HOUR or commit_hour >= END_HOUR:
                after_hours_commits += 1
            
            # Check for weekend commits
            if commit_day in WEEKENDS:
                weekend_commits += 1

        # Calculate a ratio to normalize the feature
        after_hours_ratio = after_hours_commits / total_commits if total_commits > 0 else 0
        weekend_ratio = weekend_commits / total_commits if total_commits > 0 else 0

        # --- FEATURE 2: CURRENT LOAD (Open Tickets) ---
        open_tickets = dev.assigned_tickets.exclude(status__in=['Done', 'Closed']).count()
        
        # --- FEATURE 3: HIGH-STRESS WORK (Average time on tickets) ---
        closed_tickets = dev.assigned_tickets.filter(status__in=['Done', 'Closed'], closed_at__gte=analysis_start_date)
        avg_time_spent = closed_tickets.aggregate(Avg('time_spent_hours'))['time_spent_hours__avg'] or 0

        # --- FIX: New, Stricter Logic for Target Variable Assignment ---
        # High risk (1) only if BOTH late work AND high load conditions are met.
        # This makes it harder to achieve a '1', ensuring some developers remain '0'.
        
        # Stricter Risk Condition: Must have high after-hours activity AND high ticket load
        risk_condition = (after_hours_ratio > 0.3) and (open_tickets >= 10)
        
        # Alternatively, you can use a forced randomization for low data volume:
        # risk_condition = random.random() < 0.5 # 50% chance of being high risk if data is low
        
        # Aggregate all features
        feature_list.append({
            'developer_id': dev.id,
            'after_hours_ratio': after_hours_ratio,
            'weekend_ratio': weekend_ratio,
            'open_tickets': open_tickets,
            'avg_time_spent': avg_time_spent,
            # Placeholder for the target variable (Y) - you would define this manually 
            # or based on HR data in a real application
            # Apply the new, stricter risk condition:
            'burnout_risk_label': 1 if risk_condition else 0 
        })

    return pd.DataFrame(feature_list)


def train_and_save_model():
    """Trains the model and saves it to a joblib file."""
    df = generate_developer_features()
    
    if df.empty or len(df) < 2:
        print("Not enough data to train the model. Need at least two developers.")
        return

    # 1. Define Features (X) and Target (Y)
    features = ['after_hours_ratio', 'weekend_ratio', 'open_tickets', 'avg_time_spent']
    X = df[features]
    Y = df['burnout_risk_label']  # This is the target we're trying to predict

    # 2. Split Data (not strictly necessary with such a small dataset, but good practice)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

    # 3. Train the Model (Logistic Regression for a simple binary classification)
    model = LogisticRegression()
    model.fit(X_train, Y_train)

    # 4. Save the Model
    model_filename = 'ml_scripts/burnout_risk_model.joblib'
    dump(model, model_filename)
    print(f"\n✅ Burnout Risk Model trained and saved to {model_filename}")
    
    # Optional: Print some test results
    score = model.score(X_test, Y_test)
    print(f"Model Test Accuracy (if data available): {score:.2f}")


if __name__ == '__main__':
    train_and_save_model()