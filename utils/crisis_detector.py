import google.generativeai as genai
import json
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

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
        response = model.generate_content(prompt)
        clean = response.text.strip().replace("```json", "").replace("```", "").strip()
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
