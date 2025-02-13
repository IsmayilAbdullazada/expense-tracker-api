from flask import Flask
from flask_jwt_extended import JWTManager
from .database import init_db
from .routes import bp as routes_bp
from config import DevelopmentConfig, TestingConfig, ProductionConfig
import os

def create_app(config_class=None):
    app = Flask(__name__)

    # If no config provided, use environment variable
    if config_class is None:
        env = os.environ.get("FLASK_ENV", "development")
        if env == "production":
            config_class = ProductionConfig
        elif env == "testing":
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig
    
    app.config.from_object(config_class)

    jwt = JWTManager(app)

    with app.app_context():
        init_db(app)

    app.register_blueprint(routes_bp)

    return app