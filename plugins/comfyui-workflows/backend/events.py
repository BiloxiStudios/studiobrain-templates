"""
ComfyUI Workflow Manager Plugin -- event handlers.

Listens for entity events to auto-track which entities have had
workflows executed against them.
"""

import logging

logger = logging.getLogger("plugin.comfyui-workflows")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Register event listeners for the ComfyUI workflow plugin.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Log entity updates that might trigger workflow re-runs."""
        logger.debug(
            "[comfyui-workflows] Entity updated: %s/%s",
            getattr(event, "entity_type", "?"),
            getattr(event, "entity_id", "?"),
        )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Clean up workflow outputs when an entity is deleted."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if entity_type and entity_id:
            logger.info(
                "[comfyui-workflows] Entity deleted: %s/%s — outputs may be orphaned",
                entity_type,
                entity_id,
            )
