from typing import Dict, Tuple
from app.core.intents import Intent
from app.core.templates import TEMPLATES

class Generator:
    def generate(self, intent: Intent) -> Tuple[str, Dict[str, str], str]:
        if intent.action == "explain":
             return self._explain_architecture()
        
        if intent.tech_stack == "node":
            return self._generate_node_service()
        elif intent.tech_stack == "python":
            return self._generate_python_service()
        else:
            # Default to text response if unknown stack for creation
            return "", {}, "I can help you create a Node.js or Python service. Try 'Create a Node.js service'."

    def _generate_node_service(self) -> Tuple[str, Dict[str, str], str]:
        folder_structure = """
my-service/
├── package.json
└── index.js
"""
        files = TEMPLATES["node"]
        explanation = "Created a basic Node.js Express service logic."
        return folder_structure, files, explanation

    def _generate_python_service(self) -> Tuple[str, Dict[str, str], str]:
        folder_structure = """
my-service/
├── requirements.txt
└── main.py
"""
        files = TEMPLATES["python"]
        explanation = "Created a basic Python FastAPI service logic."
        return folder_structure, files, explanation

    def _explain_architecture(self) -> Tuple[str, Dict[str, str], str]:
        explanation = """
IDP Architecture:
1. **Frontend**: React-based portal for developers.
2. **Backend**: FastAPI service (like this one) specifically to handle scaffolding.
3. **Infrastructure**: Kubernetes clusters for deploying generated services.
        """
        return "", {}, explanation
