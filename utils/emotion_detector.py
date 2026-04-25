from mistralai.client import Mistral
import json
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

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
        message = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        clean = message.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "primary_emotion": "neutral",
            "intensity": "low",
            "crisis_detected": False,
            "confidence": 0.5,
            "brief_insight": "Thank you for sharing your thoughts."
        }
