from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.core.llm import LLMService
from app.upload_api import UPLOADED_CODEBASES, save_codebases


router = APIRouter(prefix="/api")


# Initialize LLM Service
try:
    llm_service = LLMService()
except ValueError as e:
    print(f"Warning: {e}")
    llm_service = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not llm_service:
        return ChatResponse(
            explanation="Grok API Key not configured. Please set GROK_API_KEY."
        )

    # If a codebase_id is provided, use codebase-aware processing
    if request.codebase_id:
        cb = UPLOADED_CODEBASES.get(request.codebase_id)
        if not cb:
            return ChatResponse(
                explanation=f"Codebase '{request.codebase_id}' not found. Please upload it first."
            )

        result = llm_service.process_with_codebase(request.message, cb["files"])

        # Store the modified files back into the codebase for download
        if result.files:
            for path, content in result.files.items():
                cb["files"][path] = {
                    "content": content,
                    "size": len(content.encode("utf-8")),
                    "type": _detect_type(path)
                }

            cb["status"] = "modified"
            save_codebases()

        return result

    # Standard chat (no codebase context) 
    return llm_service.process_command(request.message)


def _detect_type(filename: str) -> str:
    """Quick language detection from extension."""
    import os
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "JavaScript React", ".tsx": "TypeScript React",
        ".html": "HTML", ".css": "CSS", ".json": "JSON",
        ".go": "Go", ".java": "Java", ".rs": "Rust",
    }
    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext, "Other")
