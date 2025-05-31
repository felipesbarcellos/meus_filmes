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
    language = request.args.get("language", "pt-BR")
    try:
        url = f"{TMDB_BASE_URL}/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": language,
            "sort_by": "popularity.desc",
            "page": page,
            "include_adult": False,  # Boolean instead of string
            "certification_country": "BR",
            "certification.lte": "18"  # Filmes até 14 anos (sem conteúdo adulto)
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filtragem manual adicional como backup
        if "results" in data:
            filtered_results = []
            for movie in data["results"]:
                # Filtrar filmes que podem ser adultos baseado em gêneros e ratings
                if movie.get("adult", False) == False:
                    # Verificar se não tem gêneros adultos (geralmente não há gênero específico, mas podemos verificar rating)
                    if movie.get("vote_average", 0) > 0:  # Filmes com rating válido
                        filtered_results.append(movie)
            
            data["results"] = filtered_results
            data["total_results"] = len(filtered_results)
        
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@tmdb_proxy_bp.route("/movie/<int:tmdb_id>", methods=["GET"])
def get_movie_details(tmdb_id):
    TMDB_API_KEY = current_app.config.get("TMDB_API_KEY")
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB API key not configured"}), 500
    
    append_to_response = request.args.get("append_to_response")
    language = request.args.get("language")
    try:
        # Se language for diferente de pt-BR, busca direto da TMDB e retorna (não usa banco)
        if language and language != "pt-BR":
            url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language={language}"
            if append_to_response:
                url += f"&append_to_response={append_to_response}"
            tmdb_response = requests.get(url)
            if tmdb_response.status_code == 200:
                return jsonify(tmdb_response.json())
            else:
                return jsonify({"error": f"Could not fetch movie from TMDB: {tmdb_response.text}"}), 404

        # Caso padrão: usa banco local e só busca extras da TMDB se solicitado
        movie_object = _save_movie_details_if_not_exist(tmdb_id)
        if movie_object:
            movie_dict = {
                "id": movie_object.tmdb_id,
                "title": movie_object.title,
                "overview": movie_object.overview,
                "poster_path": movie_object.poster_path,
                "release_date": movie_object.release_date.isoformat() if movie_object.release_date else None,
                "vote_average": movie_object.rating,
                "genres": movie_object.genres,
                "runtime": getattr(movie_object, "runtime", None)
            }
            if append_to_response:
                url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response={append_to_response}"
                tmdb_response = requests.get(url)
                if tmdb_response.status_code == 200:
                    tmdb_data = tmdb_response.json()
                    if "runtime" in tmdb_data:
                        movie_dict["runtime"] = tmdb_data["runtime"]
                    for key in append_to_response.split(","):
                        if key in tmdb_data:
                            movie_dict[key] = tmdb_data[key]
                else:
                    current_app.logger.warning(f"Could not fetch append_to_response for TMDB ID {tmdb_id}: {tmdb_response.text}")
            return jsonify(movie_dict)
        else:
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
    language = request.args.get("language", "pt-BR")
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "language": language,
            "query": query,
            "page": page,
            "include_adult": False
        }
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filtragem manual adicional como backup
        if "results" in data:
            filtered_results = []
            for movie in data["results"]:
                if movie.get("adult", False) == False:
                    filtered_results.append(movie)
            
            data["results"] = filtered_results
            data["total_results"] = len(filtered_results)
        
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
    language = request.args.get("language", "pt-BR")
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "language": language,
            "page": page,
            "include_adult": False
        }
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}/recommendations", params=params
        )
        response.raise_for_status()
        data = response.json()
        
        # Filtragem manual adicional como backup
        if "results" in data:
            filtered_results = []
            for movie in data["results"]:
                if movie.get("adult", False) == False:
                    filtered_results.append(movie)
            
            data["results"] = filtered_results
            data["total_results"] = len(filtered_results)
        
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
    language = request.args.get("language", "pt-BR")
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language={language}"
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
    language = request.args.get("language", "pt-BR")
    
    if not genre_id:
        return jsonify({"error": "Genre ID (with_genres) is required"}), 400
    
    try:
        params = {
            "api_key": TMDB_API_KEY,
            "language": language,
            "with_genres": genre_id,
            "page": page,
            "include_adult": False
        }
        response = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filtragem manual adicional como backup
        if "results" in data:
            filtered_results = []
            for movie in data["results"]:
                if movie.get("adult", False) == False:
                    filtered_results.append(movie)
            
            data["results"] = filtered_results
            data["total_results"] = len(filtered_results)
        
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
