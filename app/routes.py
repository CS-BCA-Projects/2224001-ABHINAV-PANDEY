from flask import render_template, redirect, url_for, request, flash, Blueprint, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import mysql, bcrypt, User
from validate_email_address import validate_email
import dns.resolver
import smtplib
import random
from email.mime.text import MIMEText
from app.config import Config

# Create a Blueprint for routes
routes = Blueprint("routes", __name__)




def register_routes(app):
    def send_email(to_email, otp):
        subject = "Your OTP Code"
        body = f"Your OTP for verification is: {otp}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = Config.EMAIL_ADDRESS
        msg["To"] = to_email

        try:
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_ADDRESS, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    # Home Route
    @app.route('/')
    def home():
        return render_template('home.html')

    
    # Route for email input page
    @routes.route("/email-verification")
    def email_verification():
            return render_template("email_verification.html")

    # Route to send OTP
    # ✅ Modify `send_otp()` to store OTP in the database
    @routes.route("/send_otp", methods=["POST"])
    def send_otp():
        email = request.form.get("email")
        
        if not email:
            flash("Email is required", "danger")
            return redirect(url_for("email_verification"))

        otp = random.randint(100000, 999999)  # Generate OTP

        # ✅ Store OTP in the database instead of session
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET otp = %s WHERE email = %s", (otp, email))
        mysql.connection.commit()
        cur.close()

        if send_email(email, otp):
            flash("OTP sent to your email", "success")
            return redirect(url_for("verify_otp"))
        else:
            flash("Failed to send OTP. Try again.", "danger")
            return redirect(url_for("email_verification"))

    # ✅ Modify `verify_otp()` to check OTP from the database
    @routes.route("/verify_otp", methods=["POST"])
    def verify_otp():
        email = request.form.get("email")
        user_otp = request.form.get("otp")

        cur = mysql.connection.cursor()
        cur.execute("SELECT otp FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()

        if not result or str(result[0]) != str(user_otp):
            flash("Invalid OTP. Try again.", "danger")
            return redirect(url_for("verify_otp"))

        # ✅ Clear OTP from the database after successful verification
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET otp = NULL WHERE email = %s", (email,))
        mysql.connection.commit()
        cur.close()

        flash("Email verified successfully!", "success")
        return redirect(url_for("email_verification"))

    # ✅ Modify `register()` to validate OTP from the database
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form.get("email")
            otp = request.form.get("otp")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            # ✅ Fetch OTP from database
            cur = mysql.connection.cursor()
            cur.execute("SELECT otp FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            cur.close()

            if not result or str(result[0]) != str(otp):
                flash("Invalid OTP. Please verify your email first.", "danger")
                return redirect(url_for("register"))

            # ✅ Check Password Matching
            if password != confirm_password:
                flash("Passwords do not match. Please try again.", "danger")
                return redirect(url_for('register'))

            # ✅ Hash Password & Insert into DB
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET password = %s, otp = NULL WHERE email = %s", (hashed_password, email))
            mysql.connection.commit()
            cur.close()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

        return render_template('register.html')

    

    # Login Route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            cur = mysql.connection.cursor()
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.check_password_hash(user[1], password):
                login_user(User(user[0], email))
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials, please try again.", "danger")

        return render_template('login.html')


    # ✅ Modify `dashboard()` to use `current_user.email`
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return f"Welcome, {current_user.email}! <a href='/logout'>Logout</a>"

    # Logout Route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for('login'))
