import zipfile
import os
import io

def create_mock_project():
    # Define virtual file system
    files = {
        "package.json": """{
  "name": "mock-express-api",
  "version": "1.0.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.0.3",
    "cors": "^2.8.5"
  }
}""",
        "server.js": """require('dotenv').config();
const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/auth', authRoutes);

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the Mock API' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
""",
        "routes/auth.js": """const express = require('express');
const router = express.router();

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'password') {
    return res.json({ token: 'mock-jwt-token-123' });
  }
  res.status(401).json({ error: 'Invalid credentials' });
});

module.exports = router;
""",
        ".env.example": """PORT=3000
JWT_SECRET=secret_key
""",
        "README.md": """# Mock Express API

This is a sample project generated to test the IDP Platform upload feature.
It contains a simple Express server with a mock auth route.

## Usage
1. Upload this codebase.
2. Ask the AI to "Add a registration route" or "explain the auth flow".
"""
    }

    zip_filename = "mock_nodejs_project.zip"
    
    print(f"Creating {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
            print(f"  - Added {filename}")
            
    print(f"\n✅ {zip_filename} created successfully!")
    print(f"Location: {os.path.abspath(zip_filename)}")

if __name__ == "__main__":
    create_mock_project()
