"""
Google Sheets Sync Plugin — event handlers.

Listens for entity lifecycle events and triggers auto-sync when enabled.
Tracks entity changes to keep spreadsheet data current.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("plugin.google-sheets-sync")

PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
STATE_FILE = DATA_DIR / "sync_state.json"

# In-memory queue of pending sync operations
_pending_syncs: list[dict] = []
MAX_PENDING = 200


def _read_state_safe() -> dict:
    """Read sync state without raising on missing file."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"last_sync": None, "sync_history": [], "entity_row_map": {}}


def _write_state_safe(state: dict) -> None:
    """Write sync state without raising."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str)
    except Exception as exc:
        logger.error("[google-sheets-sync] Failed to write state: %s", exc)


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers listeners for entity events to trigger auto-sync
    when the auto_sync setting is enabled.
    """

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Track new entity creation for spreadsheet sync."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")

        logger.info(
            "[google-sheets-sync] Entity created: %s/%s — queued for sync",
            entity_type,
            entity_id,
        )

        _pending_syncs.append({
            "action": "create",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Trim queue
        while len(_pending_syncs) > MAX_PENDING:
            _pending_syncs.pop(0)

        # Update state to note this entity needs sync
        state = _read_state_safe()
        row_map = state.setdefault("entity_row_map", {})
        key = f"{entity_type}:{entity_id}"
        row_map[key] = {
            "sheet_tab": entity_type.title(),
            "row_number": 0,  # Will be assigned on next full sync
            "last_synced": None,
            "fields_synced": 0,
            "pending": True,
        }

        history = state.setdefault("sync_history", [])
        history.insert(0, {
            "id": entity_id[:8],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "auto_queue",
            "entity_type": entity_type,
            "detail": f"New {entity_type} '{entity_id}' queued for sync",
            "status": "pending",
            "count": 1,
        })
        state["sync_history"] = history[:100]
        _write_state_safe(state)

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Track entity updates for spreadsheet sync."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        changes = getattr(event, "changes", {})

        logger.info(
            "[google-sheets-sync] Entity updated: %s/%s — queued for sync",
            entity_type,
            entity_id,
        )

        changed_fields = []
        if isinstance(changes, dict):
            changed_fields = list(changes.keys())

        _pending_syncs.append({
            "action": "update",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "changed_fields": changed_fields,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while len(_pending_syncs) > MAX_PENDING:
            _pending_syncs.pop(0)

        # Mark as needing re-sync
        state = _read_state_safe()
        row_map = state.setdefault("entity_row_map", {})
        key = f"{entity_type}:{entity_id}"
        if key in row_map:
            row_map[key]["pending"] = True
            row_map[key]["last_change"] = datetime.now(timezone.utc).isoformat()
            if changed_fields:
                row_map[key]["changed_fields"] = changed_fields
        _write_state_safe(state)

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Track entity deletions to remove from spreadsheet."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")

        logger.info(
            "[google-sheets-sync] Entity deleted: %s/%s — marked for removal from sheet",
            entity_type,
            entity_id,
        )

        _pending_syncs.append({
            "action": "delete",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while len(_pending_syncs) > MAX_PENDING:
            _pending_syncs.pop(0)

        # Remove from row map
        state = _read_state_safe()
        row_map = state.setdefault("entity_row_map", {})
        key = f"{entity_type}:{entity_id}"
        if key in row_map:
            del row_map[key]

        history = state.setdefault("sync_history", [])
        history.insert(0, {
            "id": entity_id[:8],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "auto_remove",
            "entity_type": entity_type,
            "detail": f"Deleted {entity_type} '{entity_id}' removed from sync map",
            "status": "ok",
            "count": 1,
        })
        state["sync_history"] = history[:100]
        _write_state_safe(state)


def get_pending_syncs() -> list[dict]:
    """Return the current pending sync queue (can be called by routes)."""
    return list(_pending_syncs)


def clear_pending_syncs() -> int:
    """Clear the pending sync queue. Returns how many were cleared."""
    count = len(_pending_syncs)
    _pending_syncs.clear()
    return count
