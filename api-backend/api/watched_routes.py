from flask import Blueprint, jsonify, request, current_app
import datetime
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extensions import db
from models import List, Watched, MovieList
from utils import _save_movie_details_if_not_exist, _get_tmdb_movie_details_internal, require_user_match

watched_bp = Blueprint('watched', __name__, url_prefix='/movie/watched')

@watched_bp.route("/", methods=["POST"])
@require_user_match
def add_watched_movie(auth_user_id):
    data = request.get_json()
    tmdb_id = data.get("tmdb_id")
    watched_at_str = data.get("watched_at")

    if not tmdb_id or not watched_at_str:
        return jsonify({"msg": "Missing tmdb_id or watched_at (YYYY-MM-DD)"}), 400

    local_movie = _save_movie_details_if_not_exist(tmdb_id)
    if not local_movie:
        return jsonify({"msg": f"Could not retrieve or save details for movie {tmdb_id}"}), 500

    try:
        watched_date = datetime.datetime.strptime(watched_at_str, "%Y-%m-%d").date()
        watched_at_dt = datetime.datetime.combine(watched_date, datetime.time.min, tzinfo=datetime.timezone.utc)
    except ValueError:
        return jsonify({"msg": "Invalid date format for watched_at. Use YYYY-MM-DD."}), 400

    existing_watched = Watched.query.filter_by(user_id=auth_user_id, tmdb_id=tmdb_id).first()
    if existing_watched:
        existing_watched.watched_at = watched_at_dt
        db.session.commit()
        watched_obj = existing_watched
        msg = "Data de assistido atualizada com sucesso"
    else:
        watched_obj = Watched(user_id=auth_user_id, tmdb_id=tmdb_id, watched_at=watched_at_dt)
        db.session.add(watched_obj)
        db.session.commit()
        msg = "Filme adicionado com sucesso"

    # Adiciona também na lista "Assistidos"
    assistidos_list = List.query.filter_by(user_id=auth_user_id, is_main=True, name="Assistidos").first()
    if assistidos_list:
        exists = MovieList.query.filter_by(list_id=assistidos_list.id, tmdb_id=tmdb_id).first()
        if not exists:
            db.session.add(MovieList(list_id=assistidos_list.id, tmdb_id=tmdb_id))
            db.session.commit()

    return jsonify({
        "id": watched_obj.id,
        "user_id": watched_obj.user_id,
        "tmdb_id": watched_obj.tmdb_id,
        "watched_at": watched_obj.watched_at.date().isoformat(),
        "msg": msg
    }), 200 if existing_watched else 201

@watched_bp.route("/", methods=["GET"])
@require_user_match
def get_watched_movies(auth_user_id):
    watched_records = Watched.query.filter_by(user_id=auth_user_id).order_by(Watched.watched_at.desc()).all()
    
    # Return a simpler list of watched movies: tmdb_id and watched_at
    # This avoids making N calls to TMDB for movie details.
    simple_watched_movies = []
    for w in watched_records:
        simple_watched_movies.append({
            "tmdb_id": w.tmdb_id,
            "watched_at": w.watched_at.date().isoformat() 
        })
            
    return jsonify({"user_id": auth_user_id, "watched": simple_watched_movies}), 200

@watched_bp.route("/<int:tmdb_id>", methods=["DELETE"])
@require_user_match
def delete_watched_movie(auth_user_id, tmdb_id):
    watched_record = Watched.query.filter_by(user_id=auth_user_id, tmdb_id=tmdb_id).first()
    if not watched_record:
        return jsonify({"msg": "Watched record not found"}), 404
    db.session.delete(watched_record)
    db.session.commit()
    return jsonify({"msg": "Watched record deleted"}), 200

@watched_bp.route("/count", methods=["GET"])
@require_user_match
def get_watched_count(auth_user_id):
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    query = Watched.query.filter_by(user_id=auth_user_id)
    
    try:
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            query = query.filter(Watched.watched_at >= datetime.datetime.combine(start_date, datetime.time.min, tzinfo=datetime.timezone.utc))
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            query = query.filter(Watched.watched_at <= datetime.datetime.combine(end_date, datetime.time.max, tzinfo=datetime.timezone.utc))
    except ValueError:
        return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD."}), 400
        
    count = query.count()
    return jsonify({"user_id": auth_user_id, "count": count}), 200
