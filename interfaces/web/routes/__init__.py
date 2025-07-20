from flask import Flask, Blueprint
from interfaces.web.routes.user_routes import user_bp
from interfaces.web.routes.workspace_routes import workspace_bp
from interfaces.web.routes.rag_routes import rag_bp
from interfaces.web.routes.simple_rag_routes import simple_rag_bp

bp = Blueprint('main', __name__)

def register_blueprints(app: Flask):
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(workspace_bp, url_prefix='/workspaces')
    app.register_blueprint(rag_bp, url_prefix='/rag')
    app.register_blueprint(simple_rag_bp, url_prefix='/api/rag')  # Simple API for frontend



@bp.route('/')
def home():
    return "Hello, World!"

# for page not found
@bp.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404
