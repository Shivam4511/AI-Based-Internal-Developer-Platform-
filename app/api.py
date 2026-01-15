from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.core.llm import LLMService

router = APIRouter()
# Initialize LLM Service (this will check for API key)
try:
    llm_service = LLMService()
except ValueError as e:
    print(f"Warning: {e}")
    llm_service = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not llm_service:
        return ChatResponse(
            folder_structure="",
            files={},
            explanation="Grok API Key not configured. Please set GROK_API_KEY."
        )
    
    return llm_service.process_command(request.message)
