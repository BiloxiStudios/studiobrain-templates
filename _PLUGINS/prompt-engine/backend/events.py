"""
Prompt Engine Plugin — event handlers.

Listens for entity lifecycle events and invalidates the variable-resolution
cache so that stale values are never used after an entity is edited (pe_020).
"""

import logging

logger = logging.getLogger("plugin.prompt-engine")

# Import the shared in-process cache from the routes module.
# The plugin loader imports both modules into the same process so this is safe.
try:
    from .routes import _RESOLVER_CACHE
except ImportError:
    logger.warning(
        "[prompt-engine] Could not import _RESOLVER_CACHE from routes module. "
        "Cache invalidation events will have no effect. "
        "Ensure the plugin loader imports both backend modules into the same process."
    )
    _RESOLVER_CACHE = {}  # type: ignore[assignment]


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers listeners for entity update and delete events so that the
    resolver cache stays consistent with the latest entity data.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Invalidate cache entries for the updated entity (rule pe_020)."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            return
        prefix = f"{entity_type}:{entity_id}"
        removed = [k for k in list(_RESOLVER_CACHE) if k.startswith(prefix)]
        for k in removed:
            del _RESOLVER_CACHE[k]
        if removed:
            logger.debug(
                "[prompt-engine] Cache invalidated %d entries for %s (entity.updated)",
                len(removed),
                prefix,
            )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Invalidate cache entries for the deleted entity."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            return
        prefix = f"{entity_type}:{entity_id}"
        removed = [k for k in list(_RESOLVER_CACHE) if k.startswith(prefix)]
        for k in removed:
            del _RESOLVER_CACHE[k]
        if removed:
            logger.debug(
                "[prompt-engine] Cache invalidated %d entries for %s (entity.deleted)",
                len(removed),
                prefix,
            )

    @event_bus.on("prompt.template.updated")
    async def on_prompt_updated(event):
        """Log prompt template updates for audit purposes."""
        prompt_id = getattr(event, "prompt_id", "unknown")
        logger.info("[prompt-engine] Prompt template updated: %s", prompt_id)
