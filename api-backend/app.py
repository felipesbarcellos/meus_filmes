import os
from flask import Flask, jsonify, abort
from flask_swagger_ui import get_swaggerui_blueprint
import yaml

# Import extensions and Blueprints - using absolute imports from current directory
from extensions import db, cors, mail

def create_app(config_name=None):
    app = Flask(__name__)

    # Configuration
    # Use SQLite for development if DATABASE_URL is not set or MySQL connection fails
    default_db_url = os.environ.get('DATABASE_URL')
    if not default_db_url:
        default_db_url = 'sqlite:///instance/meus_filmes.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = default_db_url
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['TMDB_API_KEY'] = os.environ.get("TMDB_API_KEY")
    app.config['TMDB_BASE_URL'] = os.environ.get("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 'yes']
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    app.config['MAIL_TIMEOUT'] = int(os.environ.get('MAIL_TIMEOUT', 30))
    app.config['MAIL_MAX_EMAILS'] = int(os.environ.get('MAIL_MAX_EMAILS', 50))

    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

    if not app.config['TMDB_API_KEY']:
        print("ALERT: TMDB_API_KEY is not configured in .env file!")

    # Initialize extensions
    mail.init_app(app)
    
    db.init_app(app)
    origins = ["http://localhost:5173", os.environ.get('FRONTEND_URL')]
    origins = [o for o in origins if o is not None]  # Filter out None values
    cors.init_app(app, origins=origins, supports_credentials=True)

    # Swagger UI setup
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing slash)
    API_SPEC_ROUTE = '/api/spec.json'  # Route that will serve the OpenAPI spec as JSON

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_SPEC_ROUTE, # Tell Swagger UI where to fetch the spec
        config={
            'app_name': "MeusFilmes API"
        }
    )
    app.register_blueprint(swaggerui_blueprint) # SWAGGER_URL is the mount point

    # Register main API blueprint and register all sub-blueprints within it
    from api import api_v1_bp, register_blueprints
    app.register_blueprint(register_blueprints(api_v1_bp))

    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
            print("Continuing without database initialization...")

    # Serve openapi.yaml content as JSON from a dedicated route
    @app.route(API_SPEC_ROUTE)
    def serve_openapi_spec():
        try:
            # Try to use prance to resolve $ref references
            try:
                from prance import ResolvingParser
                spec_path = os.path.join(app.root_path, 'openapi.yaml')
                parser = ResolvingParser(spec_path)
                return jsonify(parser.specification)
            except ImportError:
                # Fallback to simple YAML loading if prance is not available
                app.logger.warning("prance not available, serving OpenAPI spec without $ref resolution")
                spec_path = os.path.join(app.root_path, 'openapi.yaml')
                with open(spec_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                return jsonify(content)
        except FileNotFoundError:
            app.logger.error(f"OpenAPI specification file not found at {spec_path}")
            abort(404, description="OpenAPI specification file not found.")
        except yaml.YAMLError as e:
            app.logger.error(f"Error parsing OpenAPI specification: {e}")
            abort(500, description="Could not parse OpenAPI specification.")
        except Exception as e:
            app.logger.error(f"Error serving OpenAPI spec: {e}")
            abort(500, description="Could not load or parse OpenAPI specification.")
    return app
# Entry point for running the app with 'flask run' or a WSGI server
# The 'app' instance is created by Flask CLI by calling create_app()
# For development with 'python app.py':
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
