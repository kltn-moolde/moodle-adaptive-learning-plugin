from flask import Flask
from config import Config
from database import mongo
from routes.course_routes import course_bp
from routes.learning_path_routes import learning_path_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    
    CORS(app)

    app.register_blueprint(course_bp, url_prefix="/api")
    app.register_blueprint(learning_path_bp, url_prefix="/api")


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)