NODE_PACKAGE_JSON = """{
  "name": "my-service",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}"""

NODE_INDEX_JS = """const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello System!');
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
"""

PYTHON_REQUIREMENTS = """fastapi==0.109.0
uvicorn==0.27.0
"""

PYTHON_MAIN_PY = """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "System"}
"""

TEMPLATES = {
    "node": {
        "package.json": NODE_PACKAGE_JSON,
        "index.js": NODE_INDEX_JS
    },
    "python": {
        "requirements.txt": PYTHON_REQUIREMENTS,
        "main.py": PYTHON_MAIN_PY
    }
}
