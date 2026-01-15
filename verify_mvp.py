from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_chat(message: str, expected_snippet: str):
    print(f"\n--- Testing: '{message}' ---")
    response = client.post("/chat", json={"message": message})
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.text)
        return

    data = response.json()
    print("Response received.")
    
    # Check structure
    if "folder_structure" in data and "files" in data:
        print("Structure keys present.")
    else:
        print("FAILED: Missing keys")
        
    # Check content
    content = str(data)
    if expected_snippet in content:
        print("Verified: Expected content found.")
    else:
        print(f"FAILED: Expected '{expected_snippet}' not found in response.")
        print("Response:", json.dumps(data, indent=2))

if __name__ == "__main__":
    print("Starting MVP Verification...")
    test_chat("Create a Node.js service", "package.json")
    test_chat("Create a Python FastAPI service", "requirements.txt")
    test_chat("Explain architecture", "IDP Architecture")
    print("\nVerification Complete.")
