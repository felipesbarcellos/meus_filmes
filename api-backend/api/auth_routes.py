from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import sys

# Add parent directory to Python path to allow imports from api-backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extensions import db
from models import User, List

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Request body must be JSON"}), 400
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"msg": "Missing fields: name, email, and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 409
    
    hashed_pw = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    main_list = List(name="Quero ver", is_main=True, user_id=user.id)
    db.session.add(main_list)
    watched_list = List(name="Assistidos", is_main=True, user_id=user.id)
    db.session.add(watched_list)
    favourites = List(name="Favoritos", is_main=True, user_id=user.id)
    db.session.add(favourites)
    db.session.commit()

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Request body must be JSON"}), 400
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing fields: email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401
        
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }), 200

@auth_bp.route("/recovery", methods=["POST"])
def recovery():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Request body must be JSON"}), 400
    email = data.get("email")
    if not email:
        return jsonify({"msg": "Missing email"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Email not found"}), 404 
    
    current_app.logger.info(f"Password recovery requested for email: {email}")
    return jsonify({"msg": "If your email is registered, recovery instructions have been sent."}), 200
