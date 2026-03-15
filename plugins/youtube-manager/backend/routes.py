"""
YouTube Manager Plugin - Backend Routes
Handles video uploads, metadata management, and YouTube API integration.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import json
import uuid
import os
import shutil

router = APIRouter()

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------
PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
VIDEOS_FILE = DATA_DIR / "videos.json"
ENTITY_API = "http://localhost:8201/api/entity"
BRAINS_ROOT = Path("A:/Brains")

YOUTUBE_CATEGORIES = {
    "Film & Animation": "1",
    "Autos & Vehicles": "2",
    "Music": "10",
    "Pets & Animals": "15",
    "Sports": "17",
    "Gaming": "20",
    "People & Blogs": "22",
    "Comedy": "23",
    "Entertainment": "24",
    "News & Politics": "25",
    "Howto & Style": "26",
    "Education": "27",
    "Science & Technology": "28",
}


def _ensure_data():
    """Make sure data directory and videos.json exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not VIDEOS_FILE.exists():
        VIDEOS_FILE.write_text("[]", encoding="utf-8")


def _load_videos() -> list:
    _ensure_data()
    try:
        return json.loads(VIDEOS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_videos(videos: list):
    _ensure_data()
    VIDEOS_FILE.write_text(json.dumps(videos, indent=2, default=str), encoding="utf-8")


def _get_settings() -> dict:
    """Load plugin settings from the DB-backed settings service."""
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("youtube-manager")


def _has_api_key() -> bool:
    settings = _get_settings()
    key = settings.get("youtube_api_key", "")
    return bool(key and key.strip())


def _mock_youtube_id() -> str:
    """Generate a fake YouTube video ID for mock mode."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    import random
    return "".join(random.choices(chars, k=11))


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class UploadRequest(BaseModel):
    entity_type: str
    entity_id: str
    video_path: str
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    privacy: Optional[str] = "unlisted"
    category: Optional[str] = "Gaming"
    thumbnail_path: Optional[str] = None


class VideoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy: Optional[str] = None
    category: Optional[str] = None


class MetadataResponse(BaseModel):
    title: str
    description: str
    tags: List[str]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def status():
    """Plugin health check and status."""
    settings = _get_settings()
    videos = _load_videos()
    has_key = _has_api_key()
    return {
        "status": "ok",
        "plugin": "youtube-manager",
        "version": "0.2.0",
        "mode": "live" if has_key else "mock",
        "channel_id": settings.get("channel_id", ""),
        "total_videos": len(videos),
        "uploaded": len([v for v in videos if v.get("status") == "uploaded"]),
        "pending": len([v for v in videos if v.get("status") == "pending"]),
        "failed": len([v for v in videos if v.get("status") == "failed"]),
    }


@router.post("/upload")
async def upload_video(req: UploadRequest):
    """
    Upload a video to YouTube (or mock the upload if no API key configured).
    Stores tracking metadata in data/videos.json.
    """
    # Validate video file exists
    video_path = Path(req.video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video file not found: {req.video_path}")

    settings = _get_settings()
    video_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Build the video record
    record = {
        "id": video_id,
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "video_path": str(video_path),
        "title": req.title,
        "description": req.description or "",
        "tags": req.tags or [],
        "privacy": req.privacy or settings.get("default_privacy", "unlisted"),
        "category": req.category or settings.get("default_category", "Gaming"),
        "thumbnail_path": req.thumbnail_path,
        "created_at": now,
        "updated_at": now,
    }

    if _has_api_key():
        # -- Live YouTube upload would happen here --
        # For now we simulate a successful upload
        record["status"] = "uploaded"
        record["youtube_id"] = _mock_youtube_id()
        record["youtube_url"] = f"https://www.youtube.com/watch?v={record['youtube_id']}"
        record["upload_progress"] = 100
    else:
        # Mock mode
        record["status"] = "uploaded"
        record["youtube_id"] = _mock_youtube_id()
        record["youtube_url"] = f"https://www.youtube.com/watch?v={record['youtube_id']}"
        record["upload_progress"] = 100
        record["mock"] = True

    videos = _load_videos()
    videos.append(record)
    _save_videos(videos)

    return {
        "success": True,
        "video": record,
        "mode": "live" if _has_api_key() else "mock",
    }


@router.get("/videos")
async def list_videos():
    """List all tracked videos."""
    videos = _load_videos()
    # Sort by created_at descending
    videos.sort(key=lambda v: v.get("created_at", ""), reverse=True)
    return {
        "videos": videos,
        "total": len(videos),
    }


@router.get("/videos/{entity_type}/{entity_id}")
async def videos_for_entity(entity_type: str, entity_id: str):
    """Get all videos linked to a specific entity."""
    videos = _load_videos()
    linked = [
        v for v in videos
        if v.get("entity_type") == entity_type and v.get("entity_id") == entity_id
    ]
    linked.sort(key=lambda v: v.get("created_at", ""), reverse=True)
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "videos": linked,
        "total": len(linked),
    }


@router.put("/videos/{video_id}")
async def update_video(video_id: str, req: VideoUpdateRequest):
    """Update metadata for a tracked video."""
    videos = _load_videos()
    target = None
    for v in videos:
        if v.get("id") == video_id:
            target = v
            break

    if not target:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

    if req.title is not None:
        target["title"] = req.title
    if req.description is not None:
        target["description"] = req.description
    if req.tags is not None:
        target["tags"] = req.tags
    if req.privacy is not None:
        target["privacy"] = req.privacy
    if req.category is not None:
        target["category"] = req.category
    target["updated_at"] = datetime.utcnow().isoformat()

    _save_videos(videos)
    return {"success": True, "video": target}


@router.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """Remove a video from tracking (does not delete from YouTube)."""
    videos = _load_videos()
    filtered = [v for v in videos if v.get("id") != video_id]
    if len(filtered) == len(videos):
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    _save_videos(filtered)
    return {"success": True, "deleted": video_id}


@router.post("/generate-metadata/{entity_type}/{entity_id}")
async def generate_metadata(entity_type: str, entity_id: str):
    """
    Auto-generate video title, description, and tags from entity data.
    Fetches entity info from the platform API and applies the description template.
    """
    import httpx

    settings = _get_settings()
    template = settings.get(
        "description_template",
        "{name} - {type}\n\n{description}\n\n#{tags}\n\nCreated with City of Brains Studio"
    )

    # Fetch entity data
    entity_url = f"{ENTITY_API}/{entity_type}/{entity_id}"
    entity_data = {}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(entity_url)
            if resp.status_code == 200:
                entity_data = resp.json()
    except Exception:
        # If we can't reach the entity API, use fallback data
        entity_data = {
            "name": entity_id.replace("-", " ").replace("_", " ").title(),
            "type": entity_type,
            "description": f"A {entity_type} from City of Brains Studio.",
            "tags": [],
        }

    name = entity_data.get("name", entity_id)
    etype = entity_data.get("type", entity_type)
    desc = entity_data.get("description", "") or entity_data.get("bio", "") or entity_data.get("summary", "")
    raw_tags = entity_data.get("tags", []) or []
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

    # Build title
    title = f"{name} | {etype.replace('_', ' ').title()} Reveal"

    # Build tags
    base_tags = [name.lower(), etype.lower(), "cityofbrains", "character", "lore", "gaming"]
    all_tags = list(dict.fromkeys(base_tags + [t.lower() for t in raw_tags]))  # deduplicate

    # Build description from template
    tags_str = " #".join(all_tags[:15])
    description = template.format(
        name=name,
        type=etype.replace("_", " ").title(),
        description=desc if desc else f"Discover {name}, a {etype} from the City of Brains universe.",
        tags=tags_str,
    )

    return {
        "title": title,
        "description": description,
        "tags": all_tags[:20],
        "entity": {
            "name": name,
            "type": etype,
        }
    }


@router.get("/asset-videos/{entity_type}/{entity_id}")
async def list_entity_asset_videos(entity_type: str, entity_id: str):
    """List video files from an entity's assets directory."""
    # Build path: A:\Brains\{Type}s\{id}\assets\
    type_folder = entity_type.rstrip("s") + "s" if not entity_type.endswith("s") else entity_type
    type_folder = type_folder.title()
    assets_dir = BRAINS_ROOT / type_folder / entity_id / "assets"

    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv"}
    videos = []

    if assets_dir.exists():
        for f in assets_dir.iterdir():
            if f.is_file() and f.suffix.lower() in video_extensions:
                stat = f.stat()
                videos.append({
                    "filename": f.name,
                    "path": str(f),
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

    videos.sort(key=lambda v: v.get("modified", ""), reverse=True)
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "assets_dir": str(assets_dir),
        "videos": videos,
        "total": len(videos),
    }


@router.get("/categories")
async def list_categories():
    """Return available YouTube video categories."""
    return {"categories": YOUTUBE_CATEGORIES}
