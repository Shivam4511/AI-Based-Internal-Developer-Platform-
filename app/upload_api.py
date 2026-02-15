"""
Codebase Upload & AI Analysis API
Allows users to upload their codebase files, stores them in-memory,
and provides AI-powered code analysis and generation based on uploaded code.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import os
import io
import zipfile
import json
from datetime import datetime

upload_router = APIRouter(prefix="/api/upload", tags=["Codebase Upload"])

# In-memory storage (initialized from disk)
PERSISTENCE_FILE = "codebases.json"

def load_codebases():
    if os.path.exists(PERSISTENCE_FILE):
        try:
            with open(PERSISTENCE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading codebases: {e}")
    return {}

def save_codebases():
    try:
        with open(PERSISTENCE_FILE, "w", encoding="utf-8") as f:
            json.dump(UPLOADED_CODEBASES, f, indent=2)
    except Exception as e:
        print(f"Error saving codebases: {e}")

UPLOADED_CODEBASES = load_codebases()



@upload_router.post("/codebase")
async def upload_codebase(
    project_name: str = Form(...),
    description: str = Form(""),
    files: List[UploadFile] = File(...)
):
    """
    Upload a codebase (multiple files) for AI training/analysis.
    Files are stored in-memory and can be used for context-aware AI responses.
    """
    uploaded_files = {}
    total_size = 0
    languages = set()

    for f in files:
        # Check if it's a ZIP file
        if f.filename.lower().endswith('.zip'):
            content = await f.read()
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    for zip_info in z.infolist():
                        if zip_info.is_dir():
                            continue
                        
                        # Read file from zip
                        with z.open(zip_info) as zf:
                            file_content = zf.read()
                            
                            # Skip binary / large files inside zip
                            try:
                                text = file_content.decode("utf-8")
                                uploaded_files[zip_info.filename] = {
                                    "content": text,
                                    "size": len(file_content),
                                    "type": _detect_language(zip_info.filename)
                                }
                                total_size += len(file_content)
                                languages.add(_detect_language(zip_info.filename))
                            except UnicodeDecodeError:
                                # Skip binary files inside zip
                                pass
            except zipfile.BadZipFile:
                pass
            continue

        # Regular file upload
        content = await f.read()
        try:
            text = content.decode("utf-8")
            uploaded_files[f.filename] = {
                "content": text,
                "size": len(content),
                "type": _detect_language(f.filename)
            }
        except UnicodeDecodeError:
            uploaded_files[f.filename] = {
                "content": f"[Binary file - {len(content)} bytes]",
                "size": len(content),
                "type": _detect_language(f.filename)
            }
        
        total_size += len(content)
        languages.add(_detect_language(f.filename))

    codebase_id = f"cb-{len(UPLOADED_CODEBASES) + 1:03d}"


    UPLOADED_CODEBASES[codebase_id] = {
        "id": codebase_id,
        "project_name": project_name,
        "description": description,
        "files": uploaded_files,
        "file_count": len(uploaded_files),
        "total_size": total_size,
        "languages": list(languages),
        "uploaded_at": datetime.now().isoformat(),
        "status": "ready"
    }
    
    save_codebases()

    return {
        "success": True,
        "codebase_id": codebase_id,
        "project_name": project_name,
        "file_count": len(uploaded_files),
        "total_size_kb": round(total_size / 1024, 1),
        "languages": list(languages),
        "message": f"Codebase '{project_name}' uploaded successfully! {len(uploaded_files)} files indexed."
    }


@upload_router.get("/codebases")
async def list_uploaded_codebases():
    """List all uploaded codebases."""
    return [
        {
            "id": cb["id"],
            "project_name": cb["project_name"],
            "description": cb["description"],
            "file_count": cb["file_count"],
            "total_size_kb": round(cb["total_size"] / 1024, 1),
            "languages": cb["languages"],
            "uploaded_at": cb["uploaded_at"],
            "status": cb["status"]
        }
        for cb in UPLOADED_CODEBASES.values()
    ]


@upload_router.get("/codebases/{codebase_id}")
async def get_codebase_detail(codebase_id: str):
    """Get details of a specific uploaded codebase, including file listing."""
    if codebase_id not in UPLOADED_CODEBASES:
        raise HTTPException(status_code=404, detail="Codebase not found")

    cb = UPLOADED_CODEBASES[codebase_id]
    return {
        "id": cb["id"],
        "project_name": cb["project_name"],
        "description": cb["description"],
        "file_count": cb["file_count"],
        "total_size_kb": round(cb["total_size"] / 1024, 1),
        "languages": cb["languages"],
        "uploaded_at": cb["uploaded_at"],
        "status": cb["status"],
        "files": {
            name: {"size": info["size"], "type": info["type"]}
            for name, info in cb["files"].items()
        }
    }


@upload_router.get("/codebases/{codebase_id}/file")
async def get_uploaded_file(codebase_id: str, path: str):
    """Get the content of a specific file from an uploaded codebase."""
    if codebase_id not in UPLOADED_CODEBASES:
        raise HTTPException(status_code=404, detail="Codebase not found")

    cb = UPLOADED_CODEBASES[codebase_id]
    if path not in cb["files"]:
        raise HTTPException(status_code=404, detail=f"File '{path}' not found in codebase")

    return {
        "path": path,
        "content": cb["files"][path]["content"],
        "type": cb["files"][path]["type"],
        "size": cb["files"][path]["size"]
    }


@upload_router.delete("/codebases/{codebase_id}")
async def delete_codebase(codebase_id: str):
    """Delete an uploaded codebase."""
    if codebase_id not in UPLOADED_CODEBASES:
        raise HTTPException(status_code=404, detail="Codebase not found")

    name = UPLOADED_CODEBASES[codebase_id]["project_name"]
    del UPLOADED_CODEBASES[codebase_id]
    save_codebases()
    return {"success": True, "message": f"Codebase '{name}' deleted."}


@upload_router.post("/codebases/{codebase_id}/analyze")
async def analyze_codebase(codebase_id: str):
    """
    Generate a summary analysis of the uploaded codebase.
    Returns structure, languages, key patterns, and suggestions.
    """
    if codebase_id not in UPLOADED_CODEBASES:
        raise HTTPException(status_code=404, detail="Codebase not found")

    cb = UPLOADED_CODEBASES[codebase_id]
    files = cb["files"]

    # Build analysis
    lang_stats = {}
    for name, info in files.items():
        lang = info["type"]
        if lang not in lang_stats:
            lang_stats[lang] = {"count": 0, "total_size": 0}
        lang_stats[lang]["count"] += 1
        lang_stats[lang]["total_size"] += info["size"]

    # Detect patterns
    patterns = []
    file_names = [f.lower() for f in files.keys()]

    if any("test" in f or "spec" in f for f in file_names):
        patterns.append({"name": "Testing", "icon": "🧪", "detail": "Test files detected"})
    if any("docker" in f for f in file_names):
        patterns.append({"name": "Docker", "icon": "🐳", "detail": "Containerization configured"})
    if any(f.endswith("requirements.txt") or f.endswith("package.json") or f.endswith("go.mod") for f in file_names):
        patterns.append({"name": "Dependency Management", "icon": "📦", "detail": "Package manifest found"})
    if any(".env" in f for f in file_names):
        patterns.append({"name": "Environment Config", "icon": "⚙️", "detail": "Environment files detected"})
    if any("readme" in f for f in file_names):
        patterns.append({"name": "Documentation", "icon": "📄", "detail": "README found"})
    if any(f.endswith(".yml") or f.endswith(".yaml") for f in file_names):
        patterns.append({"name": "CI/CD Config", "icon": "🔄", "detail": "YAML config files found"})

    # Build file tree
    file_tree = _build_file_tree(list(files.keys()))

    return {
        "codebase_id": codebase_id,
        "project_name": cb["project_name"],
        "summary": {
            "total_files": len(files),
            "total_size_kb": round(cb["total_size"] / 1024, 1),
            "languages": lang_stats,
            "patterns": patterns
        },
        "file_tree": file_tree,
        "status": "analysis_complete"
    }


def _detect_language(filename: str) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".tsx": "TypeScript React", ".jsx": "JavaScript React",
        ".go": "Go", ".rs": "Rust", ".java": "Java",
        ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
        ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
        ".md": "Markdown", ".txt": "Text", ".sh": "Shell",
        ".sql": "SQL", ".tf": "HCL", ".toml": "TOML",
        ".xml": "XML", ".dockerfile": "Docker",
    }
    _, ext = os.path.splitext(filename.lower())
    if filename.lower() in ("dockerfile", "makefile", "procfile"):
        return filename.capitalize()
    return ext_map.get(ext, "Other")


def _build_file_tree(file_paths: list) -> str:
    """Build an ASCII file tree from a list of file paths."""
    tree = {}
    for path in sorted(file_paths):
        parts = path.replace("\\", "/").split("/")
        node = tree
        for part in parts:
            if part not in node:
                node[part] = {}
            node = node[part]

    lines = []
    _render_tree(tree, "", lines, True)
    return "\n".join(lines)


def _render_tree(node: dict, prefix: str, lines: list, is_root: bool = False):
    """Recursive ASCII tree renderer."""
    items = list(node.items())
    for i, (name, children) in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        if is_root and i == 0:
            lines.append(name + "/")
        else:
            lines.append(prefix + connector + (name + "/" if children else name))

        if children:
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension if not (is_root and i == 0) else prefix + "    "
            _render_tree(children, new_prefix, lines)


@upload_router.get("/codebases/{codebase_id}/download")
async def download_codebase(codebase_id: str):
    """Download the codebase (including AI-generated changes) as a ZIP file."""
    if codebase_id not in UPLOADED_CODEBASES:
        raise HTTPException(status_code=404, detail="Codebase not found")

    cb = UPLOADED_CODEBASES[codebase_id]
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, info in cb["files"].items():
            # Add file to zip
            zip_file.writestr(filename, info["content"])
    
    zip_buffer.seek(0)
    
    filename = f"{cb['project_name']}_modified.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
