import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from utils.recommender import get_top_n, get_popular_movies, add_rating,retrain_model
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Movie Recommender API is live!"}

@app.get("/recommend/{user_id}")
def recommend(user_id: int, n: int = 5):
    return get_top_n(user_id, n)

@app.get("/popular")
def popular():
    return get_popular_movies()

class RatingRequest(BaseModel):
    userId: int
    movieId: int
    rating: float

@app.post("/rate")
def rate_movie(req: RatingRequest):
    return add_rating(req.userId, req.movieId, req.rating)

@app.post("/retrain")
def retrain():
    return retrain_model()


