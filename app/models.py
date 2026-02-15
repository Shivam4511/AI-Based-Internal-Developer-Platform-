from pydantic import BaseModel
from typing import Dict, List, Optional


class ChatRequest(BaseModel):
    message: str
    codebase_id: Optional[str] = None


class ChatResponse(BaseModel):
    folder_structure: str = ""
    files: Dict[str, str] = {}
    explanation: str = ""
    changes: List[dict] = []
