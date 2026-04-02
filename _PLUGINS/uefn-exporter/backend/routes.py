"""
UEFN Exporter Plugin — Backend Routes.

Generates Verse data structures, device configurations, dialogue exports,
and Creative island metadata from City of Brains Studio entities.

All routes are mounted at /api/ext/uefn-exporter/ by the plugin loader.
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

logger = logging.getLogger("plugin.uefn-exporter")

router = APIRouter()

# ─── Constants ────────────────────────────────────────────────────────

BRAINS_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PLUGINS_DIR = BRAINS_ROOT / "_Plugins"
TEMPLATES_DIR = BRAINS_ROOT / "_Templates" / "Standard"

# Entity type directory mapping
ENTITY_TYPE_DIRS = {
    "character": "Characters",
    "location": "Locations",
    "item": "Items",
    "quest": "Quests",
    "faction": "Factions",
    "event": "Events",
    "dialogue": "Dialogues",
    "district": "Districts",
    "brand": "Brands",
    "campaign": "Campaigns",
    "job": "Jobs",
}

# Entity type prefixes used in markdown filenames
ENTITY_TYPE_PREFIXES = {
    "character": "CH_",
    "location": "LOC_",
    "item": "IT_",
    "quest": "QST_",
    "faction": "FAC_",
    "event": "EVT_",
    "dialogue": "DLG_",
    "district": "DST_",
    "brand": "BR_",
    "campaign": "CMP_",
    "job": "JOB_",
}

# Verse type mappings from YAML/frontmatter types
VERSE_TYPE_MAP = {
    "string": "string",
    "str": "string",
    "int": "int",
    "integer": "int",
    "float": "float",
    "number": "float",
    "bool": "logic",
    "boolean": "logic",
    "list": "[]string",
    "array": "[]string",
    "date": "string",
    "datetime": "string",
}

# Default Verse values per type
VERSE_DEFAULTS = {
    "string": '""',
    "int": "0",
    "float": "0.0",
    "logic": "false",
    "[]string": "array{}",
}


# ─── Helpers ──────────────────────────────────────────────────────────

def _get_setting(key: str, default: Any = None) -> Any:
    """Get a single plugin setting."""
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("uefn-exporter").get(key, default)


def _verse_module() -> str:
    return _get_setting("verse_module", "CityOfBrains")


def _creative_version() -> str:
    return _get_setting("creative_version", "31.00")


def _sanitize_verse_id(name: str) -> str:
    """Convert a name to a valid Verse identifier (snake_case, alphanumeric)."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower().strip())
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized or "unnamed"


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from markdown content."""
    import re as _re

    # Match frontmatter block between --- delimiters
    match = _re.match(r"^---\s*\n(.*?)\n---", content, _re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    fields = {}

    # Simple YAML parser for flat and simple nested values
    current_key = None
    current_list = None

    for line in frontmatter_text.split("\n"):
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith("#"):
            continue

        # List item continuation
        if stripped.startswith("- ") and current_key and current_list is not None:
            val = stripped[2:].strip().strip('"').strip("'")
            current_list.append(val)
            fields[current_key] = current_list
            continue

        # Key: value pair
        if ":" in stripped:
            # Check indent level
            indent = len(line) - len(line.lstrip())
            if indent > 0 and current_key:
                # Nested key — skip deep nesting for Verse export simplicity
                continue

            parts = stripped.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip().strip('"').strip("'") if len(parts) > 1 else ""

            if val == "" or val == "[]" or val == "{}":
                current_key = key
                current_list = [] if val == "[]" else None
                if val == "[]":
                    fields[key] = []
                continue

            # Check for list start on next lines
            current_key = key
            current_list = None

            # Determine type
            if val.lower() in ("true", "false"):
                fields[key] = val.lower() == "true"
            elif val.isdigit():
                fields[key] = int(val)
            else:
                try:
                    fields[key] = float(val)
                except ValueError:
                    fields[key] = val
        else:
            current_list = None

    return fields


def _read_entity(entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """Read an entity's markdown file and parse its frontmatter fields."""
    dir_name = ENTITY_TYPE_DIRS.get(entity_type)
    if not dir_name:
        return None

    entity_dir = BRAINS_ROOT / dir_name / entity_id
    if not entity_dir.is_dir():
        return None

    prefix = ENTITY_TYPE_PREFIXES.get(entity_type, "")
    md_file = entity_dir / f"{prefix}{entity_id}.md"

    if not md_file.exists():
        # Try finding any .md file in the directory
        md_files = list(entity_dir.glob("*.md"))
        if md_files:
            md_file = md_files[0]
        else:
            return None

    content = md_file.read_text(encoding="utf-8")
    fields = _parse_frontmatter(content)
    fields["_entity_type"] = entity_type
    fields["_entity_id"] = entity_id
    fields["_source_file"] = str(md_file)
    return fields


def _read_template_fields(entity_type: str) -> Dict[str, str]:
    """Read a template and extract field names with their inferred types."""
    template_name = f"{entity_type.upper()}_TEMPLATE.md"
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        return {}

    content = template_path.read_text(encoding="utf-8")
    fields = _parse_frontmatter(content)

    # Infer types from template default values
    type_map = {}
    skip_fields = {"template_version", "id", "entity_type", "created_date",
                   "last_updated", "status", "primary_image", "_entity_type",
                   "_entity_id", "_source_file"}

    for key, val in fields.items():
        if key in skip_fields or key.startswith("_"):
            continue

        if isinstance(val, bool):
            type_map[key] = "logic"
        elif isinstance(val, int):
            type_map[key] = "int"
        elif isinstance(val, float):
            type_map[key] = "float"
        elif isinstance(val, list):
            type_map[key] = "[]string"
        else:
            type_map[key] = "string"

    return type_map


def _infer_verse_type(value: Any) -> str:
    """Infer a Verse type from a Python value."""
    if isinstance(value, bool):
        return "logic"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, list):
        return "[]string"
    return "string"


def _verse_value(value: Any, vtype: str) -> str:
    """Convert a Python value to its Verse literal representation."""
    if value is None:
        return VERSE_DEFAULTS.get(vtype, '""')

    if vtype == "logic":
        return "true" if value else "false"
    elif vtype == "int":
        try:
            return str(int(value))
        except (ValueError, TypeError):
            return "0"
    elif vtype == "float":
        try:
            return str(float(value))
        except (ValueError, TypeError):
            return "0.0"
    elif vtype == "[]string":
        if isinstance(value, list):
            items = ", ".join(f'"{_escape_verse_string(str(v))}"' for v in value)
            return f"array{{{items}}}"
        return "array{}"
    else:
        return f'"{_escape_verse_string(str(value))}"'


def _escape_verse_string(s: str) -> str:
    """Escape special characters for Verse string literals."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _list_entities(entity_type: str) -> List[str]:
    """List all entity IDs of a given type."""
    dir_name = ENTITY_TYPE_DIRS.get(entity_type)
    if not dir_name:
        return []
    entity_root = BRAINS_ROOT / dir_name
    if not entity_root.is_dir():
        return []
    return [d.name for d in sorted(entity_root.iterdir())
            if d.is_dir() and not d.name.startswith(".")]


# ─── Verse Code Generators ───────────────────────────────────────────

def _generate_verse_class(entity_type: str) -> str:
    """Generate a Verse class definition from an entity type's template."""
    module = _verse_module()
    class_name = entity_type.capitalize() + "Data"
    template_fields = _read_template_fields(entity_type)

    # If no template found, try reading an actual entity to infer fields
    if not template_fields:
        entities = _list_entities(entity_type)
        if entities:
            sample = _read_entity(entity_type, entities[0])
            if sample:
                skip = {"_entity_type", "_entity_id", "_source_file",
                        "template_version", "id", "entity_type",
                        "created_date", "last_updated", "status", "primary_image"}
                template_fields = {
                    k: _infer_verse_type(v)
                    for k, v in sample.items()
                    if k not in skip and not k.startswith("_")
                }

    lines = [
        f"# Auto-generated by City of Brains UEFN Exporter",
        f"# Entity Type: {entity_type}",
        f"# Creative Version: {_creative_version()}",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"",
        f"using {{ /Verse.org/Simulation }}",
        f"using {{ /Fortnite.com/Devices }}",
        f"using {{ /UnrealEngine.com/Temporary/SpatialMath }}",
        f"",
        f"{_sanitize_verse_id(module)}_module := module:",
        f"",
        f"    {_sanitize_verse_id(class_name)} := class:",
    ]

    if not template_fields:
        lines.append(f"        # No fields found for entity type '{entity_type}'")
        lines.append(f'        Name : string = ""')
    else:
        for field_name, vtype in template_fields.items():
            safe_name = _sanitize_verse_id(field_name)
            default = VERSE_DEFAULTS.get(vtype, '""')
            lines.append(f"        {safe_name} : {vtype} = {default}")

    return "\n".join(lines)


def _generate_verse_instance(entity_type: str, entity_id: str) -> str:
    """Generate a Verse data instance for a specific entity."""
    entity = _read_entity(entity_type, entity_id)
    if not entity:
        raise HTTPException(status_code=404,
                            detail=f"Entity not found: {entity_type}/{entity_id}")

    module = _verse_module()
    class_name = entity_type.capitalize() + "Data"
    var_name = _sanitize_verse_id(entity_id)

    skip = {"_entity_type", "_entity_id", "_source_file",
            "template_version", "id", "entity_type",
            "created_date", "last_updated", "status", "primary_image"}

    lines = [
        f"# Auto-generated by City of Brains UEFN Exporter",
        f"# Entity: {entity_type}/{entity_id}",
        f"# Creative Version: {_creative_version()}",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"",
        f"{var_name} : {_sanitize_verse_id(module)}_module.{_sanitize_verse_id(class_name)} = {_sanitize_verse_id(module)}_module.{_sanitize_verse_id(class_name)}:",
    ]

    for key, value in entity.items():
        if key in skip or key.startswith("_"):
            continue
        safe_key = _sanitize_verse_id(key)
        vtype = _infer_verse_type(value)
        vval = _verse_value(value, vtype)
        lines.append(f"    {safe_key} = {vval}")

    return "\n".join(lines)


def _generate_device_config(entity_type: str, entity_id: str) -> str:
    """Generate a UEFN device configuration block for an entity."""
    entity = _read_entity(entity_type, entity_id)
    if not entity:
        raise HTTPException(status_code=404,
                            detail=f"Entity not found: {entity_type}/{entity_id}")

    module = _verse_module()
    device_name = _sanitize_verse_id(entity_id) + "_device"
    entity_name = entity.get("name", entity_id)

    lines = [
        f"# UEFN Device Configuration",
        f"# Entity: {entity_type}/{entity_id}",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"",
        f"using {{ /Verse.org/Simulation }}",
        f"using {{ /Fortnite.com/Devices }}",
        f"using {{ /Fortnite.com/Characters }}",
        f"using {{ /UnrealEngine.com/Temporary/SpatialMath }}",
        f"",
    ]

    if entity_type == "character":
        behavior = _get_setting("npc_behavior_template", "dialogue")
        lines.extend([
            f"{device_name} := class(creative_device):",
            f'    # NPC: {entity_name}',
            f'    var NpcName : string = "{_escape_verse_string(entity_name)}"',
            f'    var NpcAge : int = {entity.get("age", 0) if isinstance(entity.get("age"), int) else 0}',
            f'    var NpcGender : string = "{_escape_verse_string(str(entity.get("gender", "")))}"',
            f"    var SpawnLocation : vector3 = vector3{{X := 0.0, Y := 0.0, Z := 0.0}}",
            f'    var BehaviorMode : string = "{behavior}"',
            f"",
            f"    OnBegin<override>()<suspends> : void =",
            f'        Print("Spawning NPC: {{NpcName}}")',
            f"        # Add NPC spawn and behavior logic here",
        ])

    elif entity_type == "location":
        lines.extend([
            f"{device_name} := class(creative_device):",
            f'    # Location: {entity_name}',
            f'    var LocationName : string = "{_escape_verse_string(entity_name)}"',
            f"    var BoundaryMin : vector3 = vector3{{X := 0.0, Y := 0.0, Z := 0.0}}",
            f"    var BoundaryMax : vector3 = vector3{{X := 100.0, Y := 100.0, Z := 50.0}}",
            f"",
            f"    OnBegin<override>()<suspends> : void =",
            f'        Print("Initializing location zone: {{LocationName}}")',
        ])

    elif entity_type == "quest":
        lines.extend([
            f"{device_name} := class(creative_device):",
            f'    # Quest: {entity_name}',
            f'    var QuestName : string = "{_escape_verse_string(entity_name)}"',
            f"    var IsActive : logic = false",
            f"    var CurrentStep : int = 0",
            f"    @editable ObjectiveTracker : tracker_device = tracker_device{{}}",
            f"",
            f"    OnBegin<override>()<suspends> : void =",
            f'        Print("Quest device ready: {{QuestName}}")',
        ])

    elif entity_type == "item":
        lines.extend([
            f"{device_name} := class(creative_device):",
            f'    # Item: {entity_name}',
            f'    var ItemName : string = "{_escape_verse_string(entity_name)}"',
            f"    var IsCollectible : logic = true",
            f"    @editable ItemGranter : item_granter_device = item_granter_device{{}}",
            f"",
            f"    OnBegin<override>()<suspends> : void =",
            f'        Print("Item device ready: {{ItemName}}")',
        ])

    else:
        lines.extend([
            f"{device_name} := class(creative_device):",
            f'    # {entity_type.capitalize()}: {entity_name}',
            f'    var EntityName : string = "{_escape_verse_string(entity_name)}"',
            f"",
            f"    OnBegin<override>()<suspends> : void =",
            f'        Print("Device ready: {{EntityName}}")',
        ])

    return "\n".join(lines)


def _generate_dialogue_verse(entity_id: str) -> str:
    """Generate Verse dialogue structures for a character's dialogue data."""
    # Try to find dialogues referencing this character
    dialogue_dir = BRAINS_ROOT / "Dialogues"
    character_dialogues = []

    if dialogue_dir.is_dir():
        for sub in dialogue_dir.iterdir():
            if sub.is_dir():
                for md_file in sub.glob("*.md"):
                    content = md_file.read_text(encoding="utf-8")
                    fields = _parse_frontmatter(content)
                    participants = fields.get("participants", [])
                    if isinstance(participants, list) and entity_id in participants:
                        character_dialogues.append(fields)
                    elif fields.get("primary_speaker") == entity_id:
                        character_dialogues.append(fields)

    # Also check if this is itself a dialogue entity
    entity = _read_entity("dialogue", entity_id)
    if entity:
        character_dialogues.insert(0, entity)

    # Also check for the character directly
    character = _read_entity("character", entity_id)
    char_name = ""
    if character:
        char_name = character.get("name", entity_id)

    module = _verse_module()

    lines = [
        f"# UEFN Dialogue Export",
        f"# Entity: {entity_id}",
        f"# Creative Version: {_creative_version()}",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"",
        f"using {{ /Verse.org/Simulation }}",
        f"using {{ /Fortnite.com/Devices }}",
        f"",
        f"# Dialogue node data structure",
        f"dialogue_node := struct:",
        f'    NodeId : string = ""',
        f'    Speaker : string = ""',
        f'    Text : string = ""',
        f"    Choices : []dialogue_choice = array{{}}",
        f"",
        f"dialogue_choice := struct:",
        f'    Label : string = ""',
        f'    NextNodeId : string = ""',
        f'    ConditionTag : string = ""',
        f"",
    ]

    if not character_dialogues:
        lines.extend([
            f"# No dialogue data found for '{entity_id}'.",
            f"# Create dialogue entities in Studio with this character as a participant.",
            f"",
            f"{_sanitize_verse_id(entity_id)}_dialogues : []dialogue_node = array{{}}",
        ])
    else:
        var_name = _sanitize_verse_id(entity_id) + "_dialogues"
        lines.append(f"{var_name} : []dialogue_node = array{{")

        for idx, dlg in enumerate(character_dialogues):
            dlg_name = dlg.get("name", f"dialogue_{idx}")
            speaker = dlg.get("primary_speaker", entity_id)
            tree_type = dlg.get("tree_type", "conversation")
            lines.append(f"    dialogue_node{{")
            lines.append(f'        NodeId := "{_sanitize_verse_id(dlg_name)}"')
            lines.append(f'        Speaker := "{_escape_verse_string(str(speaker))}"')
            lines.append(f'        Text := "{_escape_verse_string(str(dlg_name))} [{tree_type}]"')
            lines.append(f"        Choices := array{{}}")
            lines.append(f"    }}")
            if idx < len(character_dialogues) - 1:
                lines[-1] += ","

        lines.append(f"}}")

    return "\n".join(lines)


def _generate_island_metadata(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate Creative island metadata from a collection of entities."""
    characters = [e for e in entities if e.get("_entity_type") == "character"]
    locations = [e for e in entities if e.get("_entity_type") == "location"]
    quests = [e for e in entities if e.get("_entity_type") == "quest"]
    items = [e for e in entities if e.get("_entity_type") == "item"]
    factions = [e for e in entities if e.get("_entity_type") == "faction"]

    return {
        "island_metadata": {
            "generator": "city-of-brains-uefn-exporter",
            "creative_version": _creative_version(),
            "verse_module": _verse_module(),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        },
        "npcs": [
            {
                "id": _sanitize_verse_id(e.get("_entity_id", "")),
                "name": e.get("name", e.get("_entity_id", "")),
                "age": e.get("age"),
                "gender": e.get("gender", ""),
                "faction": e.get("faction", ""),
                "primary_location": e.get("primary_location", ""),
                "behavior": _get_setting("npc_behavior_template", "dialogue"),
            }
            for e in characters
        ],
        "locations": [
            {
                "id": _sanitize_verse_id(e.get("_entity_id", "")),
                "name": e.get("name", e.get("_entity_id", "")),
                "district": e.get("district", ""),
            }
            for e in locations
        ],
        "quests": [
            {
                "id": _sanitize_verse_id(e.get("_entity_id", "")),
                "name": e.get("name", e.get("_entity_id", "")),
            }
            for e in quests
        ],
        "items": [
            {
                "id": _sanitize_verse_id(e.get("_entity_id", "")),
                "name": e.get("name", e.get("_entity_id", "")),
            }
            for e in items
        ],
        "factions": [
            {
                "id": _sanitize_verse_id(e.get("_entity_id", "")),
                "name": e.get("name", e.get("_entity_id", "")),
            }
            for e in factions
        ],
        "summary": {
            "total_npcs": len(characters),
            "total_locations": len(locations),
            "total_quests": len(quests),
            "total_items": len(items),
            "total_factions": len(factions),
        },
    }


# ─── Request Models ──────────────────────────────────────────────────

class BatchExportRequest(BaseModel):
    """Request body for batch export."""
    entity_type: str
    entity_ids: List[str] = []
    include_class: bool = True
    include_instances: bool = True
    include_devices: bool = True
    include_dialogue: bool = False


class ExportResult(BaseModel):
    """Single export result."""
    entity_type: str
    entity_id: str
    verse_code: str
    device_code: Optional[str] = None
    dialogue_code: Optional[str] = None


# ─── API Routes ───────────────────────────────────────────────────────

@router.get("/")
async def plugin_status():
    """Plugin status and configuration overview."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("uefn-exporter")
    entity_counts = {}
    for etype in ENTITY_TYPE_DIRS:
        entities = _list_entities(etype)
        if entities:
            entity_counts[etype] = len(entities)

    return {
        "plugin": "uefn-exporter",
        "version": "0.2.0",
        "status": "ok",
        "creative_version": _creative_version(),
        "verse_module": _verse_module(),
        "settings": settings,
        "available_entity_types": list(ENTITY_TYPE_DIRS.keys()),
        "entity_counts": entity_counts,
    }


@router.get("/entity-types")
async def list_entity_types():
    """List all available entity types and their entity counts."""
    result = []
    for etype, dir_name in ENTITY_TYPE_DIRS.items():
        entities = _list_entities(etype)
        result.append({
            "entity_type": etype,
            "directory": dir_name,
            "count": len(entities),
            "entity_ids": entities[:50],  # Cap at 50 for response size
        })
    return {"entity_types": result}


@router.get("/entities/{entity_type}")
async def list_entities_of_type(entity_type: str):
    """List all entities of a specific type."""
    if entity_type not in ENTITY_TYPE_DIRS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown entity type: {entity_type}")
    entities = _list_entities(entity_type)
    return {
        "entity_type": entity_type,
        "count": len(entities),
        "entity_ids": entities,
    }


@router.get("/verse/{entity_type}", response_class=PlainTextResponse)
async def generate_verse_class(entity_type: str):
    """Generate a Verse class definition for an entity type."""
    if entity_type not in ENTITY_TYPE_DIRS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown entity type: {entity_type}")
    code = _generate_verse_class(entity_type)
    return PlainTextResponse(content=code, media_type="text/plain")


@router.get("/preview/{entity_type}/{entity_id}", response_class=PlainTextResponse)
async def preview_verse_instance(entity_type: str, entity_id: str):
    """Preview the Verse data for a specific entity (read-only, no file writes)."""
    if entity_type not in ENTITY_TYPE_DIRS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown entity type: {entity_type}")
    code = _generate_verse_instance(entity_type, entity_id)
    return PlainTextResponse(content=code, media_type="text/plain")


@router.get("/preview-device/{entity_type}/{entity_id}", response_class=PlainTextResponse)
async def preview_device_config(entity_type: str, entity_id: str):
    """Preview a UEFN device configuration for an entity."""
    if entity_type not in ENTITY_TYPE_DIRS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown entity type: {entity_type}")
    code = _generate_device_config(entity_type, entity_id)
    return PlainTextResponse(content=code, media_type="text/plain")


@router.post("/export/{entity_type}/{entity_id}")
async def export_entity(entity_type: str, entity_id: str,
                        include_device: bool = Query(True),
                        include_dialogue: bool = Query(False)):
    """Export a single entity as Verse code with optional device config and dialogue."""
    if entity_type not in ENTITY_TYPE_DIRS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown entity type: {entity_type}")

    verse_code = _generate_verse_instance(entity_type, entity_id)
    device_code = None
    dialogue_code = None

    if include_device:
        try:
            device_code = _generate_device_config(entity_type, entity_id)
        except Exception as exc:
            logger.warning("Failed to generate device config: %s", exc)

    if include_dialogue and entity_type == "character":
        try:
            dialogue_code = _generate_dialogue_verse(entity_id)
        except Exception as exc:
            logger.warning("Failed to generate dialogue: %s", exc)

    # Optionally write to UEFN project path
    project_path = _get_setting("uefn_project_path", "")
    files_written = []

    if project_path and os.path.isdir(project_path):
        verse_dir = os.path.join(project_path, "Content", "Verse",
                                 _verse_module(), entity_type.capitalize())
        os.makedirs(verse_dir, exist_ok=True)

        # Write instance
        instance_file = os.path.join(verse_dir, f"{_sanitize_verse_id(entity_id)}.verse")
        with open(instance_file, "w", encoding="utf-8") as f:
            f.write(verse_code)
        files_written.append(instance_file)

        # Write device
        if device_code:
            device_file = os.path.join(verse_dir, f"{_sanitize_verse_id(entity_id)}_device.verse")
            with open(device_file, "w", encoding="utf-8") as f:
                f.write(device_code)
            files_written.append(device_file)

        # Write dialogue
        if dialogue_code:
            dlg_file = os.path.join(verse_dir, f"{_sanitize_verse_id(entity_id)}_dialogue.verse")
            with open(dlg_file, "w", encoding="utf-8") as f:
                f.write(dialogue_code)
            files_written.append(dlg_file)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "verse_code": verse_code,
        "device_code": device_code,
        "dialogue_code": dialogue_code,
        "files_written": files_written,
        "exported_at": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/batch-export")
async def batch_export(req: BatchExportRequest):
    """Batch export multiple entities of a given type."""
    if req.entity_type not in ENTITY_TYPE_DIRS:
        raise HTTPException(status_code=400,
                            detail=f"Unknown entity type: {req.entity_type}")

    # If no IDs specified, export all entities of this type
    entity_ids = req.entity_ids or _list_entities(req.entity_type)

    results = []
    class_code = None
    errors = []

    # Generate class definition
    if req.include_class:
        class_code = _generate_verse_class(req.entity_type)

    for eid in entity_ids:
        try:
            verse_code = ""
            device_code = None
            dialogue_code = None

            if req.include_instances:
                verse_code = _generate_verse_instance(req.entity_type, eid)

            if req.include_devices:
                try:
                    device_code = _generate_device_config(req.entity_type, eid)
                except Exception:
                    pass

            if req.include_dialogue and req.entity_type == "character":
                try:
                    dialogue_code = _generate_dialogue_verse(eid)
                except Exception:
                    pass

            results.append({
                "entity_id": eid,
                "verse_code": verse_code,
                "device_code": device_code,
                "dialogue_code": dialogue_code,
            })
        except Exception as exc:
            errors.append({"entity_id": eid, "error": str(exc)})

    # Optionally write to UEFN project path
    project_path = _get_setting("uefn_project_path", "")
    files_written = []

    if project_path and os.path.isdir(project_path):
        verse_dir = os.path.join(project_path, "Content", "Verse",
                                 _verse_module(), req.entity_type.capitalize())
        os.makedirs(verse_dir, exist_ok=True)

        # Write class definition
        if class_code:
            class_file = os.path.join(verse_dir, f"{req.entity_type}_data.verse")
            with open(class_file, "w", encoding="utf-8") as f:
                f.write(class_code)
            files_written.append(class_file)

        # Write each instance
        for r in results:
            eid = r["entity_id"]
            if r.get("verse_code"):
                fp = os.path.join(verse_dir, f"{_sanitize_verse_id(eid)}.verse")
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(r["verse_code"])
                files_written.append(fp)
            if r.get("device_code"):
                fp = os.path.join(verse_dir, f"{_sanitize_verse_id(eid)}_device.verse")
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(r["device_code"])
                files_written.append(fp)
            if r.get("dialogue_code"):
                fp = os.path.join(verse_dir, f"{_sanitize_verse_id(eid)}_dialogue.verse")
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(r["dialogue_code"])
                files_written.append(fp)

    # Generate island metadata
    all_entities = []
    for eid in entity_ids:
        e = _read_entity(req.entity_type, eid)
        if e:
            all_entities.append(e)

    island_meta = _generate_island_metadata(all_entities)

    return {
        "entity_type": req.entity_type,
        "total_exported": len(results),
        "total_errors": len(errors),
        "class_code": class_code,
        "results": results,
        "errors": errors,
        "files_written": files_written,
        "island_metadata": island_meta,
        "exported_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/dialogue/{entity_id}", response_class=PlainTextResponse)
async def export_dialogue(entity_id: str):
    """Export dialogue data for a character in UEFN-compatible Verse format."""
    code = _generate_dialogue_verse(entity_id)
    return PlainTextResponse(content=code, media_type="text/plain")


@router.get("/island-metadata")
async def get_island_metadata(
    entity_types: str = Query("character,location,quest,item,faction",
                              description="Comma-separated entity types to include")
):
    """Generate Creative island metadata from all entities of the specified types."""
    types = [t.strip() for t in entity_types.split(",") if t.strip()]
    all_entities = []

    for etype in types:
        if etype not in ENTITY_TYPE_DIRS:
            continue
        for eid in _list_entities(etype):
            e = _read_entity(etype, eid)
            if e:
                all_entities.append(e)

    return _generate_island_metadata(all_entities)


@router.get("/island-metadata/verse", response_class=PlainTextResponse)
async def get_island_metadata_verse(
    entity_types: str = Query("character,location,quest,item,faction",
                              description="Comma-separated entity types to include")
):
    """Generate island metadata as a Verse module with all entity data."""
    types = [t.strip() for t in entity_types.split(",") if t.strip()]
    module = _verse_module()

    lines = [
        f"# Creative Island Data Module",
        f"# Auto-generated by City of Brains UEFN Exporter",
        f"# Creative Version: {_creative_version()}",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"",
        f"using {{ /Verse.org/Simulation }}",
        f"using {{ /Fortnite.com/Devices }}",
        f"",
        f"{_sanitize_verse_id(module)}_island := module:",
        f"",
    ]

    for etype in types:
        if etype not in ENTITY_TYPE_DIRS:
            continue

        # Add class definition
        class_name = etype.capitalize() + "Data"
        template_fields = _read_template_fields(etype)

        if not template_fields:
            entities = _list_entities(etype)
            if entities:
                sample = _read_entity(etype, entities[0])
                if sample:
                    skip = {"_entity_type", "_entity_id", "_source_file",
                            "template_version", "id", "entity_type",
                            "created_date", "last_updated", "status", "primary_image"}
                    template_fields = {
                        k: _infer_verse_type(v)
                        for k, v in sample.items()
                        if k not in skip and not k.startswith("_")
                    }

        if template_fields:
            lines.append(f"    # ── {etype.capitalize()} ─────────────────")
            lines.append(f"    {_sanitize_verse_id(class_name)} := class:")
            for field_name, vtype in template_fields.items():
                safe_name = _sanitize_verse_id(field_name)
                default = VERSE_DEFAULTS.get(vtype, '""')
                lines.append(f"        {safe_name} : {vtype} = {default}")
            lines.append(f"")

            # Add instances
            for eid in _list_entities(etype)[:20]:  # Cap at 20 per type
                entity = _read_entity(etype, eid)
                if not entity:
                    continue
                var_name = _sanitize_verse_id(eid)
                lines.append(f"    {var_name} : {_sanitize_verse_id(class_name)} = {_sanitize_verse_id(class_name)}:")
                skip = {"_entity_type", "_entity_id", "_source_file",
                        "template_version", "id", "entity_type",
                        "created_date", "last_updated", "status", "primary_image"}
                for key, value in entity.items():
                    if key in skip or key.startswith("_"):
                        continue
                    safe_key = _sanitize_verse_id(key)
                    vtype = _infer_verse_type(value)
                    vval = _verse_value(value, vtype)
                    lines.append(f"        {safe_key} = {vval}")
                lines.append(f"")

    return PlainTextResponse(content="\n".join(lines), media_type="text/plain")
