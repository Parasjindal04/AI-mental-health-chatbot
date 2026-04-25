from mistralai.client import Mistral
import json
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

def get_coping_strategies(score, severity, assessment_type):
    prompt = f"""
A person completed a {assessment_type} mental health assessment.
Score: {score}
Severity: {severity}

Generate 5 personalized, practical coping strategies for this person.
Return ONLY valid JSON with no extra text, no markdown, no backticks:
{{
    "strategies": [
        {{
            "title": "Strategy name",
            "description": "2-3 sentence practical explanation of how to do this",
            "duration": "e.g. 5 minutes daily",
            "type": "breathing or mindfulness or physical or cognitive or social"
        }}
    ],
    "professional_help_recommended": false,
    "message": "A warm, encouraging 2-sentence message for this person"
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
            "strategies": [
                {
                    "title": "Deep Breathing",
                    "description": "Take 5 deep breaths, inhaling for 4 seconds, holding for 4, exhaling for 6. This activates your parasympathetic nervous system and reduces stress hormones.",
                    "duration": "5 minutes",
                    "type": "breathing"
                },
                {
                    "title": "Grounding Exercise",
                    "description": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. This brings you back to the present moment.",
                    "duration": "3 minutes",
                    "type": "mindfulness"
                }
            ],
            "professional_help_recommended": score > 14,
            "message": "You took a brave step by checking in with yourself today. Remember, every small step forward matters."
        }
