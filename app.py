from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, MoodEntry, Journal, Assessment, ChatMessage, UserProfile, Feedback, HealthRecord
from utils.emotion_detector import detect_emotion
from utils.coping_strategies import get_coping_strategies
from utils.ai_chat import get_ai_response
from utils.crisis_detector import check_crisis
from utils.report_generator import generate_weekly_report
from config import Config
from datetime import datetime, timedelta
import bcrypt
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself or that you are a failure",
    "Trouble concentrating on things such as reading or watching television",
    "Moving or speaking so slowly that other people could have noticed",
    "Thoughts that you would be better off dead or of hurting yourself"
]

MOOD_LABELS = {
    1: "Terrible", 2: "Very Sad", 3: "Sad", 4: "Low",
    5: "Neutral", 6: "Okay", 7: "Good", 8: "Great",
    9: "Very Good", 10: "Excellent"
}

MOOD_EMOJIS = {
    1: "😢", 2: "😞", 3: "😔", 4: "😕",
    5: "😐", 6: "🙂", 7: "😊", 8: "😄",
    9: "😁", 10: "🤩"
}

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if User.query.filter_by(email=email).first():
            return render_template("auth/register.html", error="Email already registered.")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("onboarding"))
    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            login_user(user)
            profile = UserProfile.query.filter_by(user_id=user.id).first()
            if not profile or not profile.completed:
                return redirect(url_for("onboarding"))
            return redirect(url_for("dashboard"))
        return render_template("auth/login.html", error="Invalid email or password.")
    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    recent_moods = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).limit(7).all()
    last_assessment = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.taken_at.desc()).first()
    today_mood = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.date >= datetime.utcnow().date()
    ).first()
    streak = 0
    for i in range(30):
        day = datetime.utcnow().date() - timedelta(days=i)
        entry = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.date >= day,
            MoodEntry.date < day + timedelta(days=1)
        ).first()
        if entry:
            streak += 1
        else:
            break
    return render_template("dashboard.html", moods=recent_moods, assessment=last_assessment,
                           today_mood=today_mood, streak=streak, mood_emojis=MOOD_EMOJIS)


@app.route("/mood/log", methods=["POST"])
@login_required
def log_mood():
    score = int(request.form.get("score", 5))
    note = request.form.get("note", "")
    entry = MoodEntry(user_id=current_user.id, mood_score=score, mood_label=MOOD_LABELS.get(score, "Neutral"), note=note)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"success": True, "label": MOOD_LABELS.get(score), "emoji": MOOD_EMOJIS.get(score)})


@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    if request.method == "POST":
        content = request.json.get("content", "")
        if not content.strip():
            return jsonify({"error": "Journal content cannot be empty"}), 400
        emotion = detect_emotion(content)
        crisis = check_crisis(content)
        entry = Journal(user_id=current_user.id, content=content,
                        detected_emotion=emotion.get("primary_emotion", "neutral"),
                        emotion_score=emotion.get("confidence", 0.5))
        db.session.add(entry)
        db.session.commit()
        return jsonify({"success": True, "emotion": emotion, "crisis": crisis})
    journals = Journal.query.filter_by(user_id=current_user.id).order_by(Journal.created_at.desc()).limit(10).all()
    return render_template("journal.html", journals=journals)


@app.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    if request.method == "POST":
        answers = [int(request.form.get(f"q{i}", 0)) for i in range(9)]
        score = sum(answers)
        if score <= 4: severity = "Minimal"
        elif score <= 9: severity = "Mild"
        elif score <= 14: severity = "Moderate"
        elif score <= 19: severity = "Moderately Severe"
        else: severity = "Severe"
        record = Assessment(user_id=current_user.id, type="PHQ-9", score=score, severity=severity)
        db.session.add(record)
        db.session.commit()
        strategies = get_coping_strategies(score, severity, "PHQ-9")
        return render_template("result.html", score=score, severity=severity,
                               strategies=strategies, questions=PHQ9_QUESTIONS, answers=answers)
    return render_template("assessment.html", questions=PHQ9_QUESTIONS)


@app.route("/chat")
@login_required
def chat():
    history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).limit(30).all()
    return render_template("chat.html", history=history)


@app.route("/chat/send", methods=["POST"])
@login_required
def send_message():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).limit(20).all()
    history_list = [{"role": m.role, "message": m.message} for m in history]
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    crisis = check_crisis(user_message)
    ai_response = get_ai_response(history_list, user_message, profile)
    db.session.add(ChatMessage(user_id=current_user.id, role="user", message=user_message))
    db.session.add(ChatMessage(user_id=current_user.id, role="assistant", message=ai_response))
    db.session.commit()
    return jsonify({"response": ai_response, "crisis": crisis})


@app.route("/history")
@login_required
def history():
    moods = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.asc()).limit(30).all()
    chart_data = {
        "labels": [m.date.strftime("%b %d") for m in moods],
        "scores": [m.mood_score for m in moods],
        "mood_labels": [m.mood_label for m in moods]
    }
    return render_template("history.html", moods=moods, chart_data=chart_data)


@app.route("/report")
@login_required
def report():
    week_ago = datetime.utcnow() - timedelta(days=7)
    moods = MoodEntry.query.filter(MoodEntry.user_id == current_user.id, MoodEntry.date >= week_ago).all()
    journals = Journal.query.filter(Journal.user_id == current_user.id, Journal.created_at >= week_ago).all()
    if not moods:
        return render_template("report.html", report=None, avg_score=0)
    avg_score = round(sum(m.mood_score for m in moods) / len(moods), 1)
    mood_data = [{"label": m.mood_label, "score": m.mood_score} for m in moods]
    journal_emotions = [j.detected_emotion for j in journals if j.detected_emotion]
    weekly_report = generate_weekly_report(mood_data, journal_emotions, avg_score)
    return render_template("report.html", report=weekly_report, avg_score=avg_score, moods=moods)


@app.route("/breathing")
@login_required
def breathing():
    return render_template("breathing.html")


@app.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if profile and profile.completed:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        profile = UserProfile(
            user_id=current_user.id,
            age=request.form.get("age"),
            gender=request.form.get("gender"),
            occupation=request.form.get("occupation"),
            stress_triggers=json.dumps(request.form.getlist("stress_triggers")),
            coping_methods=json.dumps(request.form.getlist("coping_methods")),
            sleep_hours=request.form.get("sleep_hours"),
            exercise_frequency=request.form.get("exercise_frequency"),
            social_preference=request.form.get("social_preference"),
            hobbies=json.dumps(request.form.getlist("hobbies")),
            dislikes=json.dumps(request.form.getlist("dislikes")),
            existing_conditions=request.form.get("existing_conditions", ""),
            current_medications=request.form.get("current_medications", ""),
            previous_therapy=request.form.get("previous_therapy") == "yes",
            preferred_coping_style=request.form.get("preferred_coping_style"),
            goals=json.dumps(request.form.getlist("goals")),
            completed=True
        )
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("onboarding.html")


@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    if request.method == "POST":
        fb = Feedback(
            user_id=current_user.id,
            rating=int(request.form.get("rating", 5)),
            helpful_features=json.dumps(request.form.getlist("helpful_features")),
            improvements=request.form.get("improvements", ""),
            would_recommend=request.form.get("would_recommend") == "yes",
            overall_experience=request.form.get("overall_experience", "")
        )
        db.session.add(fb)
        db.session.commit()
        return render_template("feedback.html", submitted=True)
    return render_template("feedback.html", submitted=False)


@app.route("/records")
@login_required
def records():
    all_records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.date_of_visit.desc()).all()
    return render_template("records.html", records=all_records)


@app.route("/records/add", methods=["GET", "POST"])
@login_required
def add_record():
    if request.method == "POST":
        f = request.form
        date_str = f.get("date_of_visit")
        next_str = f.get("next_appointment")
        record = HealthRecord(
            user_id=current_user.id,
            record_type=f.get("record_type"),
            title=f.get("title"),
            description=f.get("description", ""),
            doctor_name=f.get("doctor_name", ""),
            clinic_hospital=f.get("clinic_hospital", ""),
            date_of_visit=datetime.strptime(date_str, "%Y-%m-%d") if date_str else None,
            next_appointment=datetime.strptime(next_str, "%Y-%m-%d") if next_str else None,
            file_note=f.get("file_note", "")
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("records"))
    return render_template("add_record.html")


@app.route("/records/delete/<int:id>")
@login_required
def delete_record(id):
    record = HealthRecord.query.get_or_404(id)
    if record.user_id == current_user.id:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for("records"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)