from flask import Blueprint, jsonify, current_app
import requests

# Create a blueprint for health check routes
health_check_bp = Blueprint('health_check', __name__, url_prefix='/health')

@health_check_bp.route('', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify if the API is running and can access TMDB.
    """
    # Check if TMDB API key is configured
    tmdb_api_key = current_app.config.get("TMDB_API_KEY")
    if not tmdb_api_key:
        return jsonify({"status": "error", "message": "TMDB_API_KEY is not configured"}), 500
    tmdb_base_url = current_app.config.get("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    try:
        # Make a test request to TMDB
        response = requests.get(f"{tmdb_base_url}/movie/popular?api_key={tmdb_api_key}&language=en-US")
        response.raise_for_status()  # Raise an error for bad responses
        return jsonify({"status": "ok", "message": "API is healthy", "tmdb_reachable": True}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"TMDB API is not reachable: {str(e)}"}), 503