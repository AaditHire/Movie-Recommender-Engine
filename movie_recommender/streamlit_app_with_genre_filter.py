
import streamlit as st
import pandas as pd
import requests
import os
from PIL import Image
from utils.posters import fetch_poster  # TMDB + OMDb + fallback

# === CONFIG ===
BASE_URL = "http://127.0.0.1:8000"
MOVIES_CSV = "data/movies.csv"
RATINGS_LOG = "data/new_ratings.csv"
TMDB_API_KEY = "your api key"
OMDB_API_KEY = "your api key"
PLACEHOLDER_IMG = "placeholder.jpg"

# === DARK THEME CSS ===
st.set_page_config(page_title="🎥 Movie Recommender", layout="wide")
st.markdown("""
<style>
body, .stApp { background-color: #141414; color: #fff; }
h1, h2, h3, h4, h5, h6, .stMarkdown { color: #fff; }
.stButton>button {
    color: white; background-color: #e50914; border: none; padding: 0.5em 1.2em;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #f40612; transform: scale(1.05);
}
img { border-radius: 8px; transition: transform 0.2s; }
img:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# === LOAD MOVIES ===
@st.cache_data
def load_movies():
    df = pd.read_csv(MOVIES_CSV)
    return df.set_index("movieId")["title"].to_dict(), df

movie_titles, movies_df = load_movies()

# === GENRES ===
def get_all_genres(df):
    genres = set()
    for genre_list in df['genres'].dropna():
        genres.update(genre_list.split('|'))
    return sorted(genres)

all_genres = get_all_genres(movies_df)
selected_genres = st.sidebar.multiselect("Filter by Genre", all_genres, default=all_genres)

# === SIDEBAR ===
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Netflix_icon.svg", width=80)
page = st.sidebar.radio("Navigate", ["🏠 Recommend", "📈 Popular", "📤 Rate", "🧾 My Ratings", "🔁 Retrain", "🔍 Search"])

# === IMAGE LOADER WITH FALLBACK ===
def display_poster(image_path, width=120):
    try:
        if image_path and os.path.exists(image_path):
            st.image(Image.open(image_path), width=width)
        else:
            st.image(Image.open(PLACEHOLDER_IMG), width=width)
    except Exception as e:
        print(f"⚠️ Image load error: {e}")
        st.image(Image.open(PLACEHOLDER_IMG), width=width)

# === PAGES ===
if page == "🏠 Recommend":
    st.title("🎯 Personalized Recommendations")
    user_id = st.number_input("Enter your User ID:", min_value=1, step=1)
    if st.button("Get Recommendations"):
        try:
            res = requests.get(f"{BASE_URL}/recommend/{user_id}")
            if res.status_code == 200:
                st.subheader("🍿 Top Picks for You")
                for movie in res.json():
                    if selected_genres:
                        genres = movies_df[movies_df['title'] == movie['title']]['genres'].values
                        if not genres.any() or not any(g in genres[0].split('|') for g in selected_genres):
                            continue
                    poster = fetch_poster(movie['title'], TMDB_API_KEY, OMDB_API_KEY)
                    cols = st.columns([1, 4])
                    with cols[0]: display_poster(poster)
                    with cols[1]:
                        st.markdown(f"**{movie['title']}**  ⭐ **{movie['predicted_rating']}**", unsafe_allow_html=True)
            else:
                st.warning(res.json().get("error", "No recommendations found."))
        except Exception as e:
            st.error(f"❌ Error fetching recommendations: {e}")

elif page == "📈 Popular":
    st.title("🔥 Trending Movies")
    if st.button("Show Popular"):
        try:
            res = requests.get(f"{BASE_URL}/popular")
            if res.status_code == 200:
                st.subheader("🎬 What's Hot Now")
                for movie in res.json():
                    if selected_genres:
                        genres = movies_df[movies_df['title'] == movie['title']]['genres'].values
                        if not genres.any() or not any(g in genres[0].split('|') for g in selected_genres):
                            continue
                    poster = fetch_poster(movie['title'], TMDB_API_KEY, OMDB_API_KEY)
                    cols = st.columns([1, 4])
                    with cols[0]: display_poster(poster)
                    with cols[1]:
                        st.markdown(f"**{movie['title']}**", unsafe_allow_html=True)
            else:
                st.warning("Failed to fetch popular movies.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

elif page == "📤 Rate":
    st.title("⭐ Submit a Rating")
    col1, col2 = st.columns(2)
    with col1:
        rate_user = st.number_input("User ID", min_value=1, key="rate_uid")
        rate_movie = st.selectbox("Choose a movie", options=list(movie_titles.values()))
    with col2:
        rating_val = st.slider("Rating", min_value=0.5, max_value=5.0, value=3.0, step=0.5)
    if st.button("Submit Rating"):
        try:
            movie_id = movies_df[movies_df['title'] == rate_movie].iloc[0]["movieId"]
            payload = {"userId": int(rate_user), "movieId": int(movie_id), "rating": float(rating_val)}
            res = requests.post(f"{BASE_URL}/rate", json=payload)
            st.success("✅ Rating submitted successfully!" if res.status_code == 200 else "❌ Failed to submit rating.")
        except Exception as e:
            st.error(f"🚨 Error: {e}")

elif page == "🧾 My Ratings":
    st.title("📜 Your Rating History")
    if os.path.exists(RATINGS_LOG):
        df = pd.read_csv(RATINGS_LOG)
        df = df.merge(movies_df, on="movieId", how="left")
        df = df[["userId", "title", "rating"]].sort_values(by=["userId"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No rating history available yet.")

elif page == "🔁 Retrain":
    st.title("🔧 Retrain the Model")
    if st.button("Retrain Now"):
        try:
            res = requests.post(f"{BASE_URL}/retrain")
            st.success(res.json().get("message", "Model retrained!")) if res.status_code == 200 else st.error("❌ Retraining failed.")
        except Exception as e:
            st.error(f"💥 Retrain request failed: {e}")

elif page == "🔍 Search":
    st.title("🔍 Movie Search")
    query = st.text_input("Enter movie title:")
    if st.button("Search"):
        matched = movies_df[movies_df["title"].str.contains(query, case=False, na=False)]
        if not matched.empty:
            for _, row in matched.iterrows():
                poster = fetch_poster(row["title"], TMDB_API_KEY, OMDB_API_KEY)
                cols = st.columns([1, 5])
                with cols[0]: display_poster(poster, width=100)
                with cols[1]: st.markdown(f"**{row['title']}**")
        else:
            st.warning("No movies matched your query.")
