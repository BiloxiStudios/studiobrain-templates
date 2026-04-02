"""
UEFN Exporter Plugin — Event Handlers.

Listens for entity lifecycle events and logs export-relevant activity.
When auto-sync settings are enabled, entity updates can trigger
regeneration of Verse files in the UEFN project directory.
"""

import logging

logger = logging.getLogger("plugin.uefn-exporter")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Register event listeners for entity lifecycle events.
    """

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Log when new entities are created that could be exported."""
        entity_type = getattr(event, "entity_type", "?")
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[uefn-exporter] New entity created: %s/%s — available for UEFN export",
            entity_type, entity_id,
        )

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Log entity updates. When island_metadata_sync is enabled, flag for re-export."""
        entity_type = getattr(event, "entity_type", "?")
        entity_id = getattr(event, "entity_id", "?")
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("uefn-exporter")

        if settings.get("island_metadata_sync", False):
            logger.info(
                "[uefn-exporter] Entity updated with sync enabled: %s/%s — "
                "island metadata may need refresh",
                entity_type, entity_id,
            )
        else:
            logger.debug(
                "[uefn-exporter] Entity updated: %s/%s",
                entity_type, entity_id,
            )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Log when entities are deleted to flag stale Verse exports."""
        entity_type = getattr(event, "entity_type", "?")
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[uefn-exporter] Entity deleted: %s/%s — exported Verse files may be stale",
            entity_type, entity_id,
        )
