from app import app
from models import db, User, MoodEntry, Journal, Assessment
from datetime import datetime, timedelta
import bcrypt

with app.app_context():
    db.create_all()

    # Create dummy user
    password = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
    user = User(name="abc", email="abc@test.com", password=password)
    db.session.add(user)
    db.session.commit()

    # Add mood entries for last 7 days
    moods = [7, 5, 8, 4, 6, 9, 7]
    labels = ["Good", "Neutral", "Great", "Low", "Okay", "Very Good", "Good"]
    notes = [
        "Feeling productive today",
        "A bit tired",
        "Had a great study session",
        "Stressed about exams",
        "Doing okay",
        "Really happy today!",
        "Normal day"
    ]
    for i, (score, label, note) in enumerate(zip(moods, labels, notes)):
        entry = MoodEntry(
            user_id=user.id,
            mood_score=score,
            mood_label=label,
            note=note,
            date=datetime.utcnow() - timedelta(days=6 - i)
        )
        db.session.add(entry)

    # Add journal entries
    journals = [
        ("I feel overwhelmed with assignments. Too much to do and not enough time.", "anxious"),
        ("Had a good conversation with friends today. Feeling lighter.", "happy"),
        ("Couldn't sleep well. Mind is too active at night.", "fearful"),
    ]
    for content, emotion in journals:
        entry = Journal(
            user_id=user.id,
            content=content,
            detected_emotion=emotion,
            emotion_score=0.85,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(entry)

    # Add assessment
    assessment = Assessment(
        user_id=user.id,
        type="PHQ-9",
        score=8,
        severity="Mild",
        taken_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(assessment)
    db.session.commit()

    print("✅ Dummy user created!")
    print("Email: abc@test.com")
    print("Password: password123")
