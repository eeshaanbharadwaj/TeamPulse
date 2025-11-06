# ml_scripts/train_collaboration_model.py

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
from core.ml_services import calculate_collaboration_features, COLLAB_MODEL_PATH
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from joblib import dump

# Define standard work hours for features
TIMEZONE = pytz.timezone('UTC')  # Adjust this to your local timezone if needed
# --- End Django Setup ---

print("Django environment successfully loaded.")


def generate_developer_collaboration_data():
    """Pulls collaboration features and creates a placeholder target Y."""
    developers = Developer.objects.all()
    data_list = []
    for dev in developers:
        features = calculate_collaboration_features(dev.id)
        if features:
            # Placeholder Y: Assign a Y class based on features for training (0=Low, 1=Medium, 2=High)
            if features['avg_sentiment'] > 0.75 and features['response_ratio'] > 0.6:
                collaboration_class = 2 # High
            elif features['avg_sentiment'] > 0.5 or features['response_ratio'] > 0.4:
                collaboration_class = 1 # Medium
            else:
                collaboration_class = 0 # Low

            data_list.append({
                **features,
                'collaboration_class_target': collaboration_class # Y value
            })
    return pd.DataFrame(data_list)


def train_and_save_collaboration_model():
    df = generate_developer_collaboration_data()

    if df.empty or len(df) < 2:
        print("Not enough data to train the collaboration model.")
        return

    features = ['avg_sentiment', 'response_ratio']
    X = df[features]
    Y = df['collaboration_class_target']

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

    model = KNeighborsClassifier(n_neighbors=3) # Use KNN
    model.fit(X_train, Y_train)

    # Use os.path.basename for cross-platform compatibility
    model_filename = os.path.basename(COLLAB_MODEL_PATH)
    model_path = os.path.join('ml_scripts', model_filename)
    dump(model, model_path)
    print(f"\n✅ Collaboration Score Model trained and saved to {model_path}")

    score = model.score(X_test, Y_test)
    print(f"Model Classification Accuracy: {score:.2f}")


if __name__ == '__main__':
    train_and_save_collaboration_model()

