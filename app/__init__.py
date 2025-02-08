from flask import Flask
from flask_jwt_extended import JWTManager
from .database import init_db
from .routes import bp as routes_bp
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):  # Default to DevelopmentConfig
    app = Flask(__name__)
    app.config.from_object(config_class)

    jwt = JWTManager(app)

    # Ensure the database initialization happens within the app context
    with app.app_context():
        init_db(app)

    app.register_blueprint(routes_bp)

    return app