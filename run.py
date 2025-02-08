# run.py
from app import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os
from dotenv import load_dotenv

load_dotenv()

env = os.environ.get("FLASK_ENV", "development")

if env == "production":
    config_class = ProductionConfig
elif env == "testing":
    config_class = TestingConfig
else:
    config_class = DevelopmentConfig

app = create_app(config_class)  # Pass the config class to create_app

if __name__ == '__main__':
    app.run(debug=(config_class == DevelopmentConfig)) # Set debug based on config