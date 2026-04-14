import google.generativeai as genai
import json
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

THERAPIST_PROMPT = """
You are MindEase, a warm and supportive AI mental health companion.

STRICT RULES:
1. NEVER ask more than ONE question per response
2. Always give a helpful response FIRST, then ask one question at the end
3. If the user says anything — even just "hi" or "okay" — respond warmly and helpfully
4. Keep responses to 3-4 sentences maximum
5. Do NOT repeatedly ask "can you tell me more" — give actual help
6. Give real advice, coping tips, or emotional validation in EVERY response
7. If user seems sad — validate + give one concrete coping tip
8. If user seems anxious — give a breathing or grounding technique immediately
9. If user seems happy — celebrate with them and encourage the positive feeling
10. Never be robotic, clinical, or ask multiple questions
11. If crisis detected — immediately give: iCall: 9152987821, AASRA: 9820466627

You are NOT a replacement for professional therapy. Mention this only once per conversation.
"""

def get_ai_response(conversation_history, user_message, user_profile=None):
    profile_context = ""

    if user_profile:
        try:
            hobbies = json.loads(user_profile.hobbies or "[]")
            triggers = json.loads(user_profile.stress_triggers or "[]")
            goals = json.loads(user_profile.goals or "[]")
            coping = json.loads(user_profile.coping_methods or "[]")

            profile_context = f"""
User's personal profile (use this to personalize your response):
- Age: {user_profile.age}, Gender: {user_profile.gender}
- Occupation: {user_profile.occupation}
- Hobbies: {', '.join(hobbies) or 'not specified'}
- Stress triggers: {', '.join(triggers) or 'not specified'}
- Preferred coping: {', '.join(coping) or 'not specified'}
- Goals: {', '.join(goals) or 'not specified'}
- Sleep: {user_profile.sleep_hours} hrs/night
- Previous therapy: {'Yes' if user_profile.previous_therapy else 'No'}

Always reference their hobbies and coping preferences when suggesting activities.
"""
        except Exception:
            profile_context = ""

    full_prompt = THERAPIST_PROMPT + "\n" + profile_context + "\n\nConversation history:\n"

    for msg in conversation_history[-8:]:
        role = "User" if msg["role"] == "user" else "MindEase"
        full_prompt += f"{role}: {msg['message']}\n"

    full_prompt += f"\nUser: {user_message}\nMindEase:"

    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(full_prompt)
        return response.text.strip()
    except Exception as e:
        return "I'm really glad you reached out. It sounds like you have a lot on your mind — that's completely okay. Sometimes just putting feelings into words is the first step. What would feel most helpful to talk about right now?"