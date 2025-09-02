import os
import csv
import pandas as pd
from surprise import SVD, Dataset, Reader

# Paths
ratings_path = "data/ratings.csv"
new_ratings_path = "data/new_ratings.csv"
movies_path = "data/movies.csv"

# Global cache
model = None
trainset = None
top_n = {}
movie_titles = {}

# Load movie titles
try:
    movie_titles = pd.read_csv(movies_path).set_index('movieId')['title'].to_dict()
except:
    print("⚠️ Warning: movies.csv not found.")

# Initial training
def load_and_train_model():
    global model, trainset
    original = pd.read_csv(ratings_path)
    if os.path.exists(new_ratings_path):
        new = pd.read_csv(new_ratings_path)
        df = pd.concat([original, new], ignore_index=True)
    else:
        df = original

    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(df[["userId", "movieId", "rating"]], reader)
    trainset = data.build_full_trainset()

    model = SVD()
    model.fit(trainset)
    return df

# Load model once at startup
ratings_df = load_and_train_model()

def get_top_n(user_id, n=10):
    global model, ratings_df

    if user_id not in ratings_df['userId'].unique():
        return {"error": f"User ID {user_id} not found."}

    seen = ratings_df[ratings_df['userId'] == user_id]['movieId'].tolist()
    candidates = [m for m in ratings_df['movieId'].unique() if m not in seen]

    predictions = [(mid, model.predict(user_id, mid).est) for mid in candidates]
    predictions.sort(key=lambda x: x[1], reverse=True)
    top = predictions[:n]

    return [
        {
            "movieId": int(mid),
            "title": movie_titles.get(int(mid), "Unknown"),
            "predicted_rating": round(score, 2)
        } for mid, score in top
    ]

def get_popular_movies(n=10):
    global ratings_df
    top = (
        ratings_df.groupby('movieId')['rating']
        .agg(['count', 'mean'])
        .sort_values(by=['count', 'mean'], ascending=False)
        .head(n)
        .index.tolist()
    )
    return [{"movieId": mid, "title": movie_titles.get(mid, "Unknown")} for mid in top]

def add_rating(user_id, movie_id, rating):
    # Append to new_ratings.csv
    file_exists = os.path.isfile(new_ratings_path)
    with open(new_ratings_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["userId", "movieId", "rating"])
        writer.writerow([user_id, movie_id, rating])

    return {
        "message": "Rating submitted successfully!",
        "userId": user_id,
        "movieId": movie_id,
        "rating": rating
    }

def retrain_model():
    global model, trainset, ratings_df

    print("🔁 Retraining model...")
    ratings_df = load_and_train_model()  # Refresh global df
    return {"message": "✅ Model retrained using new_ratings.csv!"}
