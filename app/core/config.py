import os
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_BASE_URL = "https://api.groq.com/openai/v1"  # Switched to Groq based on key

