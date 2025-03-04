from flask import Blueprint, request, render_template, flash, redirect, url_for, session, send_from_directory, current_app 
from flask_mail import Message
from app import mail, generate_verification_token, confirm_verification_token
from app.models import User
from app import db, bcrypt
from werkzeug.utils import secure_filename
import os, cv2, numpy as np


routes = Blueprint("routes", __name__)

def register_routes(app):
    app.register_blueprint(routes)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Function to check image blurriness
def is_blurry(image_path, threshold=5000):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()  # Compute Laplacian variance
    print(f"laplacian Variance:{laplacian_var}")
    return laplacian_var < threshold  # Return True if blurry

@routes.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed")  # Debugging
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        print(f"Received: {email}, {password}, {confirm_password}")  # Debugging

        # Validation
        if not email or not password or not confirm_password:
            flash("Please fill in all fields", "danger")
            return redirect(url_for('routes.register'))
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            print("Password mismatch error")  # Debugging
            return redirect(url_for('routes.register'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for('routes.register'))
       
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create new user object
        new_user = User(email=email, password=hashed_password, verified=False)
        db.session.add(new_user)
        db.session.commit()  # ✅ Commit before sending email

        try:
            # Generate verification token
            token = generate_verification_token(email)
            verification_link = url_for('routes.verify_email', token=token, _external=True)
            print(f"Verification Link: {verification_link}")  # Debugging

            # Send email
            msg = Message("Confirm Your Email", recipients=[email])
            msg.body = f"Click the link to verify your email: {verification_link}"
            mail.send(msg)
            print("Verification email sent successfully!")  # Debugging

            flash("A verification email has been sent. Please check your inbox.", "info")
            return redirect(url_for('routes.login'))
        
        except Exception as e:
            db.session.rollback()  # Rollback only if something fails
            print(f"Error sending email: {e}")  # Debugging
            flash("An error occurred while sending the verification email.", "danger")
            return redirect(url_for('routes.register'))
        
        finally:
            db.session.close()  

    return render_template('register.html')

@routes.route('/verify_email/<token>')
def verify_email(token):
    email = confirm_verification_token(token)
    if not email:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for('routes.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('routes.register'))

    if user.verified:
        flash("Account already verified!", "info")
    else:
        user.verified = True
        db.session.commit()
        flash("Email verified successfully! You can now log in.", "success")

    return redirect(url_for('routes.login'))




@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not registered!", "danger")
            return redirect(url_for('routes.login'))

        if not user.verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for('routes.login'))

        if bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('routes.upload'))
        else:
            flash("Invalid password!", "danger")

    return render_template("login.html")


@routes.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash("You must be logged in to access this page!", "danger")
        return redirect(url_for('routes.login'))
    
    if request.method == 'POST':
        file = request.files['file-upload']
        filename = secure_filename(file.filename)
        file_path = (os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        file.save(file_path)
         # ✅ Check for blurriness
        if is_blurry(file_path):
            os.remove(file_path)  # Delete blurry image
            flash("Image is too blurry! Please upload a clear image.", "warning")
            return redirect(url_for('routes.upload'))
        
        flash("File uploaded successfully!", "success")  # ✅ Success message
        return redirect(url_for('routes.upload'))
    return render_template("upload.html")


@routes.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@routes.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.login'))

@routes.route('/')
def home():
    return render_template('home.html')

