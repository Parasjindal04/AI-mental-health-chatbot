from mistralai.client import Mistral
import json
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

CRISIS_RESOURCES = {
    "iCall (India)": "9152987821",
    "AASRA": "9820466627",
    "Vandrevala Foundation": "1860-2662-345",
    "iCall WhatsApp": "9152987821"
}

def check_crisis(text):
    prompt = f"""
Analyze this message for mental health crisis indicators:
"{text}"

Return ONLY valid JSON with no extra text, no markdown, no backticks:
{{
    "crisis_level": "none or low or medium or high or critical",
    "indicators": ["indicator1", "indicator2"],
    "immediate_action_needed": false
}}
"""
    try:
        message = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        clean = message.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        if result.get("crisis_level") in ["high", "critical"]:
            result["resources"] = CRISIS_RESOURCES
        return result
    except Exception:
        return {
            "crisis_level": "none",
            "indicators": [],
            "immediate_action_needed": False
        }
