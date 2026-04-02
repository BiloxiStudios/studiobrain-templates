"""
PDF Bible Exporter — Event Handlers

Logs export-related events for analytics and audit tracking.
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# In-memory export log (most recent 100 exports)
_export_log = []
MAX_LOG_SIZE = 100


def log_export_event(event_type: str, entity_type: str = "",
                     entity_id: str = "", template: str = "",
                     count: int = 1, details: str = ""):
    """Record an export event."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "template": template,
        "count": count,
        "details": details,
    }
    _export_log.append(entry)
    if len(_export_log) > MAX_LOG_SIZE:
        _export_log.pop(0)

    logger.info(
        "PDF Export [%s]: %s/%s (template=%s, count=%d)",
        event_type, entity_type, entity_id, template, count,
    )


def get_export_log():
    """Return the recent export log."""
    return list(reversed(_export_log))


def register_handlers(event_bus: Any, model_registry: Any = None):
    """
    Register event handlers with the platform event bus.
    Called by the plugin loader at startup.
    """
    logger.info("PDF Exporter event handlers registered")

    # Listen for entity export events if the bus supports it
    if hasattr(event_bus, "on"):
        @event_bus.on("entity.exported")
        def on_entity_exported(data: dict):
            log_export_event(
                event_type="single",
                entity_type=data.get("entity_type", ""),
                entity_id=data.get("entity_id", ""),
                template=data.get("template", ""),
            )

        @event_bus.on("batch.exported")
        def on_batch_exported(data: dict):
            log_export_event(
                event_type="batch",
                entity_type=data.get("entity_type", ""),
                count=data.get("count", 0),
                template=data.get("template", ""),
            )
