# test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Movie Recommender API is live!"

def test_recommend_valid_user():
    response = client.get("/recommend/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_recommend_invalid_user():
    response = client.get("/recommend/999999") 
    assert response.status_code == 200
    assert "error" in response.json()

def test_popular_movies():
    response = client.get("/popular")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "title" in response.json()[0]

def test_add_rating():
    payload = {"userId": 1, "movieId": 1, "rating": 4.0}
    response = client.post("/rate", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Rating submitted successfully!"

def test_retrain_model():
    response = client.post("/retrain")
    assert response.status_code == 200
    assert "message" in response.json()
