"""
Notion Sync Plugin — backend routes.

Provides endpoints for syncing Studio entities with Notion databases,
managing field mappings, checking sync status, and listing Notion
databases. When no API key is configured, endpoints return mock data
with clear setup instructions.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger("plugin.notion-sync")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SYNC_STATE_FILE = DATA_DIR / "sync_state.json"
MAPPINGS_FILE = DATA_DIR / "field_mappings.json"
SYNC_LOG_FILE = DATA_DIR / "sync_log.json"
BACKEND_URL = "http://localhost:8201"
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# ---------------------------------------------------------------------------
# Default field mappings per entity type
# ---------------------------------------------------------------------------

DEFAULT_MAPPINGS = {
    "character": {
        "name": {"notion_property": "Name", "notion_type": "title"},
        "description": {"notion_property": "Description", "notion_type": "rich_text"},
        "race": {"notion_property": "Race", "notion_type": "select"},
        "class_name": {"notion_property": "Class", "notion_type": "select"},
        "role": {"notion_property": "Role", "notion_type": "select"},
        "faction": {"notion_property": "Faction", "notion_type": "select"},
        "status": {"notion_property": "Status", "notion_type": "select"},
    },
    "location": {
        "name": {"notion_property": "Name", "notion_type": "title"},
        "description": {"notion_property": "Description", "notion_type": "rich_text"},
        "region": {"notion_property": "Region", "notion_type": "select"},
        "biome": {"notion_property": "Biome", "notion_type": "select"},
        "status": {"notion_property": "Status", "notion_type": "select"},
    },
    "item": {
        "name": {"notion_property": "Name", "notion_type": "title"},
        "description": {"notion_property": "Description", "notion_type": "rich_text"},
        "rarity": {"notion_property": "Rarity", "notion_type": "select"},
        "status": {"notion_property": "Status", "notion_type": "select"},
    },
    "quest": {
        "name": {"notion_property": "Name", "notion_type": "title"},
        "description": {"notion_property": "Description", "notion_type": "rich_text"},
        "status": {"notion_property": "Status", "notion_type": "select"},
    },
}

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default=None):
    _ensure_data_dir()
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def _write_json(path: Path, data):
    _ensure_data_dir()
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _load_sync_state() -> dict:
    return _read_json(SYNC_STATE_FILE, {})


def _save_sync_state(state: dict):
    _write_json(SYNC_STATE_FILE, state)


def _load_mappings() -> dict:
    return _read_json(MAPPINGS_FILE, DEFAULT_MAPPINGS)


def _save_mappings(mappings: dict):
    _write_json(MAPPINGS_FILE, mappings)


def _load_sync_log() -> list:
    return _read_json(SYNC_LOG_FILE, [])


def _append_sync_log(entry: dict):
    log = _load_sync_log()
    log.insert(0, entry)
    _write_json(SYNC_LOG_FILE, log[:500])


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------


def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("notion-sync").get(key, default)


def _get_api_key() -> str | None:
    return _get_setting("notion_api_key")


def _get_database_id() -> str | None:
    return _get_setting("default_database_id")


def _notion_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Entity fetch helper
# ---------------------------------------------------------------------------


async def _fetch_entity(entity_type: str, entity_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND_URL}/api/entity/{entity_type}/{entity_id}")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch entity {entity_type}/{entity_id}",
            )
        return resp.json()


async def _fetch_all_entities(entity_type: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{BACKEND_URL}/api/{entity_type}s")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch entities of type {entity_type}",
            )
        data = resp.json()
        # Handle both list and dict with items key
        if isinstance(data, list):
            return data
        return data.get("items", data.get("entities", []))


# ---------------------------------------------------------------------------
# Notion API helpers
# ---------------------------------------------------------------------------


def _build_notion_properties(entity: dict, entity_type: str, mappings: dict) -> dict:
    """Convert entity fields to Notion page properties based on mappings."""
    type_mappings = mappings.get(entity_type, {})
    properties = {}

    for studio_field, mapping in type_mappings.items():
        value = entity.get(studio_field)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue

        notion_prop = mapping["notion_property"]
        notion_type = mapping["notion_type"]

        if notion_type == "title":
            properties[notion_prop] = {
                "title": [{"text": {"content": str(value)[:2000]}}]
            }
        elif notion_type == "rich_text":
            properties[notion_prop] = {
                "rich_text": [{"text": {"content": str(value)[:2000]}}]
            }
        elif notion_type == "select":
            properties[notion_prop] = {
                "select": {"name": str(value)}
            }
        elif notion_type == "multi_select":
            items = [v.strip() for v in str(value).split(",") if v.strip()]
            properties[notion_prop] = {
                "multi_select": [{"name": item} for item in items]
            }
        elif notion_type == "number":
            try:
                properties[notion_prop] = {"number": float(value)}
            except (ValueError, TypeError):
                pass
        elif notion_type == "checkbox":
            properties[notion_prop] = {"checkbox": bool(value)}
        elif notion_type == "url":
            properties[notion_prop] = {"url": str(value)}

    return properties


async def _create_notion_page(api_key: str, database_id: str, properties: dict) -> dict:
    """Create a new page in a Notion database."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{NOTION_API_BASE}/pages",
            headers=_notion_headers(api_key),
            json={
                "parent": {"database_id": database_id},
                "properties": properties,
            },
        )
        if resp.status_code not in (200, 201):
            detail = resp.json().get("message", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            raise HTTPException(status_code=502, detail=f"Notion API error: {detail}")
        return resp.json()


async def _update_notion_page(api_key: str, page_id: str, properties: dict) -> dict:
    """Update an existing Notion page."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.patch(
            f"{NOTION_API_BASE}/pages/{page_id}",
            headers=_notion_headers(api_key),
            json={"properties": properties},
        )
        if resp.status_code != 200:
            detail = resp.json().get("message", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            raise HTTPException(status_code=502, detail=f"Notion API error: {detail}")
        return resp.json()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class SyncRequest(BaseModel):
    database_id: Optional[str] = None


class SyncAllRequest(BaseModel):
    entity_type: str
    database_id: Optional[str] = None


class MappingUpdate(BaseModel):
    mappings: dict


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/")
async def index():
    """Plugin status with Notion connection check."""
    api_key = _get_api_key()
    database_id = _get_database_id()
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("notion-sync")
    sync_state = _load_sync_state()

    connected = False
    workspace_name = None

    if api_key:
        # Try a lightweight API call to verify the key
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(
                    f"{NOTION_API_BASE}/users/me",
                    headers=_notion_headers(api_key),
                )
                if resp.status_code == 200:
                    connected = True
                    data = resp.json()
                    workspace_name = data.get("name", "Connected")
        except Exception:
            pass

    # Count sync states
    total_synced = sum(1 for v in sync_state.values() if v.get("status") == "synced")
    total_pending = sum(1 for v in sync_state.values() if v.get("status") == "pending")
    total_error = sum(1 for v in sync_state.values() if v.get("status") == "error")

    return {
        "plugin": "notion-sync",
        "version": "0.2.0",
        "status": "ok",
        "notion_connected": connected,
        "workspace_name": workspace_name,
        "api_key_configured": bool(api_key),
        "database_id_configured": bool(database_id),
        "auto_sync": settings.get("auto_sync", False),
        "sync_direction": settings.get("sync_direction", "studio_to_notion"),
        "sync_stats": {
            "synced": total_synced,
            "pending": total_pending,
            "error": total_error,
            "total_tracked": len(sync_state),
        },
    }


@router.post("/sync/{entity_type}/{entity_id}")
async def sync_entity(entity_type: str, entity_id: str, req: SyncRequest = SyncRequest()):
    """Sync a single entity to Notion.

    Creates a new Notion page if not yet linked, or updates the existing one.
    """
    api_key = _get_api_key()
    if not api_key:
        return {
            "status": "not_configured",
            "message": "Notion API key not configured. Go to Settings > Plugins > Notion Sync to add your integration token.",
            "setup_url": "https://www.notion.so/my-integrations",
            "instructions": [
                "1. Visit notion.so/my-integrations and create a new integration",
                "2. Copy the Internal Integration Token",
                "3. Paste it in Studio Settings > Plugins > Notion Sync > Integration Token",
                "4. Share your Notion database with the integration",
            ],
        }

    database_id = req.database_id or _get_database_id()
    if not database_id:
        raise HTTPException(
            status_code=400,
            detail="No database ID configured. Set a default database in plugin settings or pass database_id in the request.",
        )

    # Fetch entity from Studio
    entity = await _fetch_entity(entity_type, entity_id)

    # Build Notion properties
    mappings = _load_mappings()
    properties = _build_notion_properties(entity, entity_type, mappings)

    if not properties:
        raise HTTPException(
            status_code=400,
            detail=f"No field mappings configured for entity type '{entity_type}'. Configure mappings on the Notion Sync page.",
        )

    # Check sync state for existing link
    sync_state = _load_sync_state()
    state_key = f"{entity_type}:{entity_id}"
    existing = sync_state.get(state_key)

    now = datetime.now(timezone.utc).isoformat()
    entity_name = entity.get("name") or entity.get("title") or entity.get("label") or entity_id

    try:
        if existing and existing.get("notion_page_id"):
            # Update existing page
            notion_page = await _update_notion_page(api_key, existing["notion_page_id"], properties)
            action = "updated"
        else:
            # Create new page
            notion_page = await _create_notion_page(api_key, database_id, properties)
            action = "created"

        page_id = notion_page["id"]
        page_url = notion_page.get("url", f"https://notion.so/{page_id.replace('-', '')}")

        # Update sync state
        sync_state[state_key] = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "notion_page_id": page_id,
            "notion_url": page_url,
            "database_id": database_id,
            "last_synced": now,
            "status": "synced",
            "error": None,
        }
        _save_sync_state(sync_state)

        # Log
        _append_sync_log({
            "id": str(uuid.uuid4()),
            "timestamp": now,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "notion_page_id": page_id,
            "success": True,
            "error": None,
        })

        return {
            "status": "synced",
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "notion_page_id": page_id,
            "notion_url": page_url,
            "synced_at": now,
        }

    except HTTPException:
        raise
    except Exception as exc:
        # Record error in state
        sync_state[state_key] = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "notion_page_id": existing.get("notion_page_id") if existing else None,
            "notion_url": existing.get("notion_url") if existing else None,
            "database_id": database_id,
            "last_synced": existing.get("last_synced") if existing else None,
            "status": "error",
            "error": str(exc),
        }
        _save_sync_state(sync_state)

        _append_sync_log({
            "id": str(uuid.uuid4()),
            "timestamp": now,
            "action": "sync_failed",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "notion_page_id": None,
            "success": False,
            "error": str(exc),
        })

        raise HTTPException(status_code=502, detail=f"Notion sync failed: {exc}")


@router.post("/sync-all")
async def sync_all(req: SyncAllRequest):
    """Sync all entities of a given type to Notion."""
    api_key = _get_api_key()
    if not api_key:
        return {
            "status": "not_configured",
            "message": "Notion API key not configured. Add your token in Settings > Plugins > Notion Sync.",
        }

    database_id = req.database_id or _get_database_id()
    if not database_id:
        raise HTTPException(status_code=400, detail="No database ID configured.")

    entities = await _fetch_all_entities(req.entity_type)
    results = {"synced": 0, "errors": 0, "total": len(entities), "details": []}

    for entity in entities:
        eid = entity.get("id") or entity.get("entity_id")
        if not eid:
            continue
        try:
            result = await sync_entity(req.entity_type, eid, SyncRequest(database_id=database_id))
            results["synced"] += 1
            results["details"].append({
                "entity_id": eid,
                "name": entity.get("name") or entity.get("title") or eid,
                "status": "synced",
            })
        except Exception as exc:
            results["errors"] += 1
            results["details"].append({
                "entity_id": eid,
                "name": entity.get("name") or entity.get("title") or eid,
                "status": "error",
                "error": str(exc),
            })

    return results


@router.get("/mappings")
async def get_mappings():
    """Get current field mapping configuration."""
    return {
        "mappings": _load_mappings(),
        "available_notion_types": [
            "title", "rich_text", "select", "multi_select",
            "number", "checkbox", "url", "date", "email", "phone_number",
        ],
    }


@router.put("/mappings")
async def update_mappings(req: MappingUpdate):
    """Update field mapping configuration."""
    _save_mappings(req.mappings)
    return {"status": "ok", "message": "Mappings updated", "mappings": req.mappings}


@router.get("/status/{entity_type}/{entity_id}")
async def get_sync_status(entity_type: str, entity_id: str):
    """Get sync status for a specific entity."""
    sync_state = _load_sync_state()
    state_key = f"{entity_type}:{entity_id}"
    state = sync_state.get(state_key)

    if not state:
        return {
            "status": "not_linked",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "notion_page_id": None,
            "notion_url": None,
            "last_synced": None,
            "error": None,
        }

    return state


@router.get("/databases")
async def list_databases():
    """List Notion databases accessible by the integration.

    Returns mock data with setup instructions when no API key is configured.
    """
    api_key = _get_api_key()
    if not api_key:
        return {
            "status": "not_configured",
            "databases": [],
            "message": "Notion API key not configured. Add your integration token in Settings > Plugins > Notion Sync.",
            "setup_instructions": {
                "step_1": "Go to notion.so/my-integrations",
                "step_2": "Create a new internal integration",
                "step_3": "Copy the token and paste it in plugin settings",
                "step_4": "Share your Notion database with the integration (click ... menu > Connections > your integration)",
            },
        }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{NOTION_API_BASE}/search",
                headers=_notion_headers(api_key),
                json={
                    "filter": {"property": "object", "value": "database"},
                    "page_size": 50,
                },
            )
            if resp.status_code != 200:
                detail = resp.text[:200]
                raise HTTPException(status_code=502, detail=f"Notion API error: {detail}")

            data = resp.json()
            databases = []
            for db in data.get("results", []):
                title_parts = db.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_parts) or "Untitled"
                databases.append({
                    "id": db["id"],
                    "title": title,
                    "url": db.get("url", ""),
                    "created_time": db.get("created_time"),
                    "last_edited_time": db.get("last_edited_time"),
                    "property_count": len(db.get("properties", {})),
                    "properties": {
                        name: {"type": prop.get("type")}
                        for name, prop in db.get("properties", {}).items()
                    },
                })

            return {
                "status": "ok",
                "databases": databases,
                "total": len(databases),
            }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to list Notion databases: {exc}")


@router.get("/sync-log")
async def get_sync_log(limit: int = Query(50, ge=1, le=200)):
    """Get recent sync activity log."""
    log = _load_sync_log()
    return {
        "total": len(log),
        "items": log[:limit],
    }


@router.get("/overview")
async def sync_overview():
    """Get an overview of all sync states, grouped by entity type."""
    sync_state = _load_sync_state()
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("notion-sync")
    entity_types_str = settings.get("sync_entity_types", "character,location")
    entity_types = [t.strip() for t in entity_types_str.split(",") if t.strip()]

    overview = {}
    for et in entity_types:
        type_states = {
            k: v for k, v in sync_state.items() if v.get("entity_type") == et
        }
        overview[et] = {
            "total": len(type_states),
            "synced": sum(1 for v in type_states.values() if v.get("status") == "synced"),
            "pending": sum(1 for v in type_states.values() if v.get("status") == "pending"),
            "error": sum(1 for v in type_states.values() if v.get("status") == "error"),
            "not_linked": sum(1 for v in type_states.values() if v.get("status") == "not_linked"),
        }

    return {
        "entity_types": entity_types,
        "overview": overview,
        "total_tracked": len(sync_state),
    }
