from mistralai.client import Mistral
import json
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

def generate_weekly_report(mood_data, journal_emotions, avg_score):
    mood_summary = ", ".join([f"{m['label']}({m['score']})" for m in mood_data])
    emotions = ", ".join(journal_emotions) if journal_emotions else "not recorded"

    prompt = f"""
A user's mental wellness data for the past 7 days:
Average mood score: {avg_score}/10
Mood entries: {mood_summary}
Journal emotions detected: {emotions}

Generate a warm, personalized weekly wellness report.
Return ONLY valid JSON with no extra text, no markdown, no backticks:
{{
    "overall_assessment": "2-3 sentence summary of their week",
    "highlights": ["positive observation 1", "positive observation 2"],
    "areas_to_watch": ["concern 1 if any"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "motivational_message": "A warm closing message for the week ahead"
}}
"""
    try:
        message = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        clean = message.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "overall_assessment": "You've been tracking your mental health this week — that alone shows great self-awareness.",
            "highlights": ["You showed up for yourself by logging your mood", "You took time to reflect on your feelings"],
            "areas_to_watch": [],
            "recommendations": ["Continue your daily mood check-ins", "Try a 5-minute breathing exercise each morning", "Journal when you feel overwhelmed"],
            "motivational_message": "Every day you check in with yourself is a step toward better mental wellness. Keep going."
        }
