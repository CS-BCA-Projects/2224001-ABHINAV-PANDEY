Gender Recognition System
📌 About the Project
The Gender Recognition System is a web application that can detect faces in a group image and classify each face as male or female using deep learning models.
It helps in automatically identifying the gender distribution in uploaded images, useful for analytics, surveys, and business insights.

This project is built using Flask for the backend, TensorFlow/Keras for the deep learning model, OpenCV for face detection, and MySQL for user management and result storage.

🚀 Features
User Authentication (Registration & Login)

Upload Group Images

Face Detection and Gender Prediction

Count and display the number of Males and Females

User Dashboard to track uploaded images

Metadata Storage in MySQL Database

Clean and Responsive Frontend

🛠️ Technologies Used
Python

Flask

TensorFlow / Keras

OpenCV

MySQL

HTML, CSS, JavaScript (Frontend)

Jinja2 (Templating Engine)

📥 How to Use This Repository
Follow the steps below to set up and run the project on your local machine:

1. Clone the repository
git clone https://github.com/your-username/gender-recognition-system.git
2. Navigate to the project directory
cd gender-recognition-system
3. (Optional but Recommended) Create a virtual environment
python -m venv venv
Activate the virtual environment:

On Windows:
venv\Scripts\activate
On macOS/Linux:
source venv/bin/activate
4. Install all required dependencies

pip install -r requirements.txt
5. Configure the MySQL Database
Create a MySQL database (e.g., gender_recognition_db).

Update your database credentials in the config.py file:


DB_HOST = 'localhost'
DB_USER = 'your_mysql_username'
DB_PASSWORD = 'your_mysql_password'
DB_NAME = 'gender_recognition_db'
Import the database schema (if provided) or manually create necessary tables.

6. Set up environment variables (Optional)
You can create a .env file in the root directory to securely store:

SECRET_KEY=your_secret_key
and load them in app.py or config.py.

7. Run the Flask Application
python app.py
or if you have a run.py:

🤝 Contributing
Fork the repository

Create a new branch (git checkout -b feature/yourFeature)

Commit your changes (git commit -m 'Add some feature')

Push to the branch (git push origin feature/yourFeature)

Open a Pull Request

All contributions, big or small, are welcome!

📬 Contact
For any questions, suggestions, or collaboration:
📧 Email: abhinavpandey56393@gmail.com

🙌 Thank you for checking out this project!
