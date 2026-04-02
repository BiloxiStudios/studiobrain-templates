"""
Showrunner Exporter Plugin -- event handlers.

Listens for entity changes and optionally auto-syncs character data
to Showrunner.xyz when auto_sync is enabled in plugin settings.
"""

import logging

logger = logging.getLogger("plugin.showrunner-exporter")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity lifecycle events relevant to
    Showrunner synchronization.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Auto-export to Showrunner when an entity is updated (if enabled)."""
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("showrunner-exporter")
        if not settings.get("auto_sync", False):
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            logger.warning("[showrunner-exporter] entity.updated event missing type/id")
            return

        # Only auto-sync supported types
        if entity_type not in ("character", "location", "faction"):
            return

        logger.info(
            "[showrunner-exporter] Auto-sync triggered for %s/%s",
            entity_type,
            entity_id,
        )

        await _auto_export(entity_type, entity_id)

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Log when a new entity is created for tracking purposes."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        logger.info(
            "[showrunner-exporter] New entity available for export: %s/%s",
            entity_type,
            entity_id,
        )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Log when an entity is deleted -- may need cleanup in Showrunner."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        logger.warning(
            "[showrunner-exporter] Entity deleted: %s/%s -- "
            "Showrunner data may need manual cleanup",
            entity_type,
            entity_id,
        )


async def _auto_export(entity_type: str, entity_id: str):
    """
    Perform an auto-export by calling the plugin's own export logic.
    Reuses route functions to avoid code duplication.
    """
    try:
        from backend.routes import (
            _fetch_entity,
            entity_to_showrunner,
            _get_api_key,
            _get_project_id,
            _get_api_url,
            _append_export_log,
        )
        import httpx
        import uuid
        from datetime import datetime, timezone

        api_key = _get_api_key()
        project_id = _get_project_id()

        if not api_key or not project_id:
            logger.info(
                "[showrunner-exporter] Auto-sync skipped -- API key or project ID not configured"
            )
            return

        entity_data = await _fetch_entity(entity_type, entity_id)
        showrunner_data = entity_to_showrunner(entity_data, entity_type)

        # Push to Showrunner
        pushed = False
        push_error = None
        try:
            api_url = _get_api_url()
            type_plural = entity_type + "s"
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{api_url}/v1/projects/{project_id}/{type_plural}",
                    json=showrunner_data,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                )
                pushed = resp.status_code in (200, 201)
                if not pushed:
                    push_error = f"API returned {resp.status_code}"
        except httpx.RequestError as exc:
            push_error = str(exc)

        log_entry = {
            "id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": showrunner_data.get("name", "Unknown"),
            "action": "auto_sync",
            "success": True,
            "pushed_to_showrunner": pushed,
            "push_error": push_error,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
        _append_export_log(log_entry)

        if pushed:
            logger.info(
                "[showrunner-exporter] Auto-sync successful for %s/%s",
                entity_type, entity_id,
            )
        else:
            logger.error(
                "[showrunner-exporter] Auto-sync push failed for %s/%s: %s",
                entity_type, entity_id, push_error,
            )

    except Exception:
        logger.exception(
            "[showrunner-exporter] Auto-export error for %s/%s",
            entity_type, entity_id,
        )
