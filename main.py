from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api import router
from app.mock_api import mock_router
from app.upload_api import upload_router
import os
from pathlib import Path

app = FastAPI(title="IDP Platform - AI-Powered Internal Developer Platform")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)
app.include_router(mock_router)
app.include_router(upload_router)

# Mount frontend static files — use absolute path
BASE_DIR = Path(__file__).resolve().parent
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir), html=True), name="static")

@app.get("/")
def read_root():
    """Redirect to the frontend dashboard."""
    return RedirectResponse(url="/static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
