from flask import Flask
from flask_cors import CORS
from config import Config
from .routes.simple_routes import simple
from .routes.network_routes import network
from .routes.dashboard import dashboard
from .routes.packet_routes import packet
from .websockets.packet_socket import sock

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    
    # Initialize WebSocket
    sock.init_app(app)
    
    # Initialize background tasks
    from .services.background_tasks import task_manager
    task_manager.start()
    
    # Register blueprints
    app.register_blueprint(simple)
    app.register_blueprint(network)
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(packet, url_prefix='/api')
    
    return app
