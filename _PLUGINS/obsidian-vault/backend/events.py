"""
Obsidian Vault Bridge Plugin -- event handlers.

Listens for entity save/update events and, when auto_export is enabled,
automatically re-exports the changed entity to the Obsidian vault.
"""

import logging
import os

logger = logging.getLogger("plugin.obsidian-vault")


def _load_settings():
    """Load plugin settings from the DB-backed settings service."""
    from services.plugin_settings_service import get_all_settings
    defaults = {
        "vault_path": "",
        "auto_export": False,
        "include_images": True,
        "link_style": "wikilink",
        "folder_per_type": True,
    }
    stored = get_all_settings("obsidian-vault")
    defaults.update({k: v for k, v in stored.items() if k in defaults})
    return defaults


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers listeners for entity save events so the vault stays in sync
    when auto_export is enabled.
    """

    @event_bus.on("entity.saved")
    async def on_entity_saved(event):
        """Auto-export entity to Obsidian vault on save."""
        settings = _load_settings()
        if not settings.get("auto_export", False):
            return

        vault_path = settings.get("vault_path", "").strip()
        if not vault_path:
            logger.debug("[obsidian-vault] Auto-export skipped: no vault path configured")
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)

        if not entity_type or not entity_id:
            logger.debug("[obsidian-vault] Auto-export skipped: missing entity_type or entity_id")
            return

        try:
            # Import the conversion functions from routes (same package)
            from backend.routes import (
                _build_obsidian_markdown,
                _invalidate_name_cache,
                _write_to_vault,
            )

            # Invalidate cache so we pick up fresh data
            _invalidate_name_cache()

            link_style = settings.get("link_style", "wikilink")
            markdown, link_count = _build_obsidian_markdown(entity_type, entity_id, link_style)

            if not os.path.isdir(vault_path):
                os.makedirs(vault_path, exist_ok=True)

            result = _write_to_vault(entity_type, entity_id, markdown, link_count, settings)

            logger.info(
                "[obsidian-vault] Auto-exported %s/%s -> %s (%d links)",
                entity_type,
                entity_id,
                result["file"],
                link_count,
            )
        except Exception as exc:
            logger.error(
                "[obsidian-vault] Auto-export failed for %s/%s: %s",
                entity_type,
                entity_id,
                exc,
            )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Log deletions (do not remove from vault -- user may want history)."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        logger.info(
            "[obsidian-vault] Entity deleted: %s/%s (vault copy retained)",
            entity_type,
            entity_id,
        )

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Auto-export newly created entities if auto_export is on."""
        settings = _load_settings()
        if not settings.get("auto_export", False):
            return

        vault_path = settings.get("vault_path", "").strip()
        if not vault_path:
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)

        if not entity_type or not entity_id:
            return

        try:
            from backend.routes import (
                _build_obsidian_markdown,
                _invalidate_name_cache,
                _write_to_vault,
            )

            _invalidate_name_cache()
            link_style = settings.get("link_style", "wikilink")
            markdown, link_count = _build_obsidian_markdown(entity_type, entity_id, link_style)

            if not os.path.isdir(vault_path):
                os.makedirs(vault_path, exist_ok=True)

            result = _write_to_vault(entity_type, entity_id, markdown, link_count, settings)
            logger.info(
                "[obsidian-vault] Auto-exported new entity %s/%s -> %s",
                entity_type,
                entity_id,
                result["file"],
            )
        except Exception as exc:
            logger.error(
                "[obsidian-vault] Auto-export failed for new entity %s/%s: %s",
                entity_type,
                entity_id,
                exc,
            )
