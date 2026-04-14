import google.generativeai as genai
import json
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def detect_emotion(text):
    prompt = f"""
Analyze the emotional tone of this journal entry written by a person:

"{text}"

Return ONLY valid JSON with no extra text, no markdown, no backticks:
{{
    "primary_emotion": "happy or sad or anxious or angry or neutral or fearful or hopeful or overwhelmed",
    "intensity": "low or medium or high",
    "crisis_detected": false,
    "confidence": 0.85,
    "brief_insight": "One warm sentence about their emotional state"
}}
"""
    try:
        response = model.generate_content(prompt)
        clean = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "primary_emotion": "neutral",
            "intensity": "low",
            "crisis_detected": False,
            "confidence": 0.5,
            "brief_insight": "Thank you for sharing your thoughts."
        }
