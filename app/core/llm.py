from openai import OpenAI
import json
from app.core.config import GROK_API_KEY, GROK_BASE_URL
from app.core.prompts import SYSTEM_PROMPT
from app.models import ChatResponse

class LLMService:
    def __init__(self):
        if not GROK_API_KEY:
            raise ValueError("GROK_API_KEY is not set in environment variables.")
            
        self.client = OpenAI(
            api_key=GROK_API_KEY,
            base_url=GROK_BASE_URL
        )

    def process_command(self, user_message: str) -> ChatResponse:
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # Basic cleanup if model includes markdown blocks despite instructions
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            data = json.loads(content)
            
            return ChatResponse(
                folder_structure=data.get("folder_structure", ""),
                files=data.get("files", {}),
                explanation=data.get("explanation", "")
            )
            
        except Exception as e:
            # Fallback or error handling
            print(f"LLM Error: {e}")
            return ChatResponse(
                folder_structure="",
                files={},
                explanation=f"I encountered an error processing your request: {str(e)}"
            )
