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
Voice Forge Plugin — event handlers.

Logs voice generation events and listens for entity changes
that may affect voice profiles.
"""

import logging

logger = logging.getLogger("plugin.voice-forge")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity events relevant to voice management.
    """

    @event_bus.on("entity.character.*")
    async def on_character_event(event):
        """Log character entity events for voice tracking."""
        event_type = getattr(event, "event_type", "unknown")
        entity_id = getattr(event, "entity_id", "?")
        logger.info(
            "[voice-forge] Character event: %s — id=%s",
            event_type,
            entity_id,
        )

    @event_bus.on("entity.character.deleted")
    async def on_character_deleted(event):
        """Log when a character with a potential voice profile is deleted."""
        entity_id = getattr(event, "entity_id", "?")
        logger.warning(
            "[voice-forge] Character deleted: %s — voice profile may be orphaned",
            entity_id,
        )

    @event_bus.on("plugin.voice-forge.*")
    async def on_voice_forge_event(event):
        """Log internal voice-forge plugin events."""
        logger.info(
            "[voice-forge] Plugin event: %s",
            getattr(event, "event_type", "unknown"),
        )
