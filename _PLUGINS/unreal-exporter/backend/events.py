"""
Unreal Engine Exporter Plugin — event handlers.

Listens for entity lifecycle events and logs export-relevant activity.
Tracks which entities have been exported so the UI can show sync status.
"""

import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("plugin.unreal-exporter")

# Simple in-memory cache of export timestamps per entity
_export_log_path = os.path.join(os.path.dirname(__file__), "..", "exports", "_export_log.json")


def _load_export_log() -> dict:
    """Load the export log from disk."""
    try:
        with open(_export_log_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_export_log(log: dict):
    """Persist the export log to disk."""
    try:
        os.makedirs(os.path.dirname(_export_log_path), exist_ok=True)
        with open(_export_log_path, "w", encoding="utf-8") as fh:
            json.dump(log, fh, indent=2)
    except Exception as e:
        logger.warning("[unreal-exporter] Failed to save export log: %s", e)


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers listeners for entity lifecycle events to track
    which entities may need re-export to Unreal Engine.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """
        When an entity is updated, mark it as potentially out-of-sync
        with the last UE export.
        """
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")

        log = _load_export_log()
        key = f"{entity_type}/{entity_id}"

        if key in log:
            log[key]["dirty"] = True
            log[key]["last_modified"] = datetime.utcnow().isoformat() + "Z"
            _save_export_log(log)
            logger.info(
                "[unreal-exporter] Entity modified since last export: %s",
                key,
            )

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Log new entities that could be exported to UE."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        logger.info(
            "[unreal-exporter] New entity available for UE export: %s/%s",
            entity_type,
            entity_id,
        )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Remove deleted entities from the export log."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        key = f"{entity_type}/{entity_id}"

        log = _load_export_log()
        if key in log:
            del log[key]
            _save_export_log(log)
            logger.info(
                "[unreal-exporter] Removed deleted entity from export log: %s",
                key,
            )
