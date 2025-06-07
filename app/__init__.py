from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from app.services.db_service import DatabaseService

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure app
    app.config.from_object('app.config.Config')

    # Initialize database service
    db_service = DatabaseService(
        postgres_config=app.config['POSTGRES_CONFIG'],
        lance_db_path=app.config['LANCE_DB_PATH']
    )
    app.config['DB_SERVICE'] = db_service

    # Register blueprints
    from app.routes.stories import stories_bp
    from app.routes.testcases import testcases_bp

    app.register_blueprint(stories_bp, url_prefix='/api/stories')
    app.register_blueprint(testcases_bp, url_prefix='/api/testcases')

    return app 