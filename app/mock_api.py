"""
Mock API endpoints for IDP Platform dashboard.
Serves data from the in-memory mock database.
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.mock_db import (
    PLATFORM_STATS, PROJECTS, REPOSITORIES, ACTIVITY_FEED,
    search_codebase, get_repo_by_name, get_projects_by_status, get_activity_by_type
)

mock_router = APIRouter(prefix="/api", tags=["Platform Data"])


@mock_router.get("/stats")
async def get_stats():
    """Get platform-wide statistics for the dashboard."""
    return PLATFORM_STATS


@mock_router.get("/projects")
async def get_projects(status: Optional[str] = Query(None, description="Filter by status: active, staging, maintenance")):
    """List all projects, optionally filtered by status."""
    return get_projects_by_status(status or "")


@mock_router.get("/activity")
async def get_activity(
    event_type: Optional[str] = Query(None, description="Filter by type: deploy, pr_merged, incident, code_review"),
    limit: int = Query(20, ge=1, le=50)
):
    """Get the recent activity feed."""
    results = get_activity_by_type(event_type or "")
    return results[:limit]


@mock_router.get("/codebase")
async def get_codebase(q: Optional[str] = Query(None, description="Search by name, language, or description")):
    """List codebase repositories, optionally filtered by search query."""
    results = search_codebase(q or "")
    # Strip sample_files from list view for brevity
    return [
        {k: v for k, v in repo.items() if k != "sample_files"}
        for repo in results
    ]


@mock_router.get("/codebase/{repo_name}")
async def get_repo_detail(repo_name: str):
    """Get full details for a single repository, including sample files."""
    repo = get_repo_by_name(repo_name)
    if not repo:
        return {"error": f"Repository '{repo_name}' not found"}
    return repo
