"""
Version History Plugin — Event Handlers

Listens for entity lifecycle events on the backend event bus and logs
version-related activity.  When an entity is created, updated, or deleted
the handler logs the event and can optionally auto-commit the change to git.
"""

import asyncio
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("plugin.version-history")

BRAINS_ROOT = Path(r"A:\Brains")

# Mapping mirrors routes.py
ENTITY_MAP = {
    "character":  ("Characters",  "CH_"),
    "location":   ("Locations",   "LOC_"),
    "brand":      ("Brands",      "BR_"),
    "district":   ("Districts",   "DIST_"),
    "faction":    ("Factions",    "FACT_"),
    "item":       ("Items",       "ITEM_"),
    "job":        ("Jobs",        "JOB_"),
    "quest":      ("Quests",      "QUEST_"),
    "event":      ("Events",      "EVENT_"),
    "campaign":   ("Campaigns",   "CAMP_"),
    "assembly":   ("Assemblies",  "ASSM_"),
}


def _resolve_entity_path(entity_type: str, entity_id: str) -> Path | None:
    """Return the path to the entity markdown file, or None if unknown type."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        return None
    folder, prefix = mapping
    return BRAINS_ROOT / folder / entity_id / f"{prefix}{entity_id}.md"


def _run_git_sync(*args: str) -> subprocess.CompletedProcess:
    """Synchronous git helper for use inside run_in_executor."""
    cmd = ["git", "-C", str(BRAINS_ROOT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


async def _auto_commit(entity_type: str, entity_id: str, action: str):
    """Stage and commit the entity file if it has changes."""
    entity_path = _resolve_entity_path(entity_type, entity_id)
    if entity_path is None or not entity_path.exists():
        return

    rel_path = str(entity_path.relative_to(BRAINS_ROOT)).replace("\\", "/")
    loop = asyncio.get_event_loop()

    # Stage the file
    result = await loop.run_in_executor(None, lambda: _run_git_sync("add", rel_path))
    if result.returncode != 0:
        logger.warning("Failed to stage %s: %s", rel_path, result.stderr.strip())
        return

    # Check if there are staged changes for this file
    diff_result = await loop.run_in_executor(
        None, lambda: _run_git_sync("diff", "--cached", "--quiet", "--", rel_path)
    )
    if diff_result.returncode == 0:
        # No changes staged — nothing to commit
        logger.debug("No changes to commit for %s/%s", entity_type, entity_id)
        return

    # Commit
    msg = f"{action.title()} {entity_type}: {entity_id}"
    commit_result = await loop.run_in_executor(
        None, lambda: _run_git_sync("commit", "-m", msg, "--", rel_path)
    )
    if commit_result.returncode == 0:
        logger.info("[version-history] Auto-committed: %s", msg)
    else:
        logger.warning("[version-history] Commit failed for %s: %s", rel_path, commit_result.stderr.strip())


def register_handlers(event_bus):
    """Register event handlers on the backend event bus.

    Called automatically by the plugin loader when the plugin is enabled.
    """

    @event_bus.on("entity.*")
    async def on_entity_event(event):
        """Log entity events and optionally auto-commit changes."""
        event_type = getattr(event, "event_type", "unknown")
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)

        if not entity_type or not entity_id:
            return

        logger.info(
            "[version-history] %s — %s/%s",
            event_type,
            entity_type,
            entity_id,
        )

        # Determine the action from the event type
        # Common patterns: entity.created, entity.updated, entity.deleted,
        # entity.saved, entity.character.updated, etc.
        action = "update"
        et_lower = event_type.lower()
        if "creat" in et_lower:
            action = "create"
        elif "delet" in et_lower:
            action = "delete"
        elif "sav" in et_lower or "updat" in et_lower:
            action = "update"

        # Auto-commit on create/update/save events
        if action in ("create", "update"):
            try:
                await _auto_commit(entity_type, entity_id, action)
            except Exception as exc:
                logger.error("[version-history] Auto-commit error: %s", exc)
