from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from extensions import mail
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import sys

# Add parent directory to Python path to allow imports from api-backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extensions import db
from models import User, List

# Import mock mail for development
try:
    from mock_mail import MockMail
except ImportError:
    MockMail = None

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
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    recovery_link = f"{current_app.config['FRONTEND_URL']}/recovery/{token}"
    recovery_message = Message(
        subject="Password Recovery",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email],
        body=f"Click the link to recover your password: {recovery_link}"
    )
    
    try:
        current_app.logger.info(f"Sending email to: {email}")
        current_app.logger.info(f"Mail server: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
        current_app.logger.info(f"TLS: {current_app.config['MAIL_USE_TLS']}, SSL: {current_app.config['MAIL_USE_SSL']}")
        
        # Use mock mail for development if configured
        if os.environ.get('USE_MOCK_MAIL', 'False').lower() in ['true', '1', 'yes']:
            current_app.logger.info("Using mock mail service for development")
            if MockMail:
                mock_mail = MockMail()
                mock_mail.send(recovery_message)
                current_app.logger.info("Mock email sent successfully")
            else:
                current_app.logger.error("MockMail class not available")
        else:
            # Try to send email with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    mail.send(recovery_message)
                    current_app.logger.info(f"Email sent successfully on attempt {attempt + 1}")
                    break
                except Exception as retry_error:
                    current_app.logger.warning(f"Attempt {attempt + 1} failed: {str(retry_error)}")
                    if attempt == max_retries - 1:
                        raise retry_error
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                
    except Exception as e:
        current_app.logger.error(f"Failed to send recovery email: {str(e)}")
        # Still return success to avoid revealing user information
        
    current_app.logger.info(f"Password recovery requested for email: {email}")
    return jsonify({"msg": "If your email is registered, recovery instructions have been sent."}), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    if not data:
        current_app.logger.error("Reset password: No JSON data received")
        return jsonify({"msg": "Request body must be JSON"}), 400
    
    token = data.get("token")
    new_password = data.get("new_password")
    
    current_app.logger.info(f"Reset password request received. Token length: {len(token) if token else 0}")
    
    if not token or not new_password:
        current_app.logger.error(f"Reset password: Missing fields. Token: {'present' if token else 'missing'}, Password: {'present' if new_password else 'missing'}")
        return jsonify({"msg": "Missing token or new_password"}), 400
    
    try:
        # Decode and validate the JWT token
        current_app.logger.info("Attempting to decode JWT token")
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = payload.get('user_id')
        
        current_app.logger.info(f"Token decoded successfully. User ID: {user_id}")
        
        if not user_id:
            current_app.logger.error("Token decoded but no user_id found in payload")
            return jsonify({"msg": "Invalid token"}), 400
            
    except jwt.ExpiredSignatureError as e:
        current_app.logger.error(f"Token expired: {str(e)}")
        return jsonify({"msg": "Token has expired"}), 400
    except jwt.InvalidTokenError as e:
        current_app.logger.error(f"Invalid token: {str(e)}")
        return jsonify({"msg": "Invalid token"}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error decoding token: {str(e)}")
        return jsonify({"msg": "Invalid token"}), 400
    
    # Find the user
    current_app.logger.info(f"Looking for user with ID: {user_id}")
    user = User.query.get(user_id)
    if not user:
        current_app.logger.error(f"User not found with ID: {user_id}")
        return jsonify({"msg": "User not found"}), 404
    
    # Update the password
    try:
        current_app.logger.info(f"Updating password for user: {user.email}")
        hashed_pw = generate_password_hash(new_password)
        user.password = hashed_pw
        db.session.commit()
        
        current_app.logger.info(f"Password reset successfully for user ID: {user_id} ({user.email})")
        return jsonify({"msg": "Password reset successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating password: {str(e)}")
        db.session.rollback()
        return jsonify({"msg": "Error updating password"}), 500
