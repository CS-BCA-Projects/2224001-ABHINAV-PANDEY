from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from app.config import Config



# Initialize Flask App
app = Flask(__name__, template_folder="templates")


# Initialize Extensions
mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Class
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1])
    return None


# Import Routes
from app.routes import register_routes  # Import function from routes.py
register_routes(app)
