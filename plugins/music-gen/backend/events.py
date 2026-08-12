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
Music Generator Plugin — event handlers.

Listens for entity lifecycle events relevant to music track management.
The ``register_handlers`` function is called automatically by the plugin
loader when the plugin is enabled.
"""

import logging

logger = logging.getLogger("plugin.music-gen")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity events relevant to music generation.
    """

    @event_bus.on("entity.*.created")
    async def on_entity_created(event):
        """Log entity creation — could trigger auto-generation in future."""
        entity_type = getattr(event, "entity_type", "?")
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[music-gen] Entity created: %s/%s — music can be generated",
            entity_type,
            entity_id,
        )

    @event_bus.on("entity.*.deleted")
    async def on_entity_deleted(event):
        """Warn when an entity with potential music tracks is deleted."""
        entity_type = getattr(event, "entity_type", "?")
        entity_id = getattr(event, "entity_id", "?")
        logger.warning(
            "[music-gen] Entity deleted: %s/%s — associated tracks may be orphaned",
            entity_type,
            entity_id,
        )

    @event_bus.on("plugin.music-gen.*")
    async def on_music_gen_event(event):
        """Log internal music-gen plugin events."""
        logger.info(
            "[music-gen] Plugin event: %s",
            getattr(event, "event_type", "unknown"),
        )
