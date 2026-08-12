"""
DEPRECATED — SBAI-6815: This plugin targets the decommissioned Python FastAPI backend.
The current production sb-server (Rust/Axum) only loads .wasm plugin components.

Migration path:
  - See plugins/MIGRATION_PLAN.md for the full migration strategy
  - See plugins/hello-world-wasm/ for a working WASM proof-of-concept
  - See core/packages/plugin-sdk/templates/python/ for the WASM plugin template

This file will be removed after migration to WASM (componentize-py) is complete.
"""

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
