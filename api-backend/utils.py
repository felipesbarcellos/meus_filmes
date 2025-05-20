from functools import wraps
import datetime
import jwt
import requests
from flask import request, jsonify, current_app
from extensions import db
from models import Movie # Assuming Movie model is needed for _save_movie_details_if_not_exist

def require_user_match(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"msg": "Missing or invalid token"}), 401
        token = auth.split(" ")[1]
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token"}), 401
        except Exception:
            return jsonify({"msg": "Invalid token"}), 401 # Generic catch-all

        user_id_from_token = payload.get("user_id")
        
        # Extract user_id from various parts of the request for validation
        kwargs['auth_user_id'] = user_id_from_token
        return func(*args, **kwargs)
    return wrapper

def _get_tmdb_movie_details_internal(tmdb_id):
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    TMDB_BASE_URL = current_app.config.get("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    if not TMDB_API_KEY:
        print("ALERT: TMDB_API_KEY is not configured (internal).")
        return None
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=pt-BR"
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details for {tmdb_id} from TMDB (internal): {str(e)}")
        return None

def _save_movie_details_if_not_exist(tmdb_id):
    """
    Checks if a movie exists in the local DB. If not, fetches from TMDB and saves it.
    Returns the Movie object or None if fetching fails.
    """
    movie = db.session.get(Movie, tmdb_id) # Use db.session.get for primary key lookup
    if movie:
        return movie

    tmdb_details = _get_tmdb_movie_details_internal(tmdb_id)
    if not tmdb_details:
        return None

    release_date_str = tmdb_details.get("release_date")
    release_date_obj = None
    if release_date_str:
        try:
            release_date_obj = datetime.datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Warning: Could not parse release_date '{release_date_str}' for tmdb_id {tmdb_id}")
            release_date_obj = None

    new_movie = Movie(
        tmdb_id=tmdb_details.get("id"),
        title=tmdb_details.get("title"),
        overview=tmdb_details.get("overview"),
        poster_path=tmdb_details.get("poster_path"),
        release_date=release_date_obj,
        rating=tmdb_details.get("vote_average"),
        genres=tmdb_details.get("genres")
    )
    db.session.add(new_movie)
    try:
        db.session.commit()
        return new_movie
    except Exception as e:
        db.session.rollback()
        print(f"Error saving movie {tmdb_id} to database: {str(e)}")
        return None
