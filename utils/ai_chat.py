from mistralai.client import Mistral
import json
import os
import sys
import time
from config import MISTRAL_API_KEY

if not MISTRAL_API_KEY:
    print("ERROR: MISTRAL_API_KEY not found in environment variables!", file=sys.stderr)
    print("Please create a .env file with MISTRAL_API_KEY set to your Mistral API key", file=sys.stderr)
    client = None
else:
    try:
        client = Mistral(api_key=MISTRAL_API_KEY)
    except Exception as e:
        print(f"ERROR configuring Mistral API: {e}", file=sys.stderr)
        client = None

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
    if client is None:
        return "⚠️ I'm temporarily unavailable due to a configuration issue. Please check that your MISTRAL_API_KEY environment variable is properly set in the .env file."

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
        except Exception as e:
            print(f"Warning: Could not parse user profile: {e}", file=sys.stderr)
            profile_context = ""

    # Build messages for Mistral API
    messages = [
        {"role": "system", "content": THERAPIST_PROMPT + "\n" + profile_context}
    ]

    # Add conversation history
    for msg in conversation_history[-8:]:
        messages.append({
            "role": msg["role"],
            "content": msg["message"]
        })

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Retry logic with exponential backoff
    max_retries = 3
    retry_delay = 1  # Start with 1 second

    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e)
            print(f"ERROR in AI response (attempt {attempt + 1}/{max_retries}): {error_msg}", file=sys.stderr)

            # Check for rate limit errors
            if "quota" in error_msg.lower() or "rate_limit" in error_msg.lower() or "too many requests" in error_msg.lower() or "429" in error_msg:
                if attempt < max_retries - 1:
                    # Wait with exponential backoff before retrying
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"Rate limit hit. Waiting {wait_time}s before retry...", file=sys.stderr)
                    time.sleep(wait_time)
                    continue
                else:
                    return "⏳ I'm receiving too many requests right now. Please wait a moment and try again. Our team is working on improving capacity!"

            # Check for authentication errors
            elif "API_KEY" in error_msg or "authentication" in error_msg.lower() or "invalid_api_key" in error_msg.lower():
                return "⚠️ API authentication failed. Please verify your MISTRAL_API_KEY is correct in the .env file."

            # For other errors, retry once more (except on last attempt)
            elif attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"Retrying in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                return f"⚠️ I encountered an error: {error_msg}. Please try again later."