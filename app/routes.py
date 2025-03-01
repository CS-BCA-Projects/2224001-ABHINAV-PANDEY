from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from app import mail, generate_verification_token, confirm_verification_token
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
            flash("Login successful!", "success")
            return redirect(url_for('routes.dashboard'))
        else:
            flash("Invalid password!", "danger")

    return render_template("login.html")


@routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = User.query.get(session['user_id'])  # Get logged-in user
    return render_template("dashboard.html", user=user)
@routes.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.login'))
@routes.route('/upload', methods=['GET', 'POST'])
def upload():
    # if request.method == 'POST':
    #     file = request.files['file']
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #     return redirect(url_for('routes.dashboard'))
    return render_template("upload.html")

@routes.route('/')
def home():
    return render_template('home.html')

