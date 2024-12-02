from flask import Flask
from flask_cors import CORS
from config import Config
from .routes.simple_routes import simple
from .routes.network_routes import network
from .routes.dashboard import dashboard

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(simple)
    app.register_blueprint(network)
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    
    return app
