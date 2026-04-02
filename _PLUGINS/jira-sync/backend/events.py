"""
Jira Sync Plugin -- Event Handlers.

Listens for entity lifecycle events on the backend event bus and
automatically creates / transitions linked Jira issues when enabled.

The ``register_handlers`` function is called by the plugin loader when the
plugin is enabled.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("plugin.jira-sync")

PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
LINKS_FILE = DATA_DIR / "entity_links.json"
STUDIO_API = "http://localhost:8201/api"
PLUGIN_API = "http://localhost:8201/api/ext/jira-sync"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def _read_settings() -> Dict[str, Any]:
    settings_file = PLUGIN_DIR.parent / "_plugin_settings.json"
    all_settings = _load_json(settings_file, {})
    return all_settings.get("jira-sync", {})


def _jira_configured() -> bool:
    s = _read_settings()
    return bool(s.get("jira_instance_url") and s.get("jira_api_token"))


def _link_key(entity_type: str, entity_id: str) -> str:
    return f"{entity_type}:{entity_id}"


def _load_links() -> Dict[str, Any]:
    return _load_json(LINKS_FILE, {})


# ---------------------------------------------------------------------------
# Event registration
# ---------------------------------------------------------------------------

def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.

    Registers handlers for entity creation and update events so that
    Jira issues are automatically created and transitioned when the
    corresponding settings are enabled.
    """

    @event_bus.on("entity.created")
    async def on_entity_created(event):
        """Auto-create a Jira issue when a new entity is created (if enabled)."""
        settings = _read_settings()
        if not settings.get("auto_create_on_entity", False):
            return
        if not _jira_configured():
            logger.debug("[jira-sync] Skipping auto-create: Jira not configured")
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            return

        logger.info("[jira-sync] Auto-creating Jira issue for %s/%s", entity_type, entity_id)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{PLUGIN_API}/sync/{entity_type}/{entity_id}"
                )
            if resp.status_code in (200, 201):
                data = resp.json()
                logger.info(
                    "[jira-sync] Created Jira issue %s for %s/%s",
                    data.get("issue_key", "?"),
                    entity_type,
                    entity_id,
                )
            else:
                logger.error(
                    "[jira-sync] Failed to create issue for %s/%s: HTTP %s",
                    entity_type,
                    entity_id,
                    resp.status_code,
                )
        except Exception as exc:
            logger.error("[jira-sync] Auto-create error for %s/%s: %s", entity_type, entity_id, exc)

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Auto-transition linked Jira issue when entity status changes (if enabled)."""
        settings = _read_settings()
        if not settings.get("auto_transition_on_status", True):
            return
        if not _jira_configured():
            return

        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            return

        # Check if this entity is linked
        links = _load_links()
        key = _link_key(entity_type, entity_id)
        link = links.get(key)
        if not link or not link.get("issue_key"):
            return

        # Check if status changed
        changes = getattr(event, "changes", {})
        if not isinstance(changes, dict):
            return

        new_status = changes.get("production_status")
        if not new_status:
            # Also check for flat new values
            new_data = getattr(event, "data", {})
            if isinstance(new_data, dict):
                new_status = new_data.get("production_status")

        if not new_status:
            return

        # Map to Jira status
        status_raw = settings.get(
            "status_field_mapping",
            '{"draft":"To Do","in_progress":"In Progress","review":"In Review","complete":"Done"}'
        )
        try:
            status_map = json.loads(status_raw) if isinstance(status_raw, str) else status_raw
        except Exception:
            status_map = {}

        jira_status = status_map.get(new_status)
        if not jira_status:
            logger.debug("[jira-sync] No Jira status mapping for '%s'", new_status)
            return

        logger.info(
            "[jira-sync] Transitioning %s to '%s' for %s/%s",
            link["issue_key"],
            jira_status,
            entity_type,
            entity_id,
        )

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{PLUGIN_API}/sync/{entity_type}/{entity_id}"
                )
            if resp.status_code in (200, 201):
                logger.info("[jira-sync] Sync complete for %s/%s", entity_type, entity_id)
            else:
                logger.error(
                    "[jira-sync] Sync failed for %s/%s: HTTP %s",
                    entity_type,
                    entity_id,
                    resp.status_code,
                )
        except Exception as exc:
            logger.error("[jira-sync] Transition error for %s/%s: %s", entity_type, entity_id, exc)

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Log deletion of linked entities (does NOT delete the Jira issue)."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)
        if not entity_type or not entity_id:
            return

        links = _load_links()
        key = _link_key(entity_type, entity_id)
        link = links.get(key)
        if link:
            logger.warning(
                "[jira-sync] Entity %s/%s deleted but linked to Jira issue %s. "
                "The Jira issue was NOT deleted. Remove the link manually if needed.",
                entity_type,
                entity_id,
                link.get("issue_key", "?"),
            )
