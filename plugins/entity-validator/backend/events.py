"""
Entity Validator Plugin — event handlers

SBAI-1677: Intercept entity.pre_write events and reject writes whose
frontmatter fails JSON Schema validation.

The ``validate_on_write`` plugin setting (default: true) controls whether
validation is enforced.  When the setting is false the handler logs a warning
but does not block the write.
"""

import logging
from typing import Any

logger = logging.getLogger("plugin.entity-validator")

# Plugin settings are injected by the plugin loader at startup.
# Default values are defined in plugin.json → settings_schema.
_settings: dict[str, Any] = {
    "validate_on_write": True,
    "strict_mode": False,
}


def configure(settings: dict[str, Any]) -> None:
    """Called by the plugin loader with the instance settings."""
    _settings.update(settings)


def register_handlers(event_bus) -> None:
    """Register entity lifecycle listeners on the backend event bus."""

    @event_bus.on("entity.pre_write")
    async def on_entity_pre_write(event) -> None:
        """Validate entity frontmatter before it is persisted.

        The event is expected to carry:
            event.entity_type  — string entity type (e.g. "character")
            event.frontmatter  — dict of the parsed YAML frontmatter

        When validation fails and ``validate_on_write`` is enabled, the handler
        raises ``ValueError`` which the backend event bus should treat as a
        write guard: the write is aborted and the caller receives a 422 response
        with the validation errors.
        """
        entity_type = getattr(event, "entity_type", None)
        frontmatter = getattr(event, "frontmatter", None)

        if not entity_type or not isinstance(frontmatter, dict):
            # Not enough information to validate; let the write proceed.
            return

        # Import here to avoid circular imports at module load time.
        from .routes import _validate_frontmatter, ENTITY_SCHEMAS  # noqa: PLC0415

        if entity_type not in ENTITY_SCHEMAS:
            logger.debug(
                "[entity-validator] No schema for entity type '%s'; skipping validation.",
                entity_type,
            )
            return

        strict = _settings.get("strict_mode", False)
        errors = _validate_frontmatter(frontmatter, entity_type, strict=strict)

        if not errors:
            logger.debug(
                "[entity-validator] entity.pre_write OK — %s/%s",
                entity_type,
                frontmatter.get("id", "?"),
            )
            return

        error_summary = "; ".join(
            f"{e['field']}: {e['message']}" for e in errors[:5]
        )
        if len(errors) > 5:
            error_summary += f" … ({len(errors) - 5} more)"

        if _settings.get("validate_on_write", True):
            raise ValueError(
                f"Entity frontmatter validation failed for '{entity_type}' "
                f"(id={frontmatter.get('id', '?')}): {error_summary}"
            )
        else:
            logger.warning(
                "[entity-validator] Validation failed but validate_on_write=false — "
                "%s/%s — %s",
                entity_type,
                frontmatter.get("id", "?"),
                error_summary,
            )
