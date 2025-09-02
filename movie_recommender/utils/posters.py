import os
import requests
from pathlib import Path
from PIL import Image
import io
import re

POSTER_DIR = "posters"
Path(POSTER_DIR).mkdir(exist_ok=True)

def save_poster_locally(title, image_url):
    filename = f"{POSTER_DIR}/{title.replace('/', '_')}.jpg"
    if os.path.exists(filename):
        return filename
    try:
        response = requests.get(image_url, timeout=10)
        image_bytes = response.content

        # ✅ Verify image integrity
        try:
            Image.open(io.BytesIO(image_bytes)).verify()
        except Exception as e:
            print(f"❌ Invalid image for {title}: {e}")
            return None

        with open(filename, 'wb') as f:
            f.write(image_bytes)
        return filename
    except Exception as e:
        print(f"⚠️ Error saving poster for {title}: {e}")
        return None

def fetch_poster(title, tmdb_api_key, omdb_api_key):
    def try_tmdb(clean_title, retries=3):
        for i in range(retries):
            try:
                print(f"📡 TMDB API Attempt {i+1}: {clean_title}")
                url = f"https://api.themoviedb.org/3/search/movie"
                params = {"api_key": tmdb_api_key, "query": clean_title}
                res = requests.get(url, params=params, timeout=10).json()
                if res.get("results"):
                    poster_path = res["results"][0].get("poster_path")
                    if poster_path:
                        print(f"✅ TMDB Poster Found: {clean_title}")
                        return save_poster_locally(title, f"https://image.tmdb.org/t/p/w500{poster_path}")
            except Exception as e:
                print(f"🔁 TMDB retry {i+1} failed: {e}")
        return None

    def try_omdb(clean_title):
        try:
            print(f"📡 OMDb API: {clean_title}")
            omdb_url = f"http://www.omdbapi.com/?apikey={omdb_api_key}&t={clean_title}"
            res = requests.get(omdb_url, timeout=10).json()
            if res.get("Poster") and res["Poster"] != "N/A":
                print(f"✅ Poster found via OMDb: {clean_title}")
                return save_poster_locally(title, res["Poster"])
        except Exception as e:
            print(f"❗ OMDb error for {clean_title}: {e}")
        return None

    # Clean title (remove year, fix commas)
    clean_title = title
    clean_title = clean_title.replace(", The", "")
    clean_title = clean_title.replace(", A", "")
    clean_title = clean_title.replace(", An", "")
    clean_title = re.sub(r"\(\d{4}\)", "", clean_title).strip()

    # Step 1: Try TMDB
    poster = try_tmdb(clean_title)
    if poster:
        return poster

    # Step 2: Fallback to OMDb
    poster = try_omdb(clean_title)
    if poster:
        return poster

    # Step 3: Retry TMDB again (in case TMDB was rate-limited earlier)
    poster = try_tmdb(clean_title)
    if poster:
        return poster

    print(f"❌ No poster found for: {title}")
    return None
