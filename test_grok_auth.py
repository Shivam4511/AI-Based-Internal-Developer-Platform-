import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
key = os.getenv("GROK_API_KEY")

client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

try:
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "say hi"}],
    )
    print("SUCCESS_GROQ")
except Exception as e:
    print(f"FAILED: {e}")
