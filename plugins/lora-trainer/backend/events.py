"""
LoRA Training Manager Plugin -- event handlers.

Listens for entity lifecycle events and logs when entities
with linked LoRA models are updated or deleted.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("plugin.lora-trainer")

PLUGIN_DATA = Path(__file__).resolve().parent.parent / "data"
LORA_INDEX_FILE = PLUGIN_DATA / "lora_index.json"
JOBS_FILE = PLUGIN_DATA / "training_jobs.json"


def _load_lora_index() -> list[dict]:
    try:
        if LORA_INDEX_FILE.exists():
            return json.loads(LORA_INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _load_jobs() -> list[dict]:
    try:
        if JOBS_FILE.exists():
            return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _entity_has_lora(entity_id: str) -> bool:
    """Check if an entity has any linked LoRA models or completed jobs."""
    loras = _load_lora_index()
    if any(l.get("entity_id") == entity_id for l in loras):
        return True
    jobs = _load_jobs()
    if any(j.get("entity_id") == entity_id and j["status"] == "completed" for j in jobs):
        return True
    return False


def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers listeners for entity events relevant to LoRA training.
    """

    @event_bus.on("entity.updated")
    async def on_entity_updated(event):
        """Log when an entity with linked LoRAs is updated."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)

        if not entity_type or not entity_id:
            return

        # Only care about character entities
        if entity_type != "character":
            return

        if _entity_has_lora(entity_id):
            changes = getattr(event, "changes", {})
            logger.info(
                "[lora-trainer] Character with LoRA updated: %s — changes: %s",
                entity_id,
                list(changes.keys()) if isinstance(changes, dict) else "unknown",
            )

            # Check if appearance-related fields changed (may need retraining)
            appearance_fields = {
                "appearance", "physical_description", "hair_color",
                "eye_color", "skin_tone", "distinguishing_features",
            }
            if isinstance(changes, dict):
                changed_fields = set(changes.keys())
                if changed_fields & appearance_fields:
                    logger.warning(
                        "[lora-trainer] Appearance fields changed for %s — "
                        "existing LoRA may need retraining: %s",
                        entity_id,
                        changed_fields & appearance_fields,
                    )

    @event_bus.on("entity.deleted")
    async def on_entity_deleted(event):
        """Log when an entity with linked LoRAs is deleted."""
        entity_type = getattr(event, "entity_type", None)
        entity_id = getattr(event, "entity_id", None)

        if not entity_type or not entity_id:
            return

        if entity_type != "character":
            return

        if _entity_has_lora(entity_id):
            logger.warning(
                "[lora-trainer] Character with LoRA deleted: %s — "
                "LoRA files will be orphaned. Consider manual cleanup.",
                entity_id,
            )

    @event_bus.on("entity.character.created")
    async def on_character_created(event):
        """Log when a new character is created (potential training candidate)."""
        entity_id = getattr(event, "entity_id", "unknown")
        logger.info(
            "[lora-trainer] New character created: %s — may be eligible for LoRA training",
            entity_id,
        )
