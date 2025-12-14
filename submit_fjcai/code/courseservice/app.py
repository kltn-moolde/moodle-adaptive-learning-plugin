#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Course Service Application
===========================
Main Flask application with structured logging and error handling
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import mongo
from utils.logger import setup_logger
from utils.exceptions import CourseServiceError
import sys

# Setup logger
logger = setup_logger('app', level='INFO')

# Import routes
from routes.course_routes import course_bp
from routes.learning_path_routes import learning_path_bp

logger.info("✓ Routes imported successfully")


def create_app():
    """Create and configure Flask application"""
    logger.info("="*70)
    logger.info("COURSE SERVICE - Starting Application")
    logger.info("="*70)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Log configuration
    logger.info("Configuration loaded:")
    logger.info(f"  MongoDB URI: {Config.MONGO_URI[:50]}...")
    logger.info(f"  Moodle API: {Config.MOODLE_API_BASE}")
    logger.info(f"  Moodle Host: {Config.ADDRESS_MOODLE}")
    
    # Initialize MongoDB
    try:
        mongo.init_app(app)
        logger.info("✓ MongoDB initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize MongoDB: {str(e)}")
        sys.exit(1)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logger.info("✓ CORS enabled")
    
    # Register blueprints
    app.register_blueprint(course_bp, url_prefix="/api")
    app.register_blueprint(learning_path_bp, url_prefix="/api")
    logger.info("✓ Blueprints registered:")
    logger.info("  - /api/courses")
    logger.info("  - /api/learning-paths")
    
    # Global error handlers
    @app.errorhandler(CourseServiceError)
    def handle_course_service_error(error):
        logger.error(f"CourseServiceError: {error.message}")
        return jsonify(error.to_dict()), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        logger.warning(f"404 Not Found: {error}")
        return jsonify({
            'error': 'NotFound',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"500 Internal Error: {error}")
        return jsonify({
            'error': 'InternalServerError',
            'message': 'An internal error occurred'
        }), 500
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'service': 'Course Service',
            'version': '2.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'courses': '/api/courses',
                'moodle': '/api/moodle/courses',
                'learning_paths': '/api/learning-paths'
            }
        })
    
    logger.info("="*70)
    logger.info("✅ Application created successfully")
    logger.info("="*70)
    
    return app


if __name__ == "__main__":
    try:
        app = create_app()
        logger.info("\n🚀 Starting Flask server on http://localhost:5001")
        logger.info("📝 Logs directory: ./logs/")
        logger.info("\nPress Ctrl+C to stop\n")
        
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True
        )
    except KeyboardInterrupt:
        logger.info("\n✓ Server stopped by user")
    except Exception as e:
        logger.critical(f"✗ Failed to start server: {str(e)}", exc_info=True)
        sys.exit(1)