from flask import Blueprint

# Create a main blueprint for API v1
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api')

def register_blueprints(api_blueprint):
    """
    Register all blueprints with the main API blueprint.
    This function avoids circular imports by only importing the blueprints
    when this function is called (which happens after app creation).
    """
    from api.auth_routes import auth_bp
    from api.list_routes import lists_bp
    from api.watched_routes import watched_bp
    from api.tmdb_proxy_routes import tmdb_proxy_bp
    
    api_blueprint.register_blueprint(auth_bp)
    api_blueprint.register_blueprint(lists_bp)
    api_blueprint.register_blueprint(watched_bp)
    api_blueprint.register_blueprint(tmdb_proxy_bp)
    
    return api_blueprint

# Generic health check for the blueprint itself (optional)
@api_v1_bp.route('/health_bp')
def health_check_bp():
    return "API v1 Blueprint is healthy", 200
