"""
SQLtoRA Flask Application - Main entry point.
Educational tool for visualizing SQL query compilation pipeline.
"""

from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.api.routes import api_bp
from backend.core.utils import setup_logger

# Setup logger
logger = setup_logger(__name__)


def create_app():
    """
    Application factory for creating Flask app.
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'message': 'SQLtoRA API Server',
            'version': '1.0.0',
            'endpoints': {
                'process': '/api/process',
                'schema': '/api/schema',
                'health': '/api/health'
            }
        }
    
    logger.info("SQLtoRA application created successfully")
    return app


if __name__ == '__main__':
    app = create_app()
    
    logger.info(f"Starting SQLtoRA server on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )