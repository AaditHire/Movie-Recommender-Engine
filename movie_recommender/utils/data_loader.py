# utils/data_loader.py
#cd C:\Users\ASUS\movie_recommender
#.\venv310\Scripts\activate
# uvicorn app.main:app --reload
#streamlit run streamlit_app.py

import pandas as pd
import os

def load_movie_data(path="data/movies.csv"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")
    df = pd.read_csv(path)
    return df

# For quick testing:
if __name__ == "__main__":
    df = load_movie_data()
    print(df.head())
