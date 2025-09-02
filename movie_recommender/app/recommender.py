# app/recommender.py

import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
import joblib

def train_and_save_model():
    # Load ratings
    ratings = pd.read_csv("data/ratings.csv")

    # Define a reader (Surprise requires this)
    reader = Reader(rating_scale=(0.5, 5.0))

    # Load dataset from pandas DataFrame
    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    
    # Train-test split
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

    # Train SVD
    algo = SVD()
    algo.fit(trainset)

    # Save model
    joblib.dump(algo, "models/svd_model.pkl")
    print("✅ Model trained and saved as 'models/svd_model.pkl'")

def predict_rating(user_id, movie_id):
    # Load model
    algo = joblib.load("models/svd_model.pkl")
    prediction = algo.predict(user_id, movie_id)
    return prediction.est

# For manual testing
if __name__ == "__main__":
    train_and_save_model()
    # Example prediction
    print(f"Predicted rating: {predict_rating(1, 31):.2f}")