"""
Time Tracker Plugin — backend routes.

Provides endpoints for starting/stopping timers, managing time entries,
and generating time summaries. Completed time entries are persisted to the
database via PluginDataService; the active timer is held in-process memory.

SBAI-218: Migrated from file-based JSON to PluginDataService.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.plugin_data_service import PluginDataService

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PluginDataService instance — all DB work goes through this
# ---------------------------------------------------------------------------

data_svc = PluginDataService("time-tracker")

RECORD_TYPE = "time_entry"

# ---------------------------------------------------------------------------
# Active timer — ephemeral per-process state (not in DB)
# ---------------------------------------------------------------------------
# Format when set:
#   {
#       "id": "uuid",
#       "entity_type": "...",
#       "entity_id": "...",
#       "start_time": "ISO string",
#       "note": "",
#       "billable": True,
#   }
# When no timer is running: None

_active_timer: Optional[dict] = None


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class StartTimerRequest(BaseModel):
    entity_type: str
    entity_id: str
    note: Optional[str] = ""
    billable: Optional[bool] = True


class StopTimerResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    start_time: str
    end_time: str
    duration_seconds: int
    note: str
    billable: bool


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _stop_active_timer() -> dict:
    """
    Stop the in-memory active timer, persist the completed entry to the DB
    via PluginDataService, and return the entry dict shaped for the API.

    Raises ValueError if no timer is active (caller should guard).
    """
    global _active_timer

    if _active_timer is None:
        raise ValueError("No active timer")

    timer = _active_timer
    now = datetime.now(timezone.utc)
    start = datetime.fromisoformat(timer["start_time"])
    duration = max(int((now - start).total_seconds()), 0)

    end_time_iso = now.isoformat()

    # Persist to DB
    record = data_svc.create(
        record_type=RECORD_TYPE,
        data={
            "start_time": timer["start_time"],
            "end_time": end_time_iso,
            "duration_seconds": duration,
            "note": timer.get("note", ""),
            "billable": timer.get("billable", True),
        },
        entity_type=timer["entity_type"],
        entity_id=timer["entity_id"],
        record_id=timer["id"],
    )

    # Build the API-shaped entry from the DB record
    entry = _record_to_entry(record)

    # Clear the active timer
    _active_timer = None

    return entry


def _record_to_entry(record: dict) -> dict:
    """
    Convert a PluginDataService record dict into the flat entry shape
    the API has always returned.  This keeps the public contract stable.
    """
    data = record.get("data", {})
    return {
        "id": record["id"],
        "entity_type": record.get("entity_type", ""),
        "entity_id": record.get("entity_id", ""),
        "start_time": data.get("start_time", ""),
        "end_time": data.get("end_time", ""),
        "duration_seconds": data.get("duration_seconds", 0),
        "note": data.get("note", ""),
        "billable": data.get("billable", True),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status with active timer info."""
    result = data_svc.list(record_type=RECORD_TYPE, limit=0, offset=0)
    return {
        "plugin": "time-tracker",
        "version": "1.1.0",
        "status": "ok",
        "total_entries": result["total"],
        "active_timer": _active_timer,
    }


@router.post("/start")
async def start_timer(req: StartTimerRequest):
    """
    Start a new timer for the given entity.

    If a timer is already running, it will be stopped first and that
    completed entry will be returned alongside the new active timer.
    """
    global _active_timer
    stopped_entry = None

    # Auto-stop any currently running timer
    if _active_timer is not None:
        stopped_entry = _stop_active_timer()

    now = datetime.now(timezone.utc).isoformat()
    _active_timer = {
        "id": str(uuid.uuid4()),
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "start_time": now,
        "note": req.note or "",
        "billable": req.billable if req.billable is not None else True,
    }

    return {
        "active_timer": _active_timer,
        "stopped_entry": stopped_entry,
    }


@router.post("/stop")
async def stop_timer():
    """Stop the currently active timer and persist the completed entry."""
    if _active_timer is None:
        raise HTTPException(status_code=404, detail="No active timer to stop")

    entry = _stop_active_timer()
    return entry


@router.get("/active")
async def get_active_timer():
    """Return the currently running timer, or null if none."""
    return {"active_timer": _active_timer}


@router.get("/entries")
async def list_entries(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    since: Optional[str] = Query(None, description="ISO datetime -- return entries after this time"),
    until: Optional[str] = Query(None, description="ISO datetime -- return entries before this time"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    List completed time entries with optional filters.

    Results are returned newest-first.
    """
    # PluginDataService handles entity_type / entity_id filtering natively.
    # since / until require post-filtering on the data payload.
    result = data_svc.list(
        record_type=RECORD_TYPE,
        entity_type=entity_type,
        entity_id=entity_id,
        # Fetch a generous window; post-filter for time range.
        # If since/until are set we need all records to filter accurately.
        limit=10000 if (since or until) else limit,
        offset=0 if (since or until) else offset,
        order_desc=True,
    )

    entries = [_record_to_entry(r) for r in result["records"]]

    # Post-filter by time range
    if since:
        entries = [e for e in entries if e["start_time"] >= since]
    if until:
        entries = [e for e in entries if e["start_time"] <= until]

    total = len(entries)

    # Apply offset / limit after time-range filtering when we fetched all
    if since or until:
        entries = entries[offset: offset + limit]

    return {
        "entries": entries,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/summary")
async def get_summary(
    entity_type: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    until: Optional[str] = Query(None),
):
    """
    Time summary grouped by entity, with totals.

    Useful for reports and dashboards.
    """
    result = data_svc.list(
        record_type=RECORD_TYPE,
        entity_type=entity_type,
        limit=10000,
        offset=0,
        order_desc=False,
    )

    entries = [_record_to_entry(r) for r in result["records"]]

    if since:
        entries = [e for e in entries if e["start_time"] >= since]
    if until:
        entries = [e for e in entries if e["start_time"] <= until]

    # Group by entity
    by_entity: dict[str, dict] = {}
    total_seconds = 0
    total_billable_seconds = 0

    for entry in entries:
        key = f"{entry['entity_type']}:{entry['entity_id']}"
        if key not in by_entity:
            by_entity[key] = {
                "entity_type": entry["entity_type"],
                "entity_id": entry["entity_id"],
                "total_seconds": 0,
                "billable_seconds": 0,
                "entry_count": 0,
            }
        duration = entry.get("duration_seconds", 0)
        by_entity[key]["total_seconds"] += duration
        by_entity[key]["entry_count"] += 1
        total_seconds += duration
        if entry.get("billable"):
            by_entity[key]["billable_seconds"] += duration
            total_billable_seconds += duration

    # Group by entity_type for chart data
    by_type: dict[str, int] = {}
    for entry in entries:
        t = entry["entity_type"]
        by_type[t] = by_type.get(t, 0) + entry.get("duration_seconds", 0)

    # Sort entities by total time descending
    entities_sorted = sorted(by_entity.values(), key=lambda x: x["total_seconds"], reverse=True)

    return {
        "total_seconds": total_seconds,
        "total_billable_seconds": total_billable_seconds,
        "entry_count": len(entries),
        "by_entity": entities_sorted,
        "by_type": by_type,
    }


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str):
    """Delete a single time entry by ID (soft-delete)."""
    success = data_svc.delete(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"deleted": entry_id}


# ---------------------------------------------------------------------------
# Migration helper — import legacy time_entries.json into DB
# ---------------------------------------------------------------------------

LEGACY_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LEGACY_DATA_FILE = LEGACY_DATA_DIR / "time_entries.json"


def migrate_legacy_json(file_path: Optional[str] = None) -> dict:
    """
    Import entries from the old file-based time_entries.json into the DB.

    Can be called from a startup hook or manually via the /migrate endpoint.
    Skips records whose IDs already exist in the DB to make it idempotent.

    Args:
        file_path: Override path to the JSON file.  Defaults to the standard
                   ``data/time_entries.json`` next to the plugin root.

    Returns:
        {"imported": N, "skipped": N, "active_timer_found": bool}
    """
    path = Path(file_path) if file_path else LEGACY_DATA_FILE
    if not path.exists():
        return {"imported": 0, "skipped": 0, "active_timer_found": False}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read legacy JSON at %s: %s", path, exc)
        return {"imported": 0, "skipped": 0, "error": str(exc)}

    entries = raw.get("entries", [])
    active = raw.get("active_timer")
    imported = 0
    skipped = 0

    for entry in entries:
        rid = entry.get("id", str(uuid.uuid4()))

        # Check if already migrated
        existing = data_svc.get(rid)
        if existing is not None:
            skipped += 1
            continue

        data_svc.create(
            record_type=RECORD_TYPE,
            data={
                "start_time": entry.get("start_time", ""),
                "end_time": entry.get("end_time", ""),
                "duration_seconds": entry.get("duration_seconds", 0),
                "note": entry.get("note", ""),
                "billable": entry.get("billable", True),
            },
            entity_type=entry.get("entity_type", ""),
            entity_id=entry.get("entity_id", ""),
            record_id=rid,
        )
        imported += 1

    # Restore the active timer into memory if one was saved
    global _active_timer
    active_timer_found = active is not None
    if active and _active_timer is None:
        _active_timer = active
        logger.info("Restored active timer from legacy file: %s", active.get("id"))

    logger.info(
        "Legacy migration complete: %d imported, %d skipped, active_timer=%s",
        imported, skipped, active_timer_found,
    )

    return {
        "imported": imported,
        "skipped": skipped,
        "active_timer_found": active_timer_found,
    }


@router.post("/migrate")
async def run_migration(file_path: Optional[str] = None):
    """
    Manually trigger migration from the legacy time_entries.json file.

    This is idempotent — running it multiple times will not create duplicates.
    """
    result = migrate_legacy_json(file_path)
    return result
