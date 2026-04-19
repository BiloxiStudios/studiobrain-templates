"""
Social Publisher Plugin -- event handlers.

Listens for entity.created events on the backend event bus.
When auto-post is enabled in plugin settings the handler automatically
publishes a post for the new entity using the configured template.
"""

import logging

logger = logging.getLogger("plugin.social-publisher")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity lifecycle events.
    """

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Auto-post to social platforms when a new entity is created (if enabled)."""
        from services.plugin_settings_service import get_all_settings
        settings = get_all_settings("social-publisher")
        if not settings.get("auto_post_on_create", False):
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            logger.warning(
                "[social-publisher] entity.created event missing type/id"
            )
            return

        logger.info(
            "[social-publisher] Auto-posting new entity: %s/%s",
            entity_type,
            entity_id,
        )

        await _auto_post(entity_type, entity_id, settings)


async def _auto_post(entity_type: str, entity_id: str, settings: dict):
    """
    Auto-publish a new entity to all configured platforms using the
    configured template.
    """
    try:
        from backend.routes import (
            _fetch_entity,
            _get_entity_image_url,
            _render_template,
            _load_templates,
            _append_history,
            PUBLISHER_MAP,
            PLATFORMS,
        )
        import uuid
        from datetime import datetime, timezone

        entity = await _fetch_entity(entity_type, entity_id)
        entity_name = (
            entity.get("name") or entity.get("title") or "Unknown"
        )

        # Determine template
        template_id = settings.get("auto_post_template", "character-reveal")
        templates = _load_templates()
        template = next(
            (t for t in templates if t["id"] == template_id), None
        )
        if not template:
            template = templates[0] if templates else None
        if not template:
            logger.warning("[social-publisher] No templates available for auto-post")
            return

        # Build text
        hashtags = settings.get(
            "default_hashtags", "#CityOfBrains,#GameDev,#IndieGame"
        )
        hashtag_str = " ".join(
            h.strip() for h in hashtags.split(",") if h.strip()
        )
        text = _render_template(template["template"], entity, hashtag_str)

        # Image
        image_url = None
        if settings.get("auto_include_image", True):
            image_url = _get_entity_image_url(entity, entity_type, entity_id)

        # Publish to all configured platforms from the template
        target_platforms = template.get("platforms", list(PLATFORMS.keys()))
        for platform in target_platforms:
            publisher = PUBLISHER_MAP.get(platform)
            if not publisher:
                continue
            result = await publisher(text, image_url)

            history_entry = {
                "id": str(uuid.uuid4()),
                "platform": platform,
                "text": text,
                "image_url": image_url,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_name": entity_name,
                "template_id": template_id,
                "success": result.get("success", False),
                "mock": result.get("mock", False),
                "post_url": result.get("post_url"),
                "error": result.get("error"),
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "auto": True,
            }
            _append_history(history_entry)

            if result.get("success"):
                logger.info(
                    "[social-publisher] Auto-post to %s successful for %s/%s",
                    platform,
                    entity_type,
                    entity_id,
                )
            else:
                logger.error(
                    "[social-publisher] Auto-post to %s failed for %s/%s: %s",
                    platform,
                    entity_type,
                    entity_id,
                    result.get("error"),
                )

    except Exception:
        logger.exception(
            "[social-publisher] Auto-post error for %s/%s",
            entity_type,
            entity_id,
        )
