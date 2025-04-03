from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_migrate import Migrate
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)  # Load configurations

    # Initialize Flask extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Import and register routes
    from app.routes import register_routes
    register_routes(app)

    return app

def generate_verification_token(email):
    """Generate a time-sensitive verification token for email confirmation."""
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt="email-confirmation")

def confirm_verification_token(token, expiration=3600):
    """Verify and decode the email confirmation token."""
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="email-confirmation", max_age=expiration)
        return email
    except SignatureExpired:
        return None  # Token expired
    except BadSignature:
        return None  # Invalid token
