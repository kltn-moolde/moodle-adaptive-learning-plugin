#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Service Application
=============================
Main Flask application for generating and managing quiz questions
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import mongo
from utils.logger import setup_logger
from utils.exceptions import QuestionServiceError
import sys

# Setup logger
logger = setup_logger('app', level='INFO')


def create_app():
    """Create and configure Flask application"""
    logger.info("="*70)
    logger.info("QUESTION SERVICE - Starting Application")
    logger.info("="*70)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Log configuration
    logger.info("Configuration loaded:")
    logger.info(f"  Config.MONGO_URI: {Config.MONGO_URI[:50]}...")
    logger.info(f"  app.config['MONGO_URI']: {app.config.get('MONGO_URI', 'NOT SET')[:50]}...")
    
    # Initialize MongoDB
    try:
        mongo.init_app(app)
        logger.info("✓ MongoDB initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize MongoDB: {str(e)}")
        sys.exit(1)
    
    # Enable CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    logger.info("✓ CORS enabled")
    
    # Import routes inside function to avoid circular import
    from routes.question_routes import question_bp
    from routes.ai_routes import ai_bp
    
    # Register blueprints
    app.register_blueprint(question_bp, url_prefix='/api/questions')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    logger.info("✓ Blueprints registered")
    
    # Global error handlers
    @app.errorhandler(QuestionServiceError)
    def handle_service_error(error):
        logger.error(f"Service error: {str(error)}")
        return jsonify({
            'error': str(error),
            'type': error.__class__.__name__
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoints
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'question-service',
            'version': '1.0.0'
        }), 200
    
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        """API health check endpoint for Docker healthcheck"""
        try:
            # Check MongoDB connection
            mongo.db.command('ping')
            return jsonify({
                'status': 'healthy',
                'service': 'question-service',
                'version': '1.0.0',
                'mongodb': 'connected'
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'question-service',
                'error': str(e)
            }), 503
    
    logger.info("="*70)
    logger.info("QUESTION SERVICE - Started Successfully")
    logger.info("="*70)
    
    return app


# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    # For development only - use Gunicorn for production
    app.run(host='0.0.0.0', port=5003, debug=True)
