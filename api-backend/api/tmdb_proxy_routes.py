from flask import Blueprint, jsonify, request, current_app
import requests
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import _get_tmdb_movie_details_internal, _save_movie_details_if_not_exist

tmdb_proxy_bp = Blueprint('tmdb_proxy', __name__, url_prefix='/tmdb')

TMDB_BASE_URL = "https://api.themoviedb.org/3"

@tmdb_proxy_bp.route("/config", methods=["GET"])
def get_tmdb_config():
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    try:
        response = requests.get(f"{TMDB_BASE_URL}/configuration?api_key={TMDB_API_KEY}")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/popular", methods=["GET"])
def get_popular_movies():
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    page = request.args.get("page", 1)
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR&page={page}"
        )
        response.raise_for_status()
        data = response.json()

        # Removed call to _save_movie_details_if_not_exist
        # if data and "results" in data:
        #     for movie_summary in data["results"]:
        #         if movie_summary and movie_summary.get("id"):
        #             _save_movie_details_if_not_exist(movie_summary.get("id"))
        
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/movie/<int:tmdb_id>", methods=["GET"])
def get_movie_details(tmdb_id):
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    
    try:
        # _save_movie_details_if_not_exist will:
        # 1. Return the Movie object from DB if it exists.
        # 2. If not in DB, fetch from TMDB (basic details), save to DB, and return the new Movie object.
        # 3. Return None if not in DB and TMDB fetch fails.
        movie_object = _save_movie_details_if_not_exist(tmdb_id)

        if movie_object:
            # Movie is in our DB (either pre-existing or just fetched and saved).
            # Serialize and return the data from our Movie object.
            # Note: This response will only contain fields stored in the Movie model,
            # and will not include data from TMDB's 'append_to_response' (e.g., credits, recommendations).
            movie_dict = {
                "id": movie_object.tmdb_id,
                "title": movie_object.title,
                "overview": movie_object.overview,
                "poster_path": movie_object.poster_path,
                "release_date": movie_object.release_date.isoformat() if movie_object.release_date else None,
                "vote_average": movie_object.rating,
                "genres": movie_object.genres  # Assumed to be JSON-serializable (list of dicts)
            }
            return jsonify(movie_dict)
        else:
            # Movie not found in DB and could not be fetched/saved by _save_movie_details_if_not_exist.
            return jsonify({"error": f"Movie with TMDB ID {tmdb_id} not found or could not be retrieved."}), 404
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_movie_details for TMDB ID {tmdb_id}: {str(e)}")
        return jsonify({"error": "An unexpected server error occurred"}), 500

@tmdb_proxy_bp.route("/search", methods=["GET"])
def search_movies():
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    query = request.args.get("query")
    page = request.args.get("page", 1)
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={query}&page={page}"
        )
        response.raise_for_status()
        data = response.json()

        # Removed call to _save_movie_details_if_not_exist
        # if data and "results" in data:
        #     for movie_summary in data["results"]:
        #         if movie_summary and movie_summary.get("id"):
        #             _save_movie_details_if_not_exist(movie_summary.get("id"))

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/movie/<int:tmdb_id>/credits", methods=["GET"])
def get_movie_credits(tmdb_id):
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/credits?api_key={TMDB_API_KEY}&language=pt-BR"
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/movie/<int:tmdb_id>/recommendations", methods=["GET"])
def get_movie_recommendations(tmdb_id):
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    page = request.args.get("page", 1)
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/recommendations?api_key={TMDB_API_KEY}&language=pt-BR&page={page}"
        )
        response.raise_for_status()
        data = response.json()

        # Removed call to _save_movie_details_if_not_exist
        # if data and "results" in data:
        #     for movie_summary in data["results"]:
        #         if movie_summary and movie_summary.get("id"):
        #             _save_movie_details_if_not_exist(movie_summary.get("id"))

        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/genres", methods=["GET"])
def get_movie_genres_legacy():
    """Original endpoint for movie genres, kept for backwards compatibility"""
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=pt-BR"
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/movie/genres", methods=["GET"])
def get_movie_genres():
    """New endpoint for movie genres to match frontend expectation"""
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=pt-BR"
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/discover/movie", methods=["GET"])
def discover_movies():
    """Endpoint to discover movies by genre, matching the endpoint called from the frontend"""
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    
    # Get parameters from request
    genre_id = request.args.get("with_genres")
    page = request.args.get("page", 1)
    
    if not genre_id:
        return jsonify({"error": "Genre ID (with_genres) is required"}), 400
    
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres={genre_id}&page={page}"
        )
        response.raise_for_status()
        data = response.json()
        
        # Removed call to _save_movie_details_if_not_exist
        # if data and "results" in data:
        #     for movie_summary in data["results"]:
        #         if movie_summary and movie_summary.get("id"):
        #             _save_movie_details_if_not_exist(movie_summary.get("id"))
        
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
