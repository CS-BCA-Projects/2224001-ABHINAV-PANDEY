from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<User {self.email}>"


#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Corrected reference
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Corrected reference
#     name = db.Column(db.String(100))

class GenderRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corrected reference
    processed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
