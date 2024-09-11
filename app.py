from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    from main_routes import main_routes
    from auth import auth

    app.register_blueprint(main_routes)
    app.register_blueprint(auth)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
