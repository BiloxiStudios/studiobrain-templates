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
Hello World Plugin — sample event handlers.

Demonstrates how a plugin registers listeners on the backend event bus.
The ``register_handlers`` function is called automatically by the plugin
loader when the plugin is enabled.
"""

import logging

logger = logging.getLogger("plugin.hello-world")


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Register any event listeners the plugin needs here using
    ``event_bus.on(pattern)`` as a decorator or
    ``event_bus.register(pattern, handler)``.
    """

    @event_bus.on("entity.*")
    async def on_entity_event(event):
        """Log every entity lifecycle event as a demo."""
        logger.info(
            "[hello-world] Entity event: %s — %s/%s",
            event.event_type,
            getattr(event, "entity_type", "?"),
            getattr(event, "entity_id", "?"),
        )
