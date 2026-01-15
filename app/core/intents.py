from dataclasses import dataclass
from typing import Optional

@dataclass
class Intent:
    action: str  # "create", "explain"
    tech_stack: Optional[str]  # "node", "python", None
    target: str  # "service", "architecture"

class IntentParser:
    def parse(self, message: str) -> Intent:
        msg = message.lower()
        
        # Default intent
        action = "create"
        tech_stack = None
        target = "service"
        
        if "explain" in msg or "architecture" in msg:
            action = "explain"
            target = "architecture"
        
        if "node" in msg or "express" in msg:
            tech_stack = "node"
        elif "python" in msg or "fastapi" in msg:
            tech_stack = "python"
            
        return Intent(action=action, tech_stack=tech_stack, target=target)
