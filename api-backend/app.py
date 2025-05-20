import os
from flask import Flask, jsonify, abort
from flask_swagger_ui import get_swaggerui_blueprint
import yaml

# Import extensions and Blueprints - using absolute imports from current directory
from extensions import db, cors
from api import api_v1_bp

def create_app(config_name=None):
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost/meus_filmes')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['TMDB_API_KEY'] = os.environ.get("TMDB_API_KEY")
    app.config['TMDB_BASE_URL'] = os.environ.get("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.config['TMDB_API_KEY']:
        print("ALERT: TMDB_API_KEY is not configured in .env file!")

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, origins=["http://localhost:5173"])

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
        db.create_all()

    # Serve openapi.yaml content as JSON from a dedicated route
    @app.route(API_SPEC_ROUTE)
    def serve_openapi_spec():
        try:
            # app.root_path is the path to the directory where app.py is located (api-backend)
            spec_path = os.path.join(app.root_path, 'openapi.yaml')
            with open(spec_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) # Parse YAML
            return jsonify(content) # Serve as JSON
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
