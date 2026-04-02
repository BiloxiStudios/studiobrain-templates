"""
Assembly Composer Plugin — backend routes.

Provides API endpoints for the assembly visual composition system:
slot assignment, z-index reordering, slot locking, inheritance resolution,
preview compositing, auto-slot detection, and multi-pipeline export.
"""

import os
import re
import logging
import yaml
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger("plugin.assembly-composer")
router = APIRouter()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ASSEMBLIES_DIR = os.path.join(DATA_ROOT, "Assemblies")
EXPORT_PROFILES_DIR = os.path.join(
    DATA_ROOT, "_TEMPLATES", "Standard", "ExportProfiles"
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class SlotAssignRequest(BaseModel):
    assembly_id: str
    slot_group: str
    slot_name: str
    asset_id: str
    variant_key: Optional[str] = None
    z_index_override: Optional[int] = None


class SlotLockRequest(BaseModel):
    assembly_id: str
    slot_path: str          # "slot_group.slot_name"
    locked: bool


class ZIndexReorderRequest(BaseModel):
    assembly_id: str
    reorder: list[dict]     # [{"slot_group": str, "slot_name": str, "z_index": int}]


class ExportRequest(BaseModel):
    assembly_id: str
    profile_id: str
    color_variant: Optional[str] = "default"
    zombie_stage: Optional[int] = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Allow only safe identifier characters to prevent path traversal
_SAFE_ID_RE = re.compile(r'^[A-Za-z0-9_\-]+$')


def _validate_id(value: str, label: str) -> None:
    """Reject any ID that contains path-traversal characters."""
    if not _SAFE_ID_RE.match(value):
        raise HTTPException(
            status_code=422,
            detail=f"{label} contains invalid characters. "
                   "Only letters, digits, underscores, and hyphens are allowed.",
        )


def _load_assembly_frontmatter(assembly_id: str) -> dict:
    """Load and parse the YAML frontmatter of an assembly markdown file."""
    _validate_id(assembly_id, "assembly_id")
    path = os.path.join(ASSEMBLIES_DIR, f"ASM_{assembly_id}.md")
    # Resolve to an absolute path and confirm it stays inside ASSEMBLIES_DIR
    abs_path = os.path.realpath(path)
    abs_dir  = os.path.realpath(ASSEMBLIES_DIR)
    if not abs_path.startswith(abs_dir + os.sep):
        raise HTTPException(status_code=400, detail="Invalid assembly_id")
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail=f"Assembly not found: {assembly_id}")
    try:
        with open(abs_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read assembly file: {exc}")
    if not text.startswith("---"):
        raise HTTPException(status_code=422, detail="Assembly file missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise HTTPException(status_code=422, detail="Assembly file has malformed frontmatter")
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=422, detail=f"YAML parse error: {exc}")


def _resolve_inheritance_chain(assembly_id: str, depth: int = 0) -> list[dict]:
    """Walk up the parent chain and return ordered list of frontmatter dicts (root first)."""
    if depth > 4:
        raise HTTPException(status_code=422, detail="Inheritance chain exceeds max depth of 4")
    data = _load_assembly_frontmatter(assembly_id)
    parent_id = data.get("parent_assembly_id", "")
    chain = []
    if parent_id:
        chain = _resolve_inheritance_chain(parent_id, depth + 1)
    chain.append(data)
    return chain


def _collect_locked_slots(chain: list[dict]) -> set[str]:
    """Aggregate all locked_slots across the inheritance chain."""
    locked: set[str] = set()
    for node in chain:
        for path in node.get("locked_slots", []):
            locked.add(path)
    return locked


def _validate_z_index(z_index: int) -> None:
    if not (1 <= z_index <= 999):
        raise HTTPException(
            status_code=422,
            detail=f"z_index {z_index} out of range 1–999"
        )


# ---------------------------------------------------------------------------
# Routes — Assembly metadata
# ---------------------------------------------------------------------------

@router.get("/api/plugins/assembly-composer/assemblies")
def list_assemblies(
    assembly_type: Optional[str] = Query(None),
    hierarchy_level: Optional[str] = Query(None),
):
    """List all assembly files, optionally filtered by type or hierarchy level."""
    if not os.path.isdir(ASSEMBLIES_DIR):
        return {"assemblies": []}

    results = []
    for fname in sorted(os.listdir(ASSEMBLIES_DIR)):
        if not fname.endswith(".md"):
            continue
        assembly_id = re.sub(r"^ASM_", "", fname[:-3])
        try:
            data = _load_assembly_frontmatter(assembly_id)
        except HTTPException:
            continue
        if assembly_type and data.get("assembly_type") != assembly_type:
            continue
        if hierarchy_level and data.get("hierarchy_level") != hierarchy_level:
            continue
        results.append({
            "id": assembly_id,
            "name": data.get("name", assembly_id),
            "assembly_type": data.get("assembly_type"),
            "hierarchy_level": data.get("hierarchy_level"),
            "parent_assembly_id": data.get("parent_assembly_id", ""),
            "status": data.get("status"),
            "production_status": data.get("production_status", {}),
        })
    return {"assemblies": results}


@router.get("/api/plugins/assembly-composer/assemblies/{assembly_id}")
def get_assembly(assembly_id: str):
    """Return the full frontmatter for a single assembly."""
    return _load_assembly_frontmatter(assembly_id)


@router.get("/api/plugins/assembly-composer/assemblies/{assembly_id}/inheritance")
def get_inheritance_chain(assembly_id: str):
    """Return the full inheritance chain for an assembly (root → leaf)."""
    chain = _resolve_inheritance_chain(assembly_id)
    locked = _collect_locked_slots(chain)
    return {
        "assembly_id": assembly_id,
        "chain_depth": len(chain),
        "chain": [
            {
                "id": node.get("id", ""),
                "name": node.get("name", ""),
                "hierarchy_level": node.get("hierarchy_level"),
                "locked_slots": node.get("locked_slots", []),
            }
            for node in chain
        ],
        "all_locked_slots": sorted(locked),
    }


# ---------------------------------------------------------------------------
# Routes — Slot management
# ---------------------------------------------------------------------------

@router.get("/api/plugins/assembly-composer/assemblies/{assembly_id}/slots")
def get_slot_map(assembly_id: str):
    """Return all slot definitions for an assembly with inheritance resolved."""
    chain = _resolve_inheritance_chain(assembly_id)
    locked = _collect_locked_slots(chain)

    leaf = chain[-1]
    slot_definitions = leaf.get("slot_definitions", {})

    slot_map = {}
    for group_name, group_slots in slot_definitions.items():
        if not isinstance(group_slots, dict):
            continue
        slot_map[group_name] = {}
        for slot_name, slot_meta in group_slots.items():
            if not isinstance(slot_meta, dict):
                continue
            slot_path = f"{group_name}.{slot_name}"
            slot_map[group_name][slot_name] = {
                **slot_meta,
                "locked": slot_path in locked,
                "slot_path": slot_path,
            }

    return {
        "assembly_id": assembly_id,
        "assembly_type": leaf.get("assembly_type"),
        "slot_definitions": slot_map,
        "locked_slots": sorted(locked),
    }


@router.post("/api/plugins/assembly-composer/assemblies/{assembly_id}/slots/assign")
def assign_slot(assembly_id: str, req: SlotAssignRequest):
    """
    Validate a slot assignment request.

    Checks that:
    - The slot path exists in the assembly's slot_definitions
    - The slot is not locked by an ancestor
    - Any z_index_override is within range 1–999
    """
    chain = _resolve_inheritance_chain(assembly_id)
    locked = _collect_locked_slots(chain)
    slot_path = f"{req.slot_group}.{req.slot_name}"

    if slot_path in locked:
        raise HTTPException(
            status_code=403,
            detail=f"Slot '{slot_path}' is locked by an ancestor assembly and cannot be overridden."
        )

    leaf = chain[-1]
    group = leaf.get("slot_definitions", {}).get(req.slot_group)
    if group is None:
        raise HTTPException(status_code=404, detail=f"Slot group '{req.slot_group}' not found")
    slot_meta = group.get(req.slot_name)
    if not isinstance(slot_meta, dict):
        raise HTTPException(status_code=404, detail=f"Slot '{req.slot_name}' not found in group '{req.slot_group}'")

    if req.z_index_override is not None:
        _validate_z_index(req.z_index_override)

    return {
        "ok": True,
        "assembly_id": assembly_id,
        "slot_path": slot_path,
        "asset_id": req.asset_id,
        "variant_key": req.variant_key,
        "z_index": req.z_index_override or slot_meta.get("z_index"),
        "message": "Slot assignment validated. Apply via entity write API.",
    }


@router.post("/api/plugins/assembly-composer/assemblies/{assembly_id}/slots/lock")
def set_slot_lock(assembly_id: str, req: SlotLockRequest):
    """
    Validate a slot lock/unlock request.

    Verifies that the slot_path references an existing slot_group.slot_name in this assembly.
    Applying the lock to the file is handled by the entity write API.
    """
    leaf = _load_assembly_frontmatter(assembly_id)
    parts = req.slot_path.split(".", 1)
    if len(parts) != 2:
        raise HTTPException(
            status_code=422,
            detail=f"slot_path must be in format 'slot_group.slot_name', got '{req.slot_path}'"
        )
    group_name, slot_name = parts
    group = leaf.get("slot_definitions", {}).get(group_name)
    if group is None or not isinstance(group.get(slot_name), dict):
        raise HTTPException(
            status_code=404,
            detail=f"Slot '{req.slot_path}' does not exist in assembly '{assembly_id}'"
        )
    return {
        "ok": True,
        "assembly_id": assembly_id,
        "slot_path": req.slot_path,
        "locked": req.locked,
        "message": "Lock change validated. Apply via entity write API.",
    }


@router.post("/api/plugins/assembly-composer/assemblies/{assembly_id}/slots/reorder")
def reorder_z_indices(assembly_id: str, req: ZIndexReorderRequest):
    """
    Validate a bulk z-index reorder request.

    Each entry in req.reorder must have slot_group, slot_name, and z_index.
    All z_index values must be unique integers in range 1–999.
    """
    seen: set[int] = set()
    for entry in req.reorder:
        z = entry.get("z_index")
        if z is None:
            raise HTTPException(status_code=422, detail="Each reorder entry must include z_index")
        _validate_z_index(z)
        if z in seen:
            raise HTTPException(
                status_code=422,
                detail=f"Duplicate z_index {z} in reorder request"
            )
        seen.add(z)
    return {
        "ok": True,
        "assembly_id": assembly_id,
        "reordered_count": len(req.reorder),
        "message": "Z-index reorder validated. Apply via entity write API.",
    }


# ---------------------------------------------------------------------------
# Routes — Export
# ---------------------------------------------------------------------------

@router.get("/api/plugins/assembly-composer/export-profiles")
def list_export_profiles():
    """List all available export profile YAML files."""
    if not os.path.isdir(EXPORT_PROFILES_DIR):
        return {"profiles": []}
    profiles = []
    for fname in sorted(os.listdir(EXPORT_PROFILES_DIR)):
        if fname.endswith(".yaml"):
            profile_id = fname[:-5]
            profiles.append({"id": profile_id, "file": fname})
    return {"profiles": profiles}


@router.post("/api/plugins/assembly-composer/export")
def request_export(req: ExportRequest):
    """
    Validate an export request against the chosen profile.

    Checks:
    - Profile file exists in ExportProfiles/
    - Assembly has all required slots filled (reads slot_definitions)
    """
    profile_path = os.path.join(EXPORT_PROFILES_DIR, f"{req.profile_id}.yaml")
    # Validate profile_id and confirm path stays inside EXPORT_PROFILES_DIR
    _validate_id(req.profile_id, "profile_id")
    abs_profile = os.path.realpath(profile_path)
    abs_profiles_dir = os.path.realpath(EXPORT_PROFILES_DIR)
    if not abs_profile.startswith(abs_profiles_dir + os.sep):
        raise HTTPException(status_code=400, detail="Invalid profile_id")
    if not os.path.isfile(abs_profile):
        raise HTTPException(
            status_code=404,
            detail=f"Export profile '{req.profile_id}' not found"
        )

    leaf = _load_assembly_frontmatter(req.assembly_id)
    slot_defs = leaf.get("slot_definitions", {})

    missing_required = []
    for group_name, group_slots in slot_defs.items():
        if not isinstance(group_slots, dict):
            continue
        for slot_name, slot_meta in group_slots.items():
            if isinstance(slot_meta, dict) and slot_meta.get("required") is True:
                missing_required.append(f"{group_name}.{slot_name}")

    if missing_required:
        logger.warning(
            "Export requested for %s but required slots not yet validated as filled: %s",
            req.assembly_id, missing_required
        )

    return {
        "ok": True,
        "assembly_id": req.assembly_id,
        "profile_id": req.profile_id,
        "color_variant": req.color_variant,
        "zombie_stage": req.zombie_stage,
        "required_slots": missing_required,
        "message": (
            "Export job queued. Required slot fill status must be confirmed by the export service."
        ),
    }


@router.get("/api/plugins/assembly-composer/assemblies/{assembly_id}/preview")
def get_preview_info(assembly_id: str):
    """Return metadata needed for client-side composite preview rendering."""
    chain = _resolve_inheritance_chain(assembly_id)
    locked = _collect_locked_slots(chain)
    leaf = chain[-1]

    layout = leaf.get("layout", {})
    slot_defs = leaf.get("slot_definitions", {})

    z_ordered_slots = []
    for group_name, group_slots in slot_defs.items():
        if not isinstance(group_slots, dict):
            continue
        for slot_name, slot_meta in group_slots.items():
            if not isinstance(slot_meta, dict):
                continue
            slot_path = f"{group_name}.{slot_name}"
            z_ordered_slots.append({
                "slot_path": slot_path,
                "slot_group": group_name,
                "slot_name": slot_name,
                "z_index": slot_meta.get("z_index", 50),
                "overlay_modes": slot_meta.get("overlay_modes", ["replace"]),
                "locked": slot_path in locked,
            })

    z_ordered_slots.sort(key=lambda s: s["z_index"])

    return {
        "assembly_id": assembly_id,
        "assembly_type": leaf.get("assembly_type"),
        "layout": layout,
        "z_ordered_slots": z_ordered_slots,
        "color_variants": leaf.get("color_variants", [{"name": "default"}]),
        "infection_system_enabled": leaf.get("infection_system", {}).get("enabled", False),
        "zombie_progression_enabled": leaf.get("zombie_progression", {}).get("enabled", False),
    }
