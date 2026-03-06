import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "YOUR_GROQ_API_KEY_HERE":
    print("❌ GROQ_API_KEY not set in .env file!")
    exit(1)

print(f"🔑 Using Groq API key: {api_key[:10]}...{api_key[-4:]}")

try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'Groq API is working!' in one sentence."}]
    )
    print(f"✅ Groq API is working!")
    print(f"📝 Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Groq API failed: {e}")
