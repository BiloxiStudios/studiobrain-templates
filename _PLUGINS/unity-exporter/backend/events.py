"""
Unity Game Exporter Plugin — Event Handlers

Listens for entity lifecycle events and logs export-related activity.
When entities are created, updated, or exported, the handler records
events in the plugin's export log for the dashboard and sidebar display.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("plugin.unity-exporter")

BRAINS_ROOT = Path(r"A:\Brains")
LOG_FILE = BRAINS_ROOT / "_Plugins" / "unity-exporter" / "_export_log.json"
MAX_LOG_ENTRIES = 200


def _read_log() -> dict:
    """Read the export log file."""
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"exports": []}


def _write_log(data: dict):
    """Write the export log file, trimming to MAX_LOG_ENTRIES."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    exports = data.get("exports", [])
    if len(exports) > MAX_LOG_ENTRIES:
        exports = exports[-MAX_LOG_ENTRIES:]
    data["exports"] = exports
    LOG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def log_export_event(
    action: str,
    entity_type: str = "",
    entity_id: str = "",
    details: str = "",
    files: list = None,
):
    """Record an export event to the log file.

    Called by routes.py after successful exports, and by event handlers
    for entity lifecycle events.
    """
    log_data = _read_log()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details,
        "files": files or [],
    }
    log_data["exports"].append(entry)
    _write_log(log_data)
    logger.info(
        "[unity-exporter] Event logged: %s %s/%s — %s",
        action, entity_type, entity_id, details,
    )


def register_handlers(event_bus):
    """Register event handlers on the backend event bus.

    Called automatically by the plugin loader when the plugin is enabled.
    """

    @event_bus.on("entity.*")
    async def on_entity_event(event):
        """Log entity events that may affect exported Unity data."""
        event_type = getattr(event, "event_type", "unknown")
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)

        if not entity_type or not entity_id:
            return

        # Determine the action
        et_lower = event_type.lower()
        if "creat" in et_lower:
            action = "entity_created"
            details = f"New {entity_type} created — available for Unity export"
        elif "delet" in et_lower:
            action = "entity_deleted"
            details = f"{entity_type} deleted — exported .asset may be stale"
        elif "sav" in et_lower or "updat" in et_lower:
            action = "entity_updated"
            details = f"{entity_type} updated — re-export recommended"
        else:
            action = "entity_event"
            details = f"Event: {event_type}"

        logger.info(
            "[unity-exporter] %s — %s/%s",
            action, entity_type, entity_id,
        )

        # Log the event for the dashboard
        try:
            log_export_event(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            )
        except Exception as exc:
            logger.error("[unity-exporter] Failed to log event: %s", exc)
