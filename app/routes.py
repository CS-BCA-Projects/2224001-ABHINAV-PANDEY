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

<<<<<<< HEAD
# Function to check image blurriness
def is_blurry(image_path, threshold=100):
    """Check if the detected face(s) in the image are blurry."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not read image: {image_path}")
        return True  # Treat unreadable images as blurry

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print("No face detected in image.")
        return True  # No face detected means we reject the image

    for (x, y, w, h) in faces:
        face_region = gray[y:y+h, x:x+w]  # Crop the detected face
        laplacian_var = cv2.Laplacian(face_region, cv2.CV_64F).var()

        print(f"Laplacian Variance (Face): {laplacian_var}")  # Debugging
        if laplacian_var < threshold:
            return True  # Blurry face detected

    return False  # At least one face is clear
=======
def check_image_quality(image):
    """
    Checks the quality of an image based on sharpness, brightness, and contrast.

    Returns:
    - status (str): "Good" if quality is okay, otherwise "Bad"
    - message (str): Description of the issue
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 1️⃣ **Check Sharpness (Blurriness)**
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(laplacian_var)
    if laplacian_var < 1700:  
        return False, f"Image is too blurry! (Sharpness Score: {laplacian_var:.2f})"

    # 2️⃣ **Check Brightness**
    brightness = np.mean(gray)
    if brightness < 40:
        return False, f"Image is too dark! (Brightness: {brightness:.2f})"
    elif brightness > 200:
        return False, f"Image is overexposed! (Brightness: {brightness:.2f})"

    # 3️⃣ **Check Image Resolution**
    h, w = image.shape[:2]
    if h < 512 or w < 512:
        image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
        return True, "Good"

    return True, "Good"

def detect_faces_dnn(image_path, confidence_threshold=0.2, min_faces=1):
    """
    Detects faces in an image using OpenCV's DNN face detector.

    Parameters:
    - image_path (str): Path to the input image.
    - confidence_threshold (float): Minimum confidence for detecting a face.
    - min_faces (int): Minimum number of faces required for successful detection.

    Returns:
    - detected_image (numpy.ndarray): Image with detected faces drawn.
    - face_boxes (list): List of detected face bounding boxes [(x, y, x1, y1)].
    - status (str): "Success" if all faces detected properly, "Failed" otherwise.
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found: {image_path}")
    
    # **Check Image Quality First**
    quality_status, message = check_image_quality(image)
    if quality_status == False:
        return f"⚠️ Image Rejected: {message}"

    print("✅ Image Quality Check Passed. Proceeding with detection...")
    # Load the pre-trained DNN model
    prototxt_path = os.path.join(current_app.root_path, "models/deploy.prototxt")
    model_path = os.path.join(current_app.root_path, "models/res10_300x300_ssd_iter_140000.caffemodel")

    if not os.path.exists(prototxt_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Model files not found! Check 'models' directory.")

    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    

    (h, w) = image.shape[:2]

    # Try different scales
    for scale in [400, 600, 800]:  # Process at different sizes
        resized_image = cv2.resize(image, (scale, scale))
        blob = cv2.dnn.blobFromImage(resized_image, scalefactor=1.0, size=(scale, scale), 
                                     mean=(104.0, 177.0, 123.0), swapRB=False, crop=False)
        net.setInput(blob)
        detections = net.forward()

        face_boxes = []
        detected_faces = 0

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x, y, x1, y1) = box.astype("int")
                face_boxes.append((x, y, x1, y1))
                detected_faces += 1

                # Draw rectangle
                cv2.rectangle(image, (x, y), (x1, y1), (0, 255, 0), 2)
                text = f"{confidence*100:.2f}%"
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, (0, 255, 0), 2)

        if detected_faces >= min_faces:
            print(f"✅ {detected_faces} faces detected. Accepting image.")
            return image, face_boxes, "Success"

    print(f"⚠️ Faces detected: {detected_faces}. Rejecting image!")
    return None, [], "Failed"
>>>>>>> working

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
<<<<<<< HEAD
       

        # ✅ Check if the detected face is blurry (ignore background)
        if is_blurry(file_path):
            os.remove(file_path)  # Delete blurry image
            flash("Upload failed: The face in the image is blurry! Please upload a clear image.", "danger")
            return redirect(request.url)
=======
        
        # ✅ Read image properly before checking quality
        image = cv2.imread(file_path)
        if image is None:
            flash("Invalid image file!", "danger")
            return redirect(url_for('routes.upload'))
>>>>>>> working
        
        # ✅ Check image quality
        quality_status, message = check_image_quality(image)
        if quality_status == False:
            os.remove(file_path)  # Delete the image
            flash(f"Image quality is too low: {message}", "warning")
            return redirect(url_for('routes.upload'))

        # ✅ Detect Faces
        image, face_boxes, status = detect_faces_dnn(file_path)
        if status == "Failed" or len(face_boxes) == 0:
            os.remove(file_path)  # Delete the image
            flash("No clear human faces detected! Please upload a better image.", "warning")
            return redirect(url_for('routes.upload'))
        

        # ✅ Show success message
        flash(f"Image uploaded successfully! {len(face_boxes)} clear face(s) detected.", "success")
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

