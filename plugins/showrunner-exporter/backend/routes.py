"""
Showrunner Exporter Plugin -- backend routes.

Provides API endpoints for exporting entity data to Showrunner.xyz format,
previewing exports, managing Showrunner projects, and batch operations.
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("plugin.showrunner-exporter")

router = APIRouter()

# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------
BRAINS_ROOT = Path("A:/Brains")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EXPORT_LOG_FILE = DATA_DIR / "export_log.json"
BACKEND_URL = "http://localhost:8201"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Entity type mappings
TYPE_PREFIX_MAP = {
    "character": "CH",
    "location": "LOC",
    "item": "ITEM",
    "faction": "FAC",
    "brand": "BR",
    "district": "DIST",
    "job": "JOB",
}

DEFAULT_ENTITY_TYPES = ["character", "location", "item", "faction", "brand", "district", "job"]


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------
def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("showrunner-exporter").get(key, default)


def _get_api_key() -> Optional[str]:
    return _get_setting("showrunner_api_key") or None


def _get_project_id() -> Optional[str]:
    return _get_setting("project_id") or None


def _get_api_url() -> str:
    return _get_setting("showrunner_api_url", "https://api.showrunner.xyz")


# ---------------------------------------------------------------------------
# Export log persistence
# ---------------------------------------------------------------------------
def _load_export_log() -> list:
    try:
        if EXPORT_LOG_FILE.exists():
            return json.loads(EXPORT_LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_export_log(log: list):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_LOG_FILE.write_text(
        json.dumps(log[-500:], indent=2, default=str), encoding="utf-8"
    )


def _append_export_log(entry: dict):
    log = _load_export_log()
    log.append(entry)
    _save_export_log(log)


# ---------------------------------------------------------------------------
# Entity data helpers
# ---------------------------------------------------------------------------
def _get_type_dir(entity_type: str) -> str:
    return entity_type.capitalize() + "s"


def _parse_frontmatter(filepath: str) -> dict:
    """Read a markdown file and extract YAML frontmatter as a dict."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    try:
        import yaml
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        data = {}
        for line in match.group(1).split("\n"):
            if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                key, _, val = line.partition(":")
                val = val.strip().strip("'\"")
                data[key.strip()] = val
        return data


def _extract_markdown_body(filepath: str) -> str:
    """Extract the markdown body after frontmatter."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        return ""

    match = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()


def _extract_dialogue_samples(markdown_body: str, limit: int = 5) -> list[str]:
    """Extract dialogue lines from markdown body (lines in quotes or after character names)."""
    samples = []
    # Match lines that look like dialogue: "text" or > text or CHARACTER: text
    patterns = [
        re.compile(r'"([^"]{10,200})"'),
        re.compile(r'^>\s*(.{10,200})$', re.MULTILINE),
        re.compile(r'^[A-Z][A-Z\s]+:\s*(.{10,200})$', re.MULTILINE),
    ]
    for pattern in patterns:
        for match in pattern.finditer(markdown_body):
            sample = match.group(1).strip()
            if sample and sample not in samples:
                samples.append(sample)
            if len(samples) >= limit:
                break
        if len(samples) >= limit:
            break
    return samples


async def _fetch_entity(entity_type: str, entity_id: str) -> dict:
    """Fetch entity data from the backend API."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND_URL}/api/entity/{entity_type}/{entity_id}")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch entity {entity_type}/{entity_id}",
            )
        return resp.json()


def _scan_entities(entity_type: str) -> list[dict]:
    """Scan all entities of a given type from the filesystem."""
    type_dir = BRAINS_ROOT / _get_type_dir(entity_type)
    if not type_dir.is_dir():
        return []

    prefix = TYPE_PREFIX_MAP.get(entity_type, entity_type.upper())
    results = []

    for entry in os.listdir(type_dir):
        entry_path = type_dir / entry
        if not entry_path.is_dir():
            continue

        md_file = entry_path / f"{prefix}_{entry}.md"
        if not md_file.is_file():
            continue

        fm = _parse_frontmatter(str(md_file))
        name = (
            fm.get("name")
            or fm.get("character_name")
            or fm.get("business_name")
            or fm.get("item_name")
            or fm.get("faction_name")
            or fm.get("brand_name")
            or fm.get("district_name")
            or fm.get("job_name")
            or entry.replace("_", " ").title()
        )

        # Look for portrait image
        image_url = None
        images_dir = entry_path / "images"
        if images_dir.is_dir():
            for img in os.listdir(images_dir):
                if img.lower().startswith("portrait") or img.lower().startswith("thumb"):
                    image_url = f"/api/entity/{entity_type}/{entry}/image/{img}"
                    break
            if not image_url:
                for img in os.listdir(images_dir):
                    if img.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        image_url = f"/api/entity/{entity_type}/{entry}/image/{img}"
                        break

        results.append({
            "id": entry,
            "type": entity_type,
            "name": name,
            "image": image_url,
            "description": fm.get("description", ""),
            "status": fm.get("status", ""),
        })

    return results


# ---------------------------------------------------------------------------
# Showrunner format converters
# ---------------------------------------------------------------------------
def character_to_showrunner(entity_data: dict, include_voice: bool = True) -> dict:
    """Convert entity data to Showrunner character bible format."""
    personality_traits = entity_data.get("personality_traits", [])
    if isinstance(personality_traits, str):
        personality_traits = [t.strip() for t in personality_traits.split(",")]

    distinguishing_features = entity_data.get("distinguishing_features", [])
    if isinstance(distinguishing_features, str):
        distinguishing_features = [f.strip() for f in distinguishing_features.split(",")]

    result = {
        "name": entity_data.get("name") or entity_data.get("character_name", "Unknown"),
        "description": entity_data.get("ai_profile_description") or entity_data.get("description", ""),
        "personality": personality_traits,
        "voice_style": entity_data.get("ai_voice_style", "") if include_voice else "",
        "appearance": {
            "hair": entity_data.get("hair_color", ""),
            "eyes": entity_data.get("eye_color", ""),
            "build": entity_data.get("build", ""),
            "features": distinguishing_features,
        },
        "backstory": entity_data.get("ai_bio_summary") or entity_data.get("backstory", ""),
        "dialogue_samples": [],
        "metadata": {
            "source": "city-of-brains",
            "entity_type": "character",
            "entity_id": entity_data.get("id", ""),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    # Additional character fields
    if entity_data.get("race"):
        result["race"] = entity_data["race"]
    if entity_data.get("age"):
        result["age"] = entity_data["age"]
    if entity_data.get("occupation") or entity_data.get("role"):
        result["role"] = entity_data.get("occupation") or entity_data.get("role")
    if entity_data.get("faction"):
        result["faction"] = entity_data["faction"]
    if entity_data.get("alignment"):
        result["alignment"] = entity_data["alignment"]
    if entity_data.get("motivations"):
        result["motivations"] = entity_data["motivations"]
    if entity_data.get("relationships"):
        result["relationships"] = entity_data["relationships"]

    return result


def location_to_showrunner(entity_data: dict) -> dict:
    """Convert location entity to Showrunner scene/set format."""
    return {
        "name": entity_data.get("name") or entity_data.get("location_name", "Unknown"),
        "description": entity_data.get("description", ""),
        "atmosphere": entity_data.get("atmosphere", ""),
        "visual_style": entity_data.get("visual_style", ""),
        "biome": entity_data.get("biome", ""),
        "region": entity_data.get("region", ""),
        "key_features": entity_data.get("key_features", []),
        "lighting": entity_data.get("lighting", ""),
        "sound_design": entity_data.get("ambient_sounds", ""),
        "metadata": {
            "source": "city-of-brains",
            "entity_type": "location",
            "entity_id": entity_data.get("id", ""),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def faction_to_showrunner(entity_data: dict) -> dict:
    """Convert faction entity to Showrunner organization format."""
    return {
        "name": entity_data.get("name") or entity_data.get("faction_name", "Unknown"),
        "description": entity_data.get("description", ""),
        "ideology": entity_data.get("ideology", ""),
        "goals": entity_data.get("goals", []),
        "structure": entity_data.get("structure", ""),
        "leader": entity_data.get("leader", ""),
        "territory": entity_data.get("territory", ""),
        "metadata": {
            "source": "city-of-brains",
            "entity_type": "faction",
            "entity_id": entity_data.get("id", ""),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def entity_to_showrunner(entity_data: dict, entity_type: str) -> dict:
    """Route entity to appropriate Showrunner converter."""
    include_voice = _get_setting("include_voice_data", True)
    if entity_type == "character":
        return character_to_showrunner(entity_data, include_voice=include_voice)
    elif entity_type == "location":
        return location_to_showrunner(entity_data)
    elif entity_type == "faction":
        return faction_to_showrunner(entity_data)
    else:
        # Generic export
        return {
            "name": entity_data.get("name", "Unknown"),
            "description": entity_data.get("description", ""),
            "type": entity_type,
            "raw_data": {k: v for k, v in entity_data.items()
                         if k not in ("id", "type") and v},
            "metadata": {
                "source": "city-of-brains",
                "entity_type": entity_type,
                "entity_id": entity_data.get("id", ""),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            },
        }


def _build_episode_outline(title: str, characters: list, scenes: list) -> dict:
    """Build a Showrunner episode outline from structured data."""
    return {
        "title": title,
        "format": "showrunner-native",
        "characters": characters,
        "scenes": [
            {
                "scene_number": i + 1,
                "location": scene.get("location", ""),
                "description": scene.get("description", ""),
                "characters": scene.get("characters", []),
                "dialogue": scene.get("dialogue", []),
                "direction": scene.get("direction", ""),
                "mood": scene.get("mood", ""),
            }
            for i, scene in enumerate(scenes)
        ],
        "metadata": {
            "source": "city-of-brains",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "scene_count": len(scenes),
            "character_count": len(characters),
        },
    }


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ExportEpisodeRequest(BaseModel):
    title: str
    characters: list = []
    scenes: list = []


class BatchExportRequest(BaseModel):
    entity_types: list[str] = ["character"]


# ---------------------------------------------------------------------------
# Mock Showrunner projects (used when no API key is configured)
# ---------------------------------------------------------------------------
MOCK_PROJECTS = [
    {
        "id": "proj_demo_001",
        "name": "City of Brains - Season 1",
        "status": "in_development",
        "episodes": 8,
        "characters_synced": 0,
        "last_sync": None,
        "created_at": "2025-11-15T10:30:00Z",
    },
    {
        "id": "proj_demo_002",
        "name": "The Neon District Chronicles",
        "status": "pre_production",
        "episodes": 0,
        "characters_synced": 0,
        "last_sync": None,
        "created_at": "2025-12-01T14:00:00Z",
    },
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/")
async def status():
    """Plugin status and configuration info."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("showrunner-exporter")
    api_key = _get_api_key()
    project_id = _get_project_id()
    export_log = _load_export_log()

    total_exports = len(export_log)
    successful = sum(1 for e in export_log if e.get("success"))
    last_export = export_log[-1] if export_log else None

    return {
        "plugin": "showrunner-exporter",
        "version": "1.0.0",
        "status": "ok",
        "api_configured": bool(api_key),
        "project_id": project_id or "",
        "auto_sync": settings.get("auto_sync", False),
        "include_voice_data": settings.get("include_voice_data", True),
        "export_mode": settings.get("export_mode", "full-bible"),
        "total_exports": total_exports,
        "successful_exports": successful,
        "last_export": last_export,
    }


@router.post("/export/character/{entity_id}")
async def export_character(entity_id: str):
    """Export a character bible to Showrunner format."""
    entity_data = await _fetch_entity("character", entity_id)
    showrunner_data = character_to_showrunner(
        entity_data,
        include_voice=_get_setting("include_voice_data", True),
    )

    # Try to extract dialogue samples from markdown source
    type_dir = BRAINS_ROOT / "Characters" / entity_id
    prefix = TYPE_PREFIX_MAP["character"]
    md_file = type_dir / f"{prefix}_{entity_id}.md"
    if md_file.is_file():
        body = _extract_markdown_body(str(md_file))
        showrunner_data["dialogue_samples"] = _extract_dialogue_samples(body)

    # Attempt to push to Showrunner API if configured
    api_key = _get_api_key()
    project_id = _get_project_id()
    pushed = False
    push_error = None

    if api_key and project_id:
        try:
            api_url = _get_api_url()
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{api_url}/v1/projects/{project_id}/characters",
                    json=showrunner_data,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                )
                pushed = resp.status_code in (200, 201)
                if not pushed:
                    push_error = f"Showrunner API returned {resp.status_code}: {resp.text[:200]}"
        except httpx.RequestError as exc:
            push_error = str(exc)

    # Log the export
    log_entry = {
        "id": str(uuid.uuid4()),
        "entity_type": "character",
        "entity_id": entity_id,
        "entity_name": showrunner_data["name"],
        "action": "export_character",
        "success": True,
        "pushed_to_showrunner": pushed,
        "push_error": push_error,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    _append_export_log(log_entry)

    return {
        "success": True,
        "entity_id": entity_id,
        "showrunner_data": showrunner_data,
        "pushed": pushed,
        "push_error": push_error,
        "message": (
            f"Character '{showrunner_data['name']}' exported"
            + (" and pushed to Showrunner" if pushed else " (preview only)")
        ),
    }


@router.post("/export/episode")
async def export_episode(req: ExportEpisodeRequest):
    """Export an episode outline to Showrunner format."""
    episode_data = _build_episode_outline(req.title, req.characters, req.scenes)

    # Attempt to push to Showrunner API if configured
    api_key = _get_api_key()
    project_id = _get_project_id()
    pushed = False
    push_error = None

    if api_key and project_id:
        try:
            api_url = _get_api_url()
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{api_url}/v1/projects/{project_id}/episodes",
                    json=episode_data,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                )
                pushed = resp.status_code in (200, 201)
                if not pushed:
                    push_error = f"Showrunner API returned {resp.status_code}"
        except httpx.RequestError as exc:
            push_error = str(exc)

    log_entry = {
        "id": str(uuid.uuid4()),
        "entity_type": "episode",
        "entity_id": req.title,
        "entity_name": req.title,
        "action": "export_episode",
        "success": True,
        "pushed_to_showrunner": pushed,
        "push_error": push_error,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    _append_export_log(log_entry)

    return {
        "success": True,
        "episode": episode_data,
        "pushed": pushed,
        "push_error": push_error,
        "message": f"Episode '{req.title}' exported with {len(req.scenes)} scenes",
    }


@router.get("/preview/{entity_type}/{entity_id}")
async def preview_export(entity_type: str, entity_id: str):
    """Preview the Showrunner-formatted JSON for an entity without exporting."""
    entity_data = await _fetch_entity(entity_type, entity_id)
    showrunner_data = entity_to_showrunner(entity_data, entity_type)

    # For characters, try to get dialogue samples
    if entity_type == "character":
        type_dir = BRAINS_ROOT / "Characters" / entity_id
        prefix = TYPE_PREFIX_MAP.get("character", "CH")
        md_file = type_dir / f"{prefix}_{entity_id}.md"
        if md_file.is_file():
            body = _extract_markdown_body(str(md_file))
            showrunner_data["dialogue_samples"] = _extract_dialogue_samples(body)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "entity_name": showrunner_data.get("name", "Unknown"),
        "showrunner_format": showrunner_data,
        "fields_populated": sum(1 for v in showrunner_data.values() if v),
        "fields_total": len(showrunner_data),
    }


@router.post("/batch-export")
async def batch_export(req: BatchExportRequest):
    """Batch export all entities of specified types to Showrunner format."""
    results = []
    errors = []

    for entity_type in req.entity_types:
        entities = _scan_entities(entity_type)
        for entity_info in entities:
            try:
                entity_data = await _fetch_entity(entity_type, entity_info["id"])
                showrunner_data = entity_to_showrunner(entity_data, entity_type)
                results.append({
                    "entity_type": entity_type,
                    "entity_id": entity_info["id"],
                    "entity_name": entity_info["name"],
                    "showrunner_data": showrunner_data,
                    "success": True,
                })
            except Exception as exc:
                errors.append({
                    "entity_type": entity_type,
                    "entity_id": entity_info["id"],
                    "entity_name": entity_info["name"],
                    "error": str(exc),
                    "success": False,
                })

    # Log batch export
    log_entry = {
        "id": str(uuid.uuid4()),
        "entity_type": "batch",
        "entity_id": "batch",
        "entity_name": f"Batch ({', '.join(req.entity_types)})",
        "action": "batch_export",
        "success": len(errors) == 0,
        "exported_count": len(results),
        "error_count": len(errors),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    _append_export_log(log_entry)

    return {
        "success": len(errors) == 0,
        "exported": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors,
        "message": f"Exported {len(results)} entities with {len(errors)} errors",
    }


@router.get("/projects")
async def list_projects():
    """List Showrunner projects. Returns mock data if no API key is configured."""
    api_key = _get_api_key()

    if not api_key:
        return {
            "source": "mock",
            "message": "No API key configured. Showing demo projects.",
            "projects": MOCK_PROJECTS,
        }

    try:
        api_url = _get_api_url()
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{api_url}/v1/projects",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code != 200:
                return {
                    "source": "error",
                    "message": f"Showrunner API returned {resp.status_code}",
                    "projects": MOCK_PROJECTS,
                }
            data = resp.json()
            return {
                "source": "showrunner",
                "projects": data.get("projects", data if isinstance(data, list) else []),
            }
    except httpx.RequestError as exc:
        return {
            "source": "error",
            "message": str(exc),
            "projects": MOCK_PROJECTS,
        }


@router.get("/export-log")
async def get_export_log(limit: int = 50):
    """Get export history."""
    log = _load_export_log()
    log.reverse()
    return {
        "total": len(log),
        "items": log[:limit],
    }


@router.get("/export-status/{entity_type}/{entity_id}")
async def get_export_status(entity_type: str, entity_id: str):
    """Get the export status for a specific entity."""
    log = _load_export_log()

    # Find entries for this entity
    entity_exports = [
        e for e in log
        if e.get("entity_type") == entity_type and e.get("entity_id") == entity_id
    ]

    last_export = entity_exports[-1] if entity_exports else None
    pushed_count = sum(1 for e in entity_exports if e.get("pushed_to_showrunner"))

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "total_exports": len(entity_exports),
        "pushed_count": pushed_count,
        "last_export": last_export,
        "has_been_exported": len(entity_exports) > 0,
        "project_id": _get_project_id() or "",
        "api_configured": bool(_get_api_key()),
    }


@router.get("/characters")
async def list_characters():
    """List all characters with their export status."""
    characters = _scan_entities("character")
    export_log = _load_export_log()

    # Build export status map
    export_map = {}
    for entry in export_log:
        if entry.get("entity_type") == "character":
            eid = entry.get("entity_id")
            if eid not in export_map:
                export_map[eid] = {"count": 0, "last": None, "pushed": False}
            export_map[eid]["count"] += 1
            export_map[eid]["last"] = entry.get("exported_at")
            if entry.get("pushed_to_showrunner"):
                export_map[eid]["pushed"] = True

    # Augment character list with export info
    for char in characters:
        status = export_map.get(char["id"], {"count": 0, "last": None, "pushed": False})
        char["export_count"] = status["count"]
        char["last_exported"] = status["last"]
        char["pushed_to_showrunner"] = status["pushed"]

    return {
        "characters": characters,
        "total": len(characters),
        "exported_count": sum(1 for c in characters if c.get("export_count", 0) > 0),
    }


@router.get("/stats")
async def get_stats():
    """Get export statistics."""
    log = _load_export_log()
    characters = _scan_entities("character")
    locations = _scan_entities("location")
    factions = _scan_entities("faction")

    total_exports = len(log)
    successful = sum(1 for e in log if e.get("success"))
    pushed = sum(1 for e in log if e.get("pushed_to_showrunner"))
    char_exports = sum(1 for e in log if e.get("entity_type") == "character")

    today = datetime.now(timezone.utc).date().isoformat()
    exports_today = sum(1 for e in log if e.get("exported_at", "").startswith(today))

    return {
        "total_exports": total_exports,
        "successful": successful,
        "pushed_to_showrunner": pushed,
        "character_exports": char_exports,
        "exports_today": exports_today,
        "total_characters": len(characters),
        "total_locations": len(locations),
        "total_factions": len(factions),
        "api_configured": bool(_get_api_key()),
        "project_id": _get_project_id() or "",
    }
