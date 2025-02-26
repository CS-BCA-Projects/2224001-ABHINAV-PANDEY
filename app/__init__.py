from flask import Flask
from flask_bcrypt import Bcrypt
from app.config import Config
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()
# Initialize Flask App
def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    with app.app_context():
        from app import routes, models 
        from app.routes import register_routes
        register_routes(app)
    return app





