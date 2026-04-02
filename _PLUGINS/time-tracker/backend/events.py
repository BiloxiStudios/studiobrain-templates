"""
Time Tracker Plugin — event handlers.

Listens on the backend event bus for entity lifecycle events.
Logs entity edit activity that can be correlated with time entries.
In the future this could auto-start/stop timers based on entity navigation.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("plugin.time-tracker")

# In-memory log of recent entity events (kept small, used for diagnostics)
_recent_events: list[dict] = []
MAX_RECENT = 50


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers listeners for entity events that the time tracker can
    use for activity correlation and potential auto-timer behavior.
    """

    @event_bus.on("entity.*")
    async def on_entity_event(event):
        """Track entity lifecycle events for activity correlation."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        event_type = getattr(event, "event_type", "unknown")

        logger.info(
            "[time-tracker] Entity event: %s — %s/%s",
            event_type,
            entity_type or "?",
            entity_id or "?",
        )

        # Keep a small rolling log of recent events
        _recent_events.append({
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Trim to last N events
        while len(_recent_events) > MAX_RECENT:
            _recent_events.pop(0)


def get_recent_events() -> list[dict]:
    """Return the recent event log (can be called by routes if needed)."""
    return list(_recent_events)
