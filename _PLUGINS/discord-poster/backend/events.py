"""
Discord Poster Plugin — event handlers.

Listens for entity.created and entity.updated events on the backend
event bus.  When auto-post is enabled in plugin settings the handler
automatically posts a Discord embed for the affected entity.
"""

import logging

logger = logging.getLogger("plugin.discord-poster")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity lifecycle events.
    """

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Auto-post to Discord when a new entity is created (if enabled)."""
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("discord-poster")
        if not settings.get("auto_post_on_create", False):
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            logger.warning("[discord-poster] entity.created event missing type/id")
            return

        logger.info(
            "[discord-poster] Auto-posting new entity: %s/%s",
            entity_type,
            entity_id,
        )

        await _auto_post(entity_type, entity_id, action="created")

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Auto-post to Discord when an entity is updated (if enabled)."""
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("discord-poster")
        if not settings.get("auto_post_on_update", False):
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            logger.warning("[discord-poster] entity.updated event missing type/id")
            return

        logger.info(
            "[discord-poster] Auto-posting updated entity: %s/%s",
            entity_type,
            entity_id,
        )

        await _auto_post(entity_type, entity_id, action="updated")


async def _auto_post(entity_type: str, entity_id: str, action: str = "created"):
    """
    Perform an auto-post by calling the plugin's own /post endpoint logic.
    We import from routes to reuse the embed building and posting logic.
    """
    try:
        from backend.routes import (
            _fetch_entity,
            _build_embed,
            _post_to_discord,
            _get_webhooks,
            data_svc,
        )
        import uuid
        from datetime import datetime, timezone

        webhooks = _get_webhooks()
        if not webhooks:
            logger.warning("[discord-poster] Auto-post skipped — no webhooks configured")
            return

        entity = await _fetch_entity(entity_type, entity_id)
        entity_name = entity.get("name") or entity.get("title") or "Unknown"

        message = f"Entity {action}: **{entity_name}**" if action else None
        embed = _build_embed(entity, entity_type, entity_id, message=message, include_image=True)

        # Post to default (first) webhook
        webhook = webhooks[0]
        result = await _post_to_discord(webhook["url"], embed)

        history_entry = {
            "id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "webhook_name": webhook["name"],
            "webhook_url": webhook["url"][:60] + "...",
            "message": f"[Auto] Entity {action}",
            "include_image": True,
            "success": result["success"],
            "status_code": result["status_code"],
            "error": result.get("detail"),
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }
        data_svc.create(
            record_type="post_history",
            data=history_entry,
            entity_type=entity_type,
            entity_id=entity_id,
            record_id=history_entry["id"],
        )

        if result["success"]:
            logger.info("[discord-poster] Auto-post successful for %s/%s", entity_type, entity_id)
        else:
            logger.error(
                "[discord-poster] Auto-post failed for %s/%s: %s",
                entity_type,
                entity_id,
                result.get("detail"),
            )

    except Exception:
        logger.exception("[discord-poster] Auto-post error for %s/%s", entity_type, entity_id)
