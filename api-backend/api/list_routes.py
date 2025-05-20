from flask import Blueprint, jsonify, request, current_app
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extensions import db
from models import List, MovieList
from utils import _save_movie_details_if_not_exist, require_user_match

lists_bp = Blueprint('lists', __name__, url_prefix='/lists')

@lists_bp.route("/", methods=["GET"])
@require_user_match
def get_user_lists(auth_user_id): # auth_user_id is injected by the decorator
    lists = List.query.filter_by(user_id=auth_user_id).all()
    result = [{"id": l.id, "name": l.name, "is_main": l.is_main} for l in lists]
    return jsonify(result), 200

@lists_bp.route("/", methods=["POST"])
@require_user_match
def create_list(auth_user_id): # auth_user_id is injected by the decorator
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"msg": "Missing name"}), 400
    new_list = List(name=name, is_main=False, user_id=auth_user_id)
    db.session.add(new_list)
    db.session.commit()
    return jsonify({"id": new_list.id, "name": new_list.name, "is_main": new_list.is_main, "user_id": new_list.user_id}), 201

@lists_bp.route("/add_movie", methods=["POST"])
@require_user_match
def add_movie_to_list(auth_user_id): # auth_user_id is injected by the decorator
    data = request.get_json()
    list_id = data.get("list_id")
    tmdb_id = data.get("tmdb_id")

    if not list_id or not tmdb_id:
        return jsonify({"msg": "Missing list_id or tmdb_id"}), 400

    local_movie = _save_movie_details_if_not_exist(tmdb_id) # Uses imported util
    if not local_movie:
        return jsonify({"msg": f"Could not retrieve or save details for movie {tmdb_id}"}), 500

    lista = List.query.filter_by(id=list_id, user_id=auth_user_id).first()
    if not lista:
        return jsonify({"msg": "List not found or access denied"}), 404
    if MovieList.query.filter_by(list_id=list_id, tmdb_id=tmdb_id).first():
        return jsonify({"msg": "Movie already in list"}), 409
    
    movie_list_entry = MovieList(tmdb_id=tmdb_id, list_id=list_id)
    db.session.add(movie_list_entry)
    db.session.commit()
    return jsonify({"msg": "Movie added", "tmdb_id": tmdb_id}), 201

@lists_bp.route("/<list_id>", methods=["GET"])
@require_user_match
def get_list_details(auth_user_id, list_id):
    lista = List.query.filter_by(id=list_id, user_id=auth_user_id).first()
    if not lista:
        return jsonify({"msg": "List not found or access denied"}), 404
    movie_entries = MovieList.query.filter_by(list_id=lista.id).all()
    movies_output = []
    for entry in movie_entries:
        movies_output.append({"tmdb_id": entry.tmdb_id})

    return jsonify({"id": lista.id, "name": lista.name, "is_main": lista.is_main, "user_id": lista.user_id, "movies": movies_output}), 200

@lists_bp.route("/<list_id>", methods=["DELETE"])
@require_user_match
def delete_list(auth_user_id, list_id):
    lista = List.query.filter_by(id=list_id, user_id=auth_user_id).first()
    if not lista:
        return jsonify({"msg": "List not found or access denied"}), 404
    if lista.is_main:
        return jsonify({"msg": "Cannot delete the main list."}), 403
        
    MovieList.query.filter_by(list_id=list_id).delete()
    db.session.delete(lista)
    db.session.commit()
    return jsonify({"msg": "List deleted"}), 200

@lists_bp.route("/<list_id>", methods=["PUT"])
@require_user_match
def update_list_name(auth_user_id, list_id):
    data = request.get_json()
    new_name = data.get("name")
    if not new_name:
        return jsonify({"msg": "Missing name"}), 400
    lista = List.query.filter_by(id=list_id, user_id=auth_user_id).first()
    if not lista:
        return jsonify({"msg": "List not found or access denied"}), 404
    # if lista.is_main:
    #     return jsonify({"msg": "Cannot rename the main list."}), 403

    lista.name = new_name
    db.session.commit()
    return jsonify({"id": lista.id, "name": lista.name, "is_main": lista.is_main, "user_id": lista.user_id}), 200

@lists_bp.route("/<list_id>/movies/<int:tmdb_id>", methods=["DELETE"])
@require_user_match
def remove_movie_from_list(auth_user_id, list_id, tmdb_id):
    lista = List.query.filter_by(id=list_id, user_id=auth_user_id).first()
    if not lista:
        return jsonify({"msg": "List not found or access denied"}), 404

    movie_list_entry = MovieList.query.filter_by(list_id=list_id, tmdb_id=tmdb_id).first()
    if not movie_list_entry:
        return jsonify({"msg": "Movie not found in this list"}), 404

    db.session.delete(movie_list_entry)
    db.session.commit()
    return jsonify({"msg": "Movie removed from list"}), 200

@lists_bp.route("/public/<list_id>", methods=["GET"])
def get_public_list_details(list_id):
    lista = List.query.filter_by(id=list_id).first()
    if not lista:
        return jsonify({"msg": "List not found"}), 404
    movie_entries = MovieList.query.filter_by(list_id=lista.id).all()
    movies_output = []
    for entry in movie_entries:
        movies_output.append({"tmdb_id": entry.tmdb_id})

    return jsonify({
        "id": lista.id,
        "name": lista.name,
        "is_main": lista.is_main,
        "user_id": lista.user_id,
        "movies": movies_output
    }), 200
