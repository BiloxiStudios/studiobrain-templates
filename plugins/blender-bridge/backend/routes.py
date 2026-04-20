"""
Blender Bridge Plugin -- backend routes.

Provides endpoints for exporting entity data to Blender-compatible JSON,
managing render requests, checking Blender connection status, and batch
export operations.
"""

import json
import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import List

import aiohttp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("plugin.blender-bridge")

router = APIRouter()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BRAINS_ROOT = Path("A:/Brains")
PLUGIN_DATA = Path("A:/Brains/_Plugins/blender-bridge/data")
EXPORTS_DIR = PLUGIN_DATA / "exports"
RENDERS_DIR = PLUGIN_DATA / "renders"
RENDER_QUEUE_FILE = PLUGIN_DATA / "render_queue.json"
EXPORT_LOG_FILE = PLUGIN_DATA / "export_log.json"

# Ensure directories exist
PLUGIN_DATA.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

# Entity type -> file prefix mapping
TYPE_PREFIX_MAP = {
    "character": "CH",
    "location": "LOC",
    "item": "ITEM",
    "faction": "FAC",
    "brand": "BR",
    "district": "DIST",
    "job": "JOB",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("blender-bridge").get(key, default)

def _blender_url() -> str:
    """Build the Blender command server URL from settings."""
    host = _get_setting("blender_host", "localhost")
    port = _get_setting("blender_port", 8400)
    return f"http://{host}:{port}"

def _get_type_dir(entity_type: str) -> str:
    """Return the directory name for a given entity type (e.g. character -> Characters)."""
    singular = entity_type.rstrip("s")
    return singular.capitalize() + "s"

def _get_entity_file(entity_type: str, entity_id: str) -> str:
    """Return absolute path to an entity's markdown file."""
    type_dir = _get_type_dir(entity_type)
    prefix = TYPE_PREFIX_MAP.get(entity_type, entity_type.upper())
    return str(BRAINS_ROOT / type_dir / entity_id / f"{prefix}_{entity_id}.md")

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

def _load_json(path: Path, default=None):
    """Load JSON from a file, returning default on any error."""
    if default is None:
        default = []
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def _save_json(path: Path, data, max_entries: int = 0):
    """Save data as JSON. If max_entries > 0 and data is a list, truncate."""
    if max_entries > 0 and isinstance(data, list):
        data = data[-max_entries:]
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

def _load_export_log() -> list:
    return _load_json(EXPORT_LOG_FILE, [])

def _save_export_log(log: list):
    _save_json(EXPORT_LOG_FILE, log, max_entries=500)

def _load_render_queue() -> list:
    return _load_json(RENDER_QUEUE_FILE, [])

def _save_render_queue(queue: list):
    _save_json(RENDER_QUEUE_FILE, queue, max_entries=200)

# ---------------------------------------------------------------------------
# Entity -> Blender data conversion
# ---------------------------------------------------------------------------

def _ensure_list(val) -> list:
    """Normalize a value to a list."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val] if val.strip() else []
    return [val]

def entity_to_blender_data(entity_type: str, entity_id: str, entity_data: dict) -> dict:
    """
    Convert entity frontmatter into a JSON structure suitable
    for Blender's Python API (bpy.types.Object custom properties).
    """
    base = {
        "source": "city-of-brains",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "name": (
            entity_data.get("name")
            or entity_data.get("character_name")
            or entity_data.get("business_name")
            or entity_data.get("item_name")
            or entity_data.get("faction_name")
            or entity_id.replace("_", " ").title()
        ),
        "exported_at": int(time.time()),
    }

    if entity_type == "character":
        base["blender_type"] = "character"
        base["properties"] = {
            "height": entity_data.get("height", ""),
            "build": entity_data.get("build", ""),
            "age": entity_data.get("age", ""),
            "gender": entity_data.get("gender", ""),
            "species": entity_data.get("species", "human"),
            "hair_color": entity_data.get("hair_color", ""),
            "eye_color": entity_data.get("eye_color", ""),
            "skin_tone": entity_data.get("skin_tone", ""),
            "distinguishing_features": _ensure_list(
                entity_data.get("distinguishing_features")
            ),
        }
        base["metadata"] = {
            "nickname": entity_data.get("nickname", ""),
            "primary_location": entity_data.get("primary_location", ""),
            "secondary_locations": _ensure_list(
                entity_data.get("secondary_locations")
            ),
            "faction": entity_data.get("faction", ""),
            "personality_traits": _ensure_list(
                entity_data.get("personality_traits")
            ),
            "primary_skills": _ensure_list(
                entity_data.get("primary_skills")
            ),
            "inventory_items": _ensure_list(
                entity_data.get("inventory_items")
            ),
        }
        # Parse height into numeric meters for Blender armature scaling
        base["dimensions"] = _parse_character_dimensions(entity_data)

    elif entity_type == "location":
        base["blender_type"] = "scene"
        base["properties"] = {
            "location_type": entity_data.get("location_type", ""),
            "category": entity_data.get("category", ""),
            "biome": entity_data.get("biome", ""),
            "district": entity_data.get("district", ""),
            "address": entity_data.get("address", ""),
            "enterable": entity_data.get("enterable", False),
            "exterior_access": entity_data.get("exterior_access", False),
        }
        base["coordinates"] = {
            "x": _to_float(entity_data.get("coordinates_x", 0)),
            "y": _to_float(entity_data.get("coordinates_y", 0)),
            "z": _to_float(entity_data.get("coordinates_z", 0)),
        }
        base["metadata"] = {
            "parent_location": entity_data.get("parent_location", ""),
            "entrance_points": _ensure_list(
                entity_data.get("entrance_points")
            ),
            "founded_year": entity_data.get("founded_year"),
            "destroyed_year": entity_data.get("destroyed_year"),
        }
        # Scene setup hints for Blender
        base["scene_setup"] = _build_scene_setup(entity_data)

    elif entity_type == "item":
        base["blender_type"] = "prop"
        base["properties"] = {
            "item_type": entity_data.get("item_type", ""),
            "rarity": entity_data.get("rarity", ""),
            "weight": entity_data.get("weight", ""),
            "material": entity_data.get("material", ""),
            "color": entity_data.get("color", ""),
            "size": entity_data.get("size", ""),
        }
        base["metadata"] = {
            "description": entity_data.get("description", ""),
            "effects": _ensure_list(entity_data.get("effects")),
        }

    else:
        # Generic export for any other entity type
        base["blender_type"] = "custom"
        base["properties"] = {
            k: v for k, v in entity_data.items()
            if k not in ("template_version",) and isinstance(v, (str, int, float, bool))
        }
        base["metadata"] = {}

    # Attach image references if present
    images = _ensure_list(entity_data.get("images"))
    if images:
        base["reference_images"] = images[:10]  # Limit to 10

    return base

def _parse_character_dimensions(data: dict) -> dict:
    """
    Parse height string (e.g. '6\\'2"', '5 foot 10', '180cm') into
    approximate meters for Blender armature scaling.
    """
    height_str = str(data.get("height", ""))
    meters = 1.75  # default

    # Try feet'inches" format
    ft_match = re.match(r"(\d+)'(\d+)\"?", height_str)
    if ft_match:
        feet = int(ft_match.group(1))
        inches = int(ft_match.group(2))
        meters = round((feet * 12 + inches) * 0.0254, 2)
    else:
        # Try cm
        cm_match = re.match(r"(\d+)\s*cm", height_str, re.IGNORECASE)
        if cm_match:
            meters = round(int(cm_match.group(1)) / 100, 2)

    build = str(data.get("build", "average")).lower()
    build_scale = {
        "thin": 0.85,
        "slim": 0.9,
        "lean": 0.92,
        "average": 1.0,
        "medium": 1.0,
        "athletic": 1.05,
        "muscular": 1.1,
        "stocky": 1.1,
        "heavy": 1.15,
        "large": 1.2,
        "massive": 1.3,
    }
    width_factor = build_scale.get(build, 1.0)

    return {
        "height_meters": meters,
        "height_raw": height_str,
        "build": build,
        "width_scale_factor": width_factor,
        "armature_scale": [width_factor, width_factor, meters / 1.75],
    }

def _to_float(val, default: float = 0.0) -> float:
    """Safely convert to float."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def _build_scene_setup(data: dict) -> dict:
    """Build Blender scene setup hints from location data."""
    biome = str(data.get("biome", "")).lower()

    # Map biomes to lighting/environment presets
    environment_map = {
        "urban": {"hdri_suggestion": "city_night", "sun_intensity": 0.8, "ambient_color": [0.15, 0.15, 0.2]},
        "forest": {"hdri_suggestion": "forest_path", "sun_intensity": 0.5, "ambient_color": [0.1, 0.15, 0.1]},
        "desert": {"hdri_suggestion": "desert_sun", "sun_intensity": 1.2, "ambient_color": [0.3, 0.25, 0.15]},
        "coastal": {"hdri_suggestion": "ocean_hdri", "sun_intensity": 1.0, "ambient_color": [0.15, 0.2, 0.25]},
        "underground": {"hdri_suggestion": "studio_dark", "sun_intensity": 0.0, "ambient_color": [0.05, 0.05, 0.08]},
        "industrial": {"hdri_suggestion": "warehouse", "sun_intensity": 0.6, "ambient_color": [0.12, 0.12, 0.12]},
    }

    env = environment_map.get(biome, {"hdri_suggestion": "studio_neutral", "sun_intensity": 0.7, "ambient_color": [0.15, 0.15, 0.15]})

    return {
        "environment": env,
        "world_coordinates": {
            "x": _to_float(data.get("coordinates_x", 0)),
            "y": _to_float(data.get("coordinates_y", 0)),
            "z": _to_float(data.get("coordinates_z", 0)),
        },
        "category": data.get("category", ""),
        "is_interior": data.get("enterable", False),
        "has_exterior": data.get("exterior_access", False),
    }

def _entity_images_dir(entity_type: str, entity_id: str) -> Path:
    """Return the images directory for an entity."""
    type_folder = _get_type_dir(entity_type)
    return BRAINS_ROOT / type_folder / entity_id / "images"

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class BatchExportRequest(BaseModel):
    entity_type: str
    entity_ids: List[str]

class RenderRequest(BaseModel):
    scene_file: str
    entity_ids: List[str] = Field(default_factory=list)
    render_settings: dict = Field(default_factory=lambda: {
        "engine": "CYCLES",
        "samples": 128,
        "resolution_x": 1920,
        "resolution_y": 1080,
        "output_format": "PNG",
    })

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def plugin_status():
    """Status endpoint with Blender connection info."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("blender-bridge")
    blender_port = settings.get("blender_port", 8400)
    export_log = _load_export_log()
    render_queue = _load_render_queue()

    # Quick connection check
    connected = False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{_blender_url()}/status",
                timeout=aiohttp.ClientTimeout(total=3),
            ) as resp:
                if resp.status == 200:
                    connected = True
    except Exception:
        pass

    return {
        "plugin": "blender-bridge",
        "version": "0.2.0",
        "blender_connected": connected,
        "blender_port": blender_port,
        "auto_export": settings.get("auto_export", False),
        "total_exports": len(export_log),
        "pending_renders": len([r for r in render_queue if r.get("status") == "pending"]),
        "completed_renders": len([r for r in render_queue if r.get("status") == "completed"]),
    }

@router.get("/connection-status")
async def connection_status():
    """Detailed Blender connection check."""
    blender_url = _blender_url()
    result = {
        "url": blender_url,
        "connected": False,
        "blender_version": None,
        "scene_name": None,
        "error": None,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{blender_url}/status",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result["connected"] = True
                    result["blender_version"] = data.get("blender_version", "unknown")
                    result["scene_name"] = data.get("scene_name", "unknown")
                else:
                    result["error"] = f"HTTP {resp.status}"
    except aiohttp.ClientConnectorError:
        result["error"] = f"Cannot connect to Blender at {blender_url}. Is the Blender command server addon running?"
    except Exception as exc:
        result["error"] = str(exc)

    return result

@router.get("/export-format/{entity_type}/{entity_id}")
async def preview_export(entity_type: str, entity_id: str):
    """Preview the Blender export data for an entity without actually exporting."""
    filepath = _get_entity_file(entity_type, entity_id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    fm = _parse_frontmatter(filepath)
    blender_data = entity_to_blender_data(entity_type, entity_id, fm)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "preview": True,
        "blender_data": blender_data,
    }

@router.post("/export/{entity_type}/{entity_id}")
async def export_entity(entity_type: str, entity_id: str):
    """
    Export entity data as Blender-compatible JSON.
    Saves to the exports directory and optionally sends to Blender if connected.
    """
    filepath = _get_entity_file(entity_type, entity_id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    fm = _parse_frontmatter(filepath)
    blender_data = entity_to_blender_data(entity_type, entity_id, fm)

    # Save export file
    ts = int(time.time())
    short_id = uuid.uuid4().hex[:8]
    export_filename = f"{entity_type}_{entity_id}_{ts}_{short_id}.json"
    export_path = EXPORTS_DIR / export_filename
    export_path.write_text(json.dumps(blender_data, indent=2, default=str), encoding="utf-8")

    logger.info("Exported entity %s/%s to %s", entity_type, entity_id, export_path)

    # Try to send to Blender if connected
    sent_to_blender = False
    blender_error = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{_blender_url()}/import",
                json=blender_data,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    sent_to_blender = True
                else:
                    blender_error = f"Blender returned HTTP {resp.status}"
    except aiohttp.ClientConnectorError:
        blender_error = "Blender not connected"
    except Exception as exc:
        blender_error = str(exc)

    # Log the export
    log = _load_export_log()
    log.append({
        "timestamp": ts,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "name": blender_data["name"],
        "filename": export_filename,
        "sent_to_blender": sent_to_blender,
        "blender_error": blender_error,
    })
    _save_export_log(log)

    return {
        "success": True,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "name": blender_data["name"],
        "export_file": export_filename,
        "sent_to_blender": sent_to_blender,
        "blender_error": blender_error,
        "blender_data": blender_data,
    }

@router.post("/batch-export")
async def batch_export(req: BatchExportRequest):
    """Export multiple entities at once."""
    results = []
    errors = []

    for eid in req.entity_ids:
        filepath = _get_entity_file(req.entity_type, eid)
        if not os.path.isfile(filepath):
            errors.append({"entity_id": eid, "error": "Entity not found"})
            continue

        fm = _parse_frontmatter(filepath)
        blender_data = entity_to_blender_data(req.entity_type, eid, fm)

        ts = int(time.time())
        short_id = uuid.uuid4().hex[:8]
        export_filename = f"{req.entity_type}_{eid}_{ts}_{short_id}.json"
        export_path = EXPORTS_DIR / export_filename
        export_path.write_text(json.dumps(blender_data, indent=2, default=str), encoding="utf-8")

        results.append({
            "entity_id": eid,
            "name": blender_data["name"],
            "export_file": export_filename,
        })

    # Try batch send to Blender
    sent_to_blender = False
    blender_error = None
    if results:
        try:
            batch_payload = {
                "entity_type": req.entity_type,
                "entities": [
                    json.loads((EXPORTS_DIR / r["export_file"]).read_text(encoding="utf-8"))
                    for r in results
                ],
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{_blender_url()}/batch-import",
                    json=batch_payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        sent_to_blender = True
                    else:
                        blender_error = f"Blender returned HTTP {resp.status}"
        except aiohttp.ClientConnectorError:
            blender_error = "Blender not connected"
        except Exception as exc:
            blender_error = str(exc)

    # Log
    log = _load_export_log()
    log.append({
        "timestamp": int(time.time()),
        "entity_type": req.entity_type,
        "batch": True,
        "count": len(results),
        "entity_ids": [r["entity_id"] for r in results],
        "sent_to_blender": sent_to_blender,
    })
    _save_export_log(log)

    return {
        "success": True,
        "exported": len(results),
        "errors": errors,
        "results": results,
        "sent_to_blender": sent_to_blender,
        "blender_error": blender_error,
    }

@router.post("/render-request")
async def create_render_request(req: RenderRequest):
    """Queue a render request for Blender."""
    request_id = uuid.uuid4().hex[:12]
    ts = int(time.time())

    render_entry = {
        "id": request_id,
        "scene_file": req.scene_file,
        "entity_ids": req.entity_ids,
        "render_settings": req.render_settings,
        "status": "pending",
        "created_at": ts,
        "started_at": None,
        "completed_at": None,
        "output_file": None,
        "error": None,
    }

    # Try to send to Blender
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{_blender_url()}/render",
                json={
                    "request_id": request_id,
                    "scene_file": req.scene_file,
                    "entity_ids": req.entity_ids,
                    "settings": req.render_settings,
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    render_entry["status"] = "queued"
                else:
                    render_entry["error"] = f"Blender returned HTTP {resp.status}"
    except aiohttp.ClientConnectorError:
        render_entry["error"] = "Blender not connected -- render saved locally"
    except Exception as exc:
        render_entry["error"] = str(exc)

    queue = _load_render_queue()
    queue.append(render_entry)
    _save_render_queue(queue)

    logger.info("Render request created: %s", request_id)

    return {
        "success": True,
        "request_id": request_id,
        "status": render_entry["status"],
        "error": render_entry["error"],
    }

@router.get("/renders")
async def list_renders():
    """List all render requests and their statuses."""
    queue = _load_render_queue()

    # Also scan renders directory for completed files
    completed_files = []
    if RENDERS_DIR.exists():
        for f in sorted(RENDERS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".exr", ".tiff"):
                stat = f.stat()
                completed_files.append({
                    "filename": f.name,
                    "size": stat.st_size,
                    "created": int(stat.st_mtime),
                    "path": str(f),
                })

    # Sort queue by most recent first
    queue.sort(key=lambda x: x.get("created_at", 0), reverse=True)

    return {
        "queue": queue[:50],
        "completed_files": completed_files[:50],
        "total_requests": len(queue),
        "pending": len([r for r in queue if r.get("status") == "pending"]),
        "completed": len([r for r in queue if r.get("status") == "completed"]),
    }

@router.get("/export-log")
async def get_export_log():
    """Return recent export history."""
    log = _load_export_log()
    log.reverse()
    return {"entries": log[:100]}

@router.get("/exports/{entity_type}/{entity_id}")
async def get_entity_exports(entity_type: str, entity_id: str):
    """List all export files for a specific entity."""
    exports = []
    prefix = f"{entity_type}_{entity_id}_"

    if EXPORTS_DIR.exists():
        for f in sorted(EXPORTS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.name.startswith(prefix) and f.suffix == ".json":
                stat = f.stat()
                exports.append({
                    "filename": f.name,
                    "size": stat.st_size,
                    "created": int(stat.st_mtime),
                })

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "exports": exports,
    }

@router.get("/available-entities/{entity_type}")
async def list_available_entities(entity_type: str):
    """List all entities of a type that can be exported."""
    type_dir = BRAINS_ROOT / _get_type_dir(entity_type)
    if not type_dir.is_dir():
        return {"entity_type": entity_type, "entities": []}

    prefix = TYPE_PREFIX_MAP.get(entity_type, entity_type.upper())
    entities = []

    for entry in sorted(type_dir.iterdir()):
        if not entry.is_dir():
            continue
        md_file = entry / f"{prefix}_{entry.name}.md"
        if not md_file.is_file():
            continue

        fm = _parse_frontmatter(str(md_file))
        name = (
            fm.get("name")
            or fm.get("character_name")
            or fm.get("business_name")
            or fm.get("item_name")
            or fm.get("faction_name")
            or entry.name.replace("_", " ").title()
        )

        # Check for image
        image_url = None
        images_dir = entry / "images"
        if images_dir.is_dir():
            for img in images_dir.iterdir():
                if img.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                    image_url = f"/api/entity/{entity_type}/{entry.name}/image/{img.name}"
                    break

        entities.append({
            "id": entry.name,
            "name": name,
            "image": image_url,
            "has_height": bool(fm.get("height")),
            "has_build": bool(fm.get("build")),
        })

    return {"entity_type": entity_type, "entities": entities}
