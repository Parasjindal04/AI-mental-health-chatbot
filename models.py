from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
[]
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    moods = db.relationship('MoodEntry', backref='user', lazy=True)
    journals = db.relationship('Journal', backref='user', lazy=True)
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    messages = db.relationship('ChatMessage', backref='user', lazy=True)


class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)
    mood_label = db.Column(db.String(50))
    note = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    detected_emotion = db.Column(db.String(50))
    emotion_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20))
    score = db.Column(db.Integer, nullable=False)
    severity = db.Column(db.String(50))
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    # Personal
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    occupation = db.Column(db.String(100))

    # Mental health background
    stress_triggers = db.Column(db.Text)        # JSON list
    coping_methods = db.Column(db.Text)         # JSON list
    sleep_hours = db.Column(db.Float)
    exercise_frequency = db.Column(db.String(50))
    social_preference = db.Column(db.String(50)) # introvert/extrovert/ambivert

    # Likes & dislikes
    hobbies = db.Column(db.Text)                # JSON list
    dislikes = db.Column(db.Text)               # JSON list

    # Medical
    existing_conditions = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    previous_therapy = db.Column(db.Boolean, default=False)

    # Preferences
    preferred_coping_style = db.Column(db.String(50))  # breathing/journaling/exercise/talking
    goals = db.Column(db.Text)                 # JSON list

    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer)              # 1-5 stars
    helpful_features = db.Column(db.Text)       # JSON list
    improvements = db.Column(db.Text)
    would_recommend = db.Column(db.Boolean)
    overall_experience = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    record_type = db.Column(db.String(50))      # counselling/therapy/blood_test/medication/hospital
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    doctor_name = db.Column(db.String(100))
    clinic_hospital = db.Column(db.String(100))
    date_of_visit = db.Column(db.DateTime)
    next_appointment = db.Column(db.DateTime)
    file_note = db.Column(db.Text)              # typed notes instead of file upload
    created_at = db.Column(db.DateTime, default=datetime.utcnow)