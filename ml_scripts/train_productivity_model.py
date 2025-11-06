# ml_scripts/train_productivity_model.py

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
from core.ml_services import calculate_productivity_features
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from joblib import dump

# Define standard work hours for features
TIMEZONE = pytz.timezone('UTC')  # Adjust this to your local timezone if needed
# --- End Django Setup ---

print("Django environment successfully loaded.")


def generate_developer_productivity_data():
    """Pulls productivity features and creates a placeholder target Y."""
    developers = Developer.objects.all()
    data_list = []
    for dev in developers:
        features = calculate_productivity_features(dev.id)
        if features:
            # Placeholder Y: Assign a Y value based on features for training
            # The score is loosely based on lines changed + tickets closed * 5
            raw_score = features['total_lines_changed'] / 50 + features['high_value_tickets_closed'] * 15

            data_list.append({
                **features,  # Spread the features into the dictionary
                'productivity_score_target': raw_score  # Y value
            })
    return pd.DataFrame(data_list)


def train_and_save_productivity_model():
    df = generate_developer_productivity_data()

    if df.empty or len(df) < 2:
        print("Not enough data to train the productivity model.")
        return

    features = ['total_lines_changed', 'high_value_tickets_closed']
    X = df[features]
    Y = df['productivity_score_target']

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

    model = LinearRegression()  # Use Linear Regression
    model.fit(X_train, Y_train)

    model_filename = 'ml_scripts/productivity_score_model.joblib'
    dump(model, model_filename)
    print(f"\n✅ Productivity Score Model trained and saved to {model_filename}")

    score = model.score(X_test, Y_test)
    print(f"Model R-squared Score: {score:.2f}")


if __name__ == '__main__':
    train_and_save_productivity_model()

