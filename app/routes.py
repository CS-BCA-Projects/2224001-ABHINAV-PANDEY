from flask import render_template, redirect, url_for, request, flash, Blueprint
from app.models import User
from app import db, bcrypt  # Importing bcrypt from extensions

routes = Blueprint("routes", __name__)

def register_routes(app):
    app.register_blueprint(routes)

@routes.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed")  # Debugging
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        print(f"{email},{password},{confirm_password}")

        # validation
        if not email or not password or not confirm_password:
            flash("Please fill in all fields", "danger")
            return redirect(url_for('routes.register'))
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            print('error')
            return redirect(url_for('routes.register'))
       
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create new user object
        new_user = User(email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            print("User registered successfully!") 
            return redirect(url_for('routes.login'))  # Redirect to login page
            # return redirect(url_for('routes.register'))
        except:
            db.session.rollback()
            flash("Email already registered!", "danger")
            return redirect(url_for('routes.register'))
        finally:
            db.session.close()  

    return render_template('register.html')
@routes.route('/verify_email/<token>')
def verify_email(token):
    
    return redirect(url_for('routes.login'))

@routes.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
   
    return render_template('resend_verification.html')


@routes.route('/email-verification')
def email_verification():
    return render_template('email_verification.html')

@routes.route('/send_otp', methods=["POST"])
def send_otp():
    
        return redirect(url_for("routes.email_verification"))

@routes.route('/verify_otp', methods=["POST"])
def verify_otp():
  
    return redirect(url_for("routes.email_verification"))


@routes.route('/login', methods=['GET', 'POST'])
def login():
    
    return render_template('login.html')


@routes.route('/')
def home():
    return render_template('home.html')

