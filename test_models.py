from mistralai.client import Mistral
from config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

# Test Mistral API connection
print("Testing Mistral API connection...")
try:
    message = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✓ Mistral API is working!")
    print(f"Response: {message.choices[0].message.content}")
except Exception as e:
    print(f"✗ Mistral API error: {e}")
