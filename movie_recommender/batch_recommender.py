import pandas as pd
from surprise import SVD, Dataset, Reader
import json

# Load ratings
ratings = pd.read_csv("data/ratings.csv")

# Load movie titles
movies = pd.read_csv("data/movies.csv")
movie_map = dict(zip(movies['movieId'], movies['title']))

# Prepare the Surprise dataset
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
trainset = data.build_full_trainset()

# Train the SVD model
algo = SVD()
algo.fit(trainset)

# Get all user and movie IDs
all_user_ids = ratings['userId'].unique()
all_movie_ids = ratings['movieId'].unique()

top_n = []
for uid in all_user_ids:
    user_rated_movies = ratings[ratings['userId'] == uid]['movieId'].values
    unrated_movies = [mid for mid in all_movie_ids if mid not in user_rated_movies]

    predictions = [algo.predict(uid, mid) for mid in unrated_movies]
    predictions.sort(key=lambda x: x.est, reverse=True)
    top_predictions = predictions[:10]

    for pred in top_predictions:
        movie_id = pred.iid
        movie_title = movie_map.get(int(movie_id), "Unknown Title")
        top_n.append({
            "userId": int(uid),
            "movieId": int(movie_id),
            "title": movie_title,
            "predicted_rating": round(pred.est, 2)
        })

# Save to JSON
with open("batch_top_n.json", "w", encoding='utf-8') as f:
    json.dump(top_n, f, indent=2)

print("✅ Batch Top-N with Titles saved to batch_top_n.json")
