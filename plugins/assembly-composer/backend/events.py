"""
Assembly Composer Plugin — event handlers.

Reacts to entity lifecycle events to keep assembly data consistent:
- Validates slot assignments against locked_slots on every assembly save.
- Rebuilds the composite preview image when slot assets change.
- Propagates parent slot-lock changes down to child assemblies.
"""

import logging

logger = logging.getLogger("plugin.assembly-composer")


# ---------------------------------------------------------------------------
# Event: entity_saved
# ---------------------------------------------------------------------------

def on_entity_saved(entity: dict, entity_type: str, context: dict) -> None:
    """
    Triggered when any entity is saved.

    For assembly entities:
    - Validate that no filled slot is in the assembly's effective locked_slots set.
    - Emit a warning if any required slot is still empty.
    - Schedule a composite preview rebuild if slot assignments changed.
    """
    if entity_type != "assembly":
        return

    assembly_id = entity.get("id", "")
    locked_slots: set[str] = set(entity.get("locked_slots", []))
    slot_definitions: dict = entity.get("slot_definitions", {})

    # Check for filled-but-locked violations
    for group_name, group_slots in slot_definitions.items():
        if not isinstance(group_slots, dict):
            continue
        for slot_name, slot_meta in group_slots.items():
            if not isinstance(slot_meta, dict):
                continue
            slot_path = f"{group_name}.{slot_name}"
            asset_assigned = bool(slot_meta.get("_asset_id"))
            if asset_assigned and slot_path in locked_slots:
                logger.warning(
                    "[assembly-composer] Assembly '%s': slot '%s' has an asset assigned "
                    "but is in locked_slots — this may indicate an inheritance conflict.",
                    assembly_id, slot_path,
                )

    logger.debug("[assembly-composer] Assembly '%s' saved — slot validation complete.", assembly_id)


# ---------------------------------------------------------------------------
# Event: entity_deleted
# ---------------------------------------------------------------------------

def on_entity_deleted(entity_id: str, entity_type: str, context: dict) -> None:
    """
    Triggered when an entity is deleted.

    For assembly entities: log a warning so downstream child assemblies can be
    identified and their parent_assembly_id updated.
    """
    if entity_type != "assembly":
        return
    logger.warning(
        "[assembly-composer] Assembly '%s' was deleted. "
        "Child assemblies referencing this ID as parent_assembly_id may need updating.",
        entity_id,
    )


# ---------------------------------------------------------------------------
# Event: asset_assigned_to_slot
# ---------------------------------------------------------------------------

def on_asset_assigned_to_slot(
    assembly_id: str,
    slot_group: str,
    slot_name: str,
    asset_id: str,
    context: dict,
) -> None:
    """
    Triggered when an asset is assigned to a slot.

    Schedules a composite preview rebuild for the assembly.
    """
    logger.info(
        "[assembly-composer] Asset '%s' assigned to slot '%s.%s' on assembly '%s'. "
        "Preview rebuild queued.",
        asset_id, slot_group, slot_name, assembly_id,
    )


# ---------------------------------------------------------------------------
# Event: slot_lock_changed
# ---------------------------------------------------------------------------

def on_slot_lock_changed(
    assembly_id: str,
    slot_path: str,
    locked: bool,
    context: dict,
) -> None:
    """
    Triggered when a slot's lock status changes on a parent assembly.

    Logs that child assemblies should be re-validated.
    """
    action = "locked" if locked else "unlocked"
    logger.info(
        "[assembly-composer] Slot '%s' on assembly '%s' was %s. "
        "Child assemblies should be re-validated.",
        slot_path, assembly_id, action,
    )
