"""
Production Kanban Plugin — event handlers.

Listens for entity status changes and logs production pipeline transitions.
"""

import logging

logger = logging.getLogger("plugin.kanban-board")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers listeners for entity lifecycle events to track
    production status transitions on the kanban board.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Log when an entity is updated — may include status changes."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        changes = getattr(event, "changes", {})

        # Check if the status field was part of the update
        if isinstance(changes, dict) and "status" in changes:
            old_status = changes["status"].get("old", "none")
            new_status = changes["status"].get("new", "none")
            logger.info(
                "[kanban-board] Status transition: %s/%s — %s -> %s",
                entity_type,
                entity_id,
                old_status,
                new_status,
            )
        else:
            logger.debug(
                "[kanban-board] Entity updated: %s/%s",
                entity_type,
                entity_id,
            )

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Log when a new entity is created — it enters the first column."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        logger.info(
            "[kanban-board] New entity enters board: %s/%s (column: Concept)",
            entity_type,
            entity_id,
        )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Log when an entity is removed from the board."""
        entity_type = getattr(event, "entity_type", "unknown")
        entity_id = getattr(event, "entity_id", "unknown")
        logger.info(
            "[kanban-board] Entity removed from board: %s/%s",
            entity_type,
            entity_id,
        )
