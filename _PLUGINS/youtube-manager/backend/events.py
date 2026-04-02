"""
YouTube Manager Plugin - Event Handlers
Listens for platform events relevant to video management.
"""

import json
from pathlib import Path
from datetime import datetime

PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
EVENTS_LOG = DATA_DIR / "events.log"


def _log_event(event_type: str, payload: dict):
    """Append an event to the local event log."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "payload": payload,
    }
    with open(EVENTS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


# ---------------------------------------------------------------------------
# Event handlers – called by the platform event bus
# ---------------------------------------------------------------------------

async def on_entity_updated(entity_type: str, entity_id: str, changes: dict):
    """
    Fired when an entity is updated. Could trigger re-generation of video
    metadata if the entity name/description changed.
    """
    _log_event("entity_updated", {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "changed_fields": list(changes.keys()) if isinstance(changes, dict) else [],
    })


async def on_entity_deleted(entity_type: str, entity_id: str):
    """
    Fired when an entity is deleted. Logs the event; does NOT auto-remove
    YouTube videos (that would be destructive).
    """
    _log_event("entity_deleted", {
        "entity_type": entity_type,
        "entity_id": entity_id,
    })


async def on_plugin_enabled():
    """Called when the plugin is first enabled."""
    _log_event("plugin_enabled", {"plugin": "youtube-manager"})


async def on_plugin_disabled():
    """Called when the plugin is disabled."""
    _log_event("plugin_disabled", {"plugin": "youtube-manager"})


# ---------------------------------------------------------------------------
# Handler registry – the platform uses this dict to bind events
# ---------------------------------------------------------------------------
EVENT_HANDLERS = {
    "entity:updated": on_entity_updated,
    "entity:deleted": on_entity_deleted,
    "plugin:enabled": on_plugin_enabled,
    "plugin:disabled": on_plugin_disabled,
}
