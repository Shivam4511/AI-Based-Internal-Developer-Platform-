from pydantic import BaseModel
from typing import Dict

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    folder_structure: str
    files: Dict[str, str]
    explanation: str
