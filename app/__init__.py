from flask import Flask
from flask_bcrypt import Bcrypt
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer


db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
# Initialize Flask App
def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    with app.app_context():
        from app import routes, models 
        from app.routes import register_routes
        db.create_all()
        register_routes(app)
    return app

# Function to generate tokens
def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt="email-confirmation")



# Function to confirm tokens
def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="email-confirmation", max_age=expiration)
        return email
    except:
        return None
