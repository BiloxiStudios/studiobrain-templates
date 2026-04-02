"""
Blender Bridge Plugin -- event handlers.

Listens for entity update events and auto-exports to Blender
if the auto_export setting is enabled.
"""

import json
import logging
import time
import uuid
from pathlib import Path

logger = logging.getLogger("plugin.blender-bridge")

BRAINS_ROOT = Path("A:/Brains")
PLUGIN_DATA = Path("A:/Brains/_Plugins/blender-bridge/data")
EXPORTS_DIR = PLUGIN_DATA / "exports"
EXPORT_LOG_FILE = PLUGIN_DATA / "export_log.json"


def _is_auto_export_enabled() -> bool:
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("blender-bridge").get("auto_export", False)


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity events relevant to Blender export.
    """

    @event_bus.on("entity.character.updated")
    async def on_character_updated(event):
        """Auto-export character to Blender on update."""
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[blender-bridge] Character updated: %s",
            entity_id,
        )
        if _is_auto_export_enabled():
            logger.info(
                "[blender-bridge] Auto-export triggered for character %s",
                entity_id,
            )
            await _auto_export("character", entity_id)

    @event_bus.on("entity.location.updated")
    async def on_location_updated(event):
        """Auto-export location to Blender on update."""
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[blender-bridge] Location updated: %s",
            entity_id,
        )
        if _is_auto_export_enabled():
            logger.info(
                "[blender-bridge] Auto-export triggered for location %s",
                entity_id,
            )
            await _auto_export("location", entity_id)

    @event_bus.on("entity.item.updated")
    async def on_item_updated(event):
        """Auto-export item to Blender on update."""
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[blender-bridge] Item updated: %s",
            entity_id,
        )
        if _is_auto_export_enabled():
            logger.info(
                "[blender-bridge] Auto-export triggered for item %s",
                entity_id,
            )
            await _auto_export("item", entity_id)

    @event_bus.on("entity.*.deleted")
    async def on_entity_deleted(event):
        """Log when an entity is deleted that may have Blender exports."""
        entity_type = getattr(event, "entity_type", "?")
        entity_id = getattr(event, "entity_id", "?")
        logger.warning(
            "[blender-bridge] Entity deleted: %s/%s -- existing Blender exports may be stale",
            entity_type,
            entity_id,
        )

    @event_bus.on("plugin.blender-bridge.*")
    async def on_plugin_event(event):
        """Log internal plugin events."""
        logger.info(
            "[blender-bridge] Plugin event: %s",
            getattr(event, "event_type", "unknown"),
        )


async def _auto_export(entity_type: str, entity_id: str):
    """
    Perform an automatic export of an entity when auto_export is enabled.
    This imports route helpers at call time to avoid circular imports.
    """
    try:
        from backend.routes import (
            _get_entity_file,
            _parse_frontmatter,
            entity_to_blender_data,
            _blender_url,
        )
        import os
        import aiohttp

        filepath = _get_entity_file(entity_type, entity_id)
        if not os.path.isfile(filepath):
            logger.warning("[blender-bridge] Auto-export: entity file not found: %s", filepath)
            return

        fm = _parse_frontmatter(filepath)
        blender_data = entity_to_blender_data(entity_type, entity_id, fm)

        # Save export file
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        short_id = uuid.uuid4().hex[:8]
        export_filename = f"{entity_type}_{entity_id}_{ts}_{short_id}.json"
        export_path = EXPORTS_DIR / export_filename
        export_path.write_text(
            json.dumps(blender_data, indent=2, default=str),
            encoding="utf-8",
        )

        # Try to push to Blender
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{_blender_url()}/import",
                    json=blender_data,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        logger.info("[blender-bridge] Auto-exported %s/%s to Blender", entity_type, entity_id)
                    else:
                        logger.warning("[blender-bridge] Blender returned %d for auto-export", resp.status)
        except Exception as exc:
            logger.debug("[blender-bridge] Could not push auto-export to Blender: %s", exc)

        # Log
        log_file = EXPORT_LOG_FILE
        log = []
        try:
            if log_file.exists():
                log = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        log.append({
            "timestamp": ts,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "name": blender_data.get("name", entity_id),
            "filename": export_filename,
            "auto_export": True,
            "sent_to_blender": False,
        })
        log_file.write_text(json.dumps(log[-500:], indent=2, default=str), encoding="utf-8")

    except Exception as exc:
        logger.error("[blender-bridge] Auto-export failed for %s/%s: %s", entity_type, entity_id, exc)
