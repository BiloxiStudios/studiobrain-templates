"""
Notion Sync Plugin — event handlers.

Listens for entity.updated events on the backend event bus.
When auto_sync is enabled in plugin settings, automatically syncs
the updated entity to Notion.
"""

import logging

logger = logging.getLogger("plugin.notion-sync")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity lifecycle events that trigger auto-sync.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Auto-sync entity to Notion when updated (if auto_sync is enabled)."""
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("notion-sync")
        if not settings.get("auto_sync", False):
            return

        # Check that API key is configured
        api_key = settings.get("notion_api_key")
        if not api_key:
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            logger.warning("[notion-sync] entity.updated event missing type/id")
            return

        # Check if this entity type is in the sync list
        sync_types_str = settings.get("sync_entity_types", "character,location")
        sync_types = [t.strip() for t in sync_types_str.split(",") if t.strip()]
        if entity_type not in sync_types:
            return

        logger.info(
            "[notion-sync] Auto-syncing updated entity: %s/%s",
            entity_type,
            entity_id,
        )

        await _auto_sync(entity_type, entity_id)

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Auto-sync entity to Notion when created (if auto_sync is enabled)."""
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("notion-sync")
        if not settings.get("auto_sync", False):
            return

        api_key = settings.get("notion_api_key")
        if not api_key:
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            logger.warning("[notion-sync] entity.created event missing type/id")
            return

        sync_types_str = settings.get("sync_entity_types", "character,location")
        sync_types = [t.strip() for t in sync_types_str.split(",") if t.strip()]
        if entity_type not in sync_types:
            return

        logger.info(
            "[notion-sync] Auto-syncing new entity: %s/%s",
            entity_type,
            entity_id,
        )

        await _auto_sync(entity_type, entity_id)


async def _auto_sync(entity_type: str, entity_id: str):
    """
    Perform an auto-sync by calling the plugin's own sync endpoint logic.
    Imports from routes to reuse the sync machinery.
    """
    try:
        from backend.routes import sync_entity, SyncRequest

        result = await sync_entity(entity_type, entity_id, SyncRequest())

        if isinstance(result, dict) and result.get("status") == "synced":
            logger.info(
                "[notion-sync] Auto-sync successful for %s/%s -> Notion page %s",
                entity_type,
                entity_id,
                result.get("notion_page_id", "?"),
            )
        else:
            logger.warning(
                "[notion-sync] Auto-sync returned non-synced status for %s/%s: %s",
                entity_type,
                entity_id,
                result,
            )

    except Exception:
        logger.exception(
            "[notion-sync] Auto-sync error for %s/%s",
            entity_type,
            entity_id,
        )
