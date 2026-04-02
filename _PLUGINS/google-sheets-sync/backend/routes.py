"""
Google Sheets Sync Plugin — backend routes.

Provides endpoints for exporting entity data to CSV/JSON, previewing
spreadsheet data, managing field-to-column mappings, and triggering
full syncs. When Google credentials are not configured, CSV export
serves as the fallback workflow.

All persistent state is stored in data/sync_state.json.
"""

import csv
import io
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger("plugin.google-sheets-sync")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
STATE_FILE = DATA_DIR / "sync_state.json"
MAPPING_FILE = DATA_DIR / "field_mapping.json"

BACKEND_API = "http://localhost:8201/api"

# Known entity types and their API plural forms + standard fields
ENTITY_REGISTRY = {
    "character": {
        "plural": "characters",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "location": {
        "plural": "locations",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "item": {
        "plural": "items",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "brand": {
        "plural": "brands",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "district": {
        "plural": "districts",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "faction": {
        "plural": "factions",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "job": {
        "plural": "jobs",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "quest": {
        "plural": "quests",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "event": {
        "plural": "events",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "campaign": {
        "plural": "campaigns",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
    "assembly": {
        "plural": "assemblies",
        "default_fields": ["id", "name", "status", "description", "tags"],
    },
}


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_state() -> dict:
    """Read the sync state file, creating it if needed."""
    _ensure_data_dir()
    if not STATE_FILE.exists():
        initial = {
            "last_sync": None,
            "sync_history": [],
            "entity_row_map": {},
            "spreadsheet_id": None,
        }
        STATE_FILE.write_text(json.dumps(initial, indent=2))
        return initial
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_state(state: dict) -> None:
    _ensure_data_dir()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def _read_mapping() -> dict:
    """Read field-to-column mappings."""
    _ensure_data_dir()
    if not MAPPING_FILE.exists():
        default_mapping = {}
        for etype, info in ENTITY_REGISTRY.items():
            default_mapping[etype] = {
                field: {
                    "column": field.replace("_", " ").title(),
                    "enabled": True,
                    "order": idx,
                }
                for idx, field in enumerate(info["default_fields"])
            }
        MAPPING_FILE.write_text(json.dumps(default_mapping, indent=2))
        return default_mapping
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_mapping(mapping: dict) -> None:
    _ensure_data_dir()
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)


def _add_sync_log(state: dict, action: str, entity_type: str = "",
                  detail: str = "", status: str = "ok", count: int = 0) -> None:
    """Append an entry to the sync history log."""
    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "entity_type": entity_type,
        "detail": detail,
        "status": status,
        "count": count,
    }
    state.setdefault("sync_history", []).insert(0, entry)
    # Keep last 100 entries
    state["sync_history"] = state["sync_history"][:100]


# ---------------------------------------------------------------------------
# Internal: fetch entities from the studio backend
# ---------------------------------------------------------------------------

async def _fetch_entities(entity_type: str) -> List[Dict[str, Any]]:
    """Fetch all entities of a given type from the studio backend API."""
    import httpx

    registry = ENTITY_REGISTRY.get(entity_type)
    if not registry:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    plural = registry["plural"]
    url = f"{BACKEND_API}/{plural}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            # The API may return a list directly or wrapped in a key
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # Try common wrapper keys
                for key in [plural, "items", "data", "results", "entities"]:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                return [data]
            return []
    except httpx.HTTPStatusError as exc:
        logger.error("Failed to fetch %s: HTTP %s", entity_type, exc.response.status_code)
        raise HTTPException(
            status_code=502,
            detail=f"Backend API error fetching {entity_type}: HTTP {exc.response.status_code}",
        )
    except httpx.RequestError as exc:
        logger.error("Failed to connect to backend for %s: %s", entity_type, exc)
        raise HTTPException(
            status_code=502,
            detail=f"Cannot reach backend API: {exc}",
        )


def _flatten_entity(entity: dict, fields: List[str]) -> dict:
    """Extract and flatten the requested fields from an entity dict."""
    row = {}
    for field in fields:
        value = entity.get(field, "")
        # Flatten lists/dicts to JSON strings for spreadsheet compatibility
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        elif value is None:
            value = ""
        row[field] = value
    return row


def _get_enabled_fields(entity_type: str) -> List[str]:
    """Return the ordered list of enabled fields for an entity type."""
    mapping = _read_mapping()
    type_map = mapping.get(entity_type, {})
    if not type_map:
        registry = ENTITY_REGISTRY.get(entity_type, {})
        return registry.get("default_fields", ["id", "name"])
    enabled = {
        field: info
        for field, info in type_map.items()
        if info.get("enabled", True)
    }
    sorted_fields = sorted(enabled.items(), key=lambda x: x[1].get("order", 999))
    return [f for f, _ in sorted_fields]


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class MappingUpdate(BaseModel):
    mapping: Dict[str, Dict[str, Any]]


class SyncRequest(BaseModel):
    entity_types: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status and sync overview."""
    state = _read_state()
    mapping = _read_mapping()

    return {
        "plugin": "google-sheets-sync",
        "version": "0.1.0",
        "status": "ok",
        "last_sync": state.get("last_sync"),
        "configured_types": list(mapping.keys()),
        "total_sync_events": len(state.get("sync_history", [])),
        "spreadsheet_id": state.get("spreadsheet_id"),
    }


@router.post("/export/{entity_type}")
async def export_entities(entity_type: str, format: str = Query("csv", regex="^(csv|json)$")):
    """
    Export all entities of a given type.

    Returns CSV (default) or JSON. This is the primary fallback when Google
    API credentials are not configured -- users can download and paste into
    their spreadsheet manually.
    """
    if entity_type not in ENTITY_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    entities = await _fetch_entities(entity_type)
    fields = _get_enabled_fields(entity_type)
    rows = [_flatten_entity(e, fields) for e in entities]

    # Update sync state
    state = _read_state()
    _add_sync_log(state, "export", entity_type,
                  f"Exported {len(rows)} {entity_type}(s) as {format.upper()}",
                  count=len(rows))
    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    _write_state(state)

    if format == "json":
        return {
            "entity_type": entity_type,
            "fields": fields,
            "count": len(rows),
            "rows": rows,
        }

    # CSV response
    output = io.StringIO()
    mapping = _read_mapping()
    type_map = mapping.get(entity_type, {})

    # Use column display names from mapping
    headers = []
    for field in fields:
        col_name = type_map.get(field, {}).get("column", field.replace("_", " ").title())
        headers.append(col_name)

    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row.get(f, "") for f in fields])

    output.seek(0)
    filename = f"{entity_type}s_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/preview/{entity_type}")
async def preview_entities(entity_type: str, limit: int = Query(50, ge=1, le=500)):
    """
    Preview entity data as it would appear in the spreadsheet.

    Returns the field mapping (columns) and the first N rows of data.
    """
    if entity_type not in ENTITY_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    entities = await _fetch_entities(entity_type)
    fields = _get_enabled_fields(entity_type)

    mapping = _read_mapping()
    type_map = mapping.get(entity_type, {})

    columns = []
    for field in fields:
        col_info = type_map.get(field, {})
        columns.append({
            "field": field,
            "column_name": col_info.get("column", field.replace("_", " ").title()),
            "enabled": col_info.get("enabled", True),
            "order": col_info.get("order", 999),
        })

    rows = [_flatten_entity(e, fields) for e in entities[:limit]]

    return {
        "entity_type": entity_type,
        "columns": columns,
        "total_entities": len(entities),
        "preview_count": len(rows),
        "rows": rows,
    }


@router.post("/sync")
async def sync_all(req: SyncRequest = None):
    """
    Trigger a full sync of all configured entity types.

    Without Google credentials, this collects all entity data and stores
    the snapshot in sync state for tracking purposes. With credentials,
    it would push to Google Sheets (implementation requires OAuth flow).
    """
    state = _read_state()
    mapping = _read_mapping()
    entity_types = (req.entity_types if req and req.entity_types
                    else list(mapping.keys()))

    results = {}
    total_count = 0

    for etype in entity_types:
        if etype not in ENTITY_REGISTRY:
            results[etype] = {"status": "skipped", "reason": f"Unknown type: {etype}"}
            continue

        try:
            entities = await _fetch_entities(etype)
            fields = _get_enabled_fields(etype)
            rows = [_flatten_entity(e, fields) for e in entities]

            # Store the entity-to-row index for the sidebar panel
            entity_row_map = state.setdefault("entity_row_map", {})
            for idx, row in enumerate(rows):
                eid = row.get("id", "")
                if eid:
                    entity_row_map[f"{etype}:{eid}"] = {
                        "sheet_tab": etype.title(),
                        "row_number": idx + 2,  # +1 header, +1 for 1-based
                        "last_synced": datetime.now(timezone.utc).isoformat(),
                        "fields_synced": len(fields),
                    }

            results[etype] = {
                "status": "ok",
                "count": len(rows),
                "fields": fields,
            }
            total_count += len(rows)

            _add_sync_log(state, "sync", etype,
                          f"Synced {len(rows)} entities with {len(fields)} fields",
                          count=len(rows))

        except HTTPException as exc:
            results[etype] = {"status": "error", "detail": exc.detail}
            _add_sync_log(state, "sync", etype, exc.detail, status="error")
        except Exception as exc:
            results[etype] = {"status": "error", "detail": str(exc)}
            _add_sync_log(state, "sync", etype, str(exc), status="error")

    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    _write_state(state)

    return {
        "status": "ok",
        "synced_types": len([r for r in results.values() if r.get("status") == "ok"]),
        "total_entities": total_count,
        "results": results,
        "timestamp": state["last_sync"],
    }


@router.get("/mapping")
async def get_mapping():
    """
    Return the current field-to-column mapping for all entity types.

    The mapping controls which entity fields appear as columns in the
    spreadsheet and their display names.
    """
    mapping = _read_mapping()
    return {
        "mapping": mapping,
        "available_types": list(ENTITY_REGISTRY.keys()),
    }


@router.put("/mapping")
async def update_mapping(req: MappingUpdate):
    """
    Update field-to-column mapping.

    Accepts a partial or full mapping dict keyed by entity type.
    Each field entry specifies { column, enabled, order }.
    """
    current = _read_mapping()

    for etype, fields in req.mapping.items():
        if etype not in ENTITY_REGISTRY:
            continue
        if etype not in current:
            current[etype] = {}
        for field, config in fields.items():
            if field not in current[etype]:
                current[etype][field] = {}
            current[etype][field].update(config)

    _write_mapping(current)

    state = _read_state()
    _add_sync_log(state, "mapping_update", "",
                  f"Updated mapping for: {', '.join(req.mapping.keys())}")
    _write_state(state)

    return {"status": "ok", "mapping": current}


@router.get("/state")
async def get_sync_state():
    """Return the full sync state including history and entity row map."""
    state = _read_state()
    return state


@router.get("/history")
async def get_sync_history(limit: int = Query(25, ge=1, le=100)):
    """Return the sync event log."""
    state = _read_state()
    history = state.get("sync_history", [])
    return {
        "total": len(history),
        "entries": history[:limit],
    }


@router.get("/entity-link/{entity_type}/{entity_id}")
async def get_entity_link(entity_type: str, entity_id: str):
    """
    Return the spreadsheet link info for a specific entity.

    Used by the entity-sidebar panel to show where this entity lives
    in the spreadsheet.
    """
    state = _read_state()
    key = f"{entity_type}:{entity_id}"
    row_map = state.get("entity_row_map", {})
    link_info = row_map.get(key)

    spreadsheet_id = state.get("spreadsheet_id")

    if link_info:
        sheet_url = None
        if spreadsheet_id:
            tab = link_info.get("sheet_tab", "")
            row = link_info.get("row_number", 1)
            sheet_url = (
                f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
                f"/edit#gid=0&range=A{row}"
            )

        return {
            "linked": True,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "sheet_tab": link_info.get("sheet_tab", ""),
            "row_number": link_info.get("row_number", 0),
            "last_synced": link_info.get("last_synced"),
            "fields_synced": link_info.get("fields_synced", 0),
            "sheet_url": sheet_url,
        }

    return {
        "linked": False,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "message": "Entity not yet synced to spreadsheet",
    }


@router.post("/set-spreadsheet")
async def set_spreadsheet(spreadsheet_id: str = Query(...)):
    """Store the target spreadsheet ID for linking."""
    state = _read_state()
    state["spreadsheet_id"] = spreadsheet_id
    _add_sync_log(state, "config", "", f"Spreadsheet ID set: {spreadsheet_id[:20]}...")
    _write_state(state)

    return {
        "status": "ok",
        "spreadsheet_id": spreadsheet_id,
        "sheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
    }


@router.delete("/clear-state")
async def clear_sync_state():
    """Reset all sync state. Useful for starting fresh."""
    initial = {
        "last_sync": None,
        "sync_history": [],
        "entity_row_map": {},
        "spreadsheet_id": None,
    }
    _write_state(initial)
    return {"status": "ok", "message": "Sync state cleared"}
