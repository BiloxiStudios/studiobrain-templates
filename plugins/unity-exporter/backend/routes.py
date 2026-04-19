"""
Unity Game Exporter Plugin — Backend Routes

Generates Unity-compatible ScriptableObject .asset files, C# data class
scripts, and prefab stubs from City of Brains entity data.  Supports
single-entity export, batch export, and full C# script generation.

All entity data is read from the A:\\Brains directory tree.
"""

import hashlib
import json
import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger("plugin.unity-exporter")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BRAINS_ROOT = Path(r"A:\Brains")

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

# Default settings (overridden by plugin settings at runtime)
DEFAULT_SETTINGS = {
    "unity_project_path": "",
    "output_subdir": "Assets/Data/CityOfBrains",
    "namespace": "CityOfBrains.Data",
    "generate_enums": True,
    "export_portraits": True,
    "generate_prefab_stubs": False,
    "auto_generate_meta": True,
}

# C# type mapping for common entity field patterns
CSHARP_TYPE_MAP = {
    "name": "string",
    "title": "string",
    "description": "string",
    "summary": "string",
    "backstory": "string",
    "background": "string",
    "bio": "string",
    "notes": "string",
    "history": "string",
    "lore": "string",
    "dialogue": "string",
    "age": "int",
    "level": "int",
    "health": "int",
    "hp": "int",
    "mp": "int",
    "strength": "int",
    "dexterity": "int",
    "intelligence": "int",
    "wisdom": "int",
    "charisma": "int",
    "constitution": "int",
    "attack": "int",
    "defense": "int",
    "speed": "int",
    "weight": "float",
    "height": "float",
    "price": "float",
    "cost": "float",
    "value": "float",
    "damage": "float",
    "range": "float",
    "is_active": "bool",
    "is_alive": "bool",
    "is_hostile": "bool",
    "is_locked": "bool",
    "is_hidden": "bool",
    "active": "bool",
    "alive": "bool",
    "hostile": "bool",
    "locked": "bool",
    "hidden": "bool",
    "enabled": "bool",
    "gender": "string",
    "race": "string",
    "class": "string",
    "faction": "string",
    "occupation": "string",
    "location": "string",
    "portrait": "Sprite",
    "icon": "Sprite",
    "image": "Sprite",
    "prefab": "GameObject",
    "tags": "List<string>",
    "items": "List<string>",
    "allies": "List<string>",
    "enemies": "List<string>",
    "skills": "List<string>",
    "abilities": "List<string>",
    "inventory": "List<string>",
    "relationships": "List<string>",
    "connections": "List<string>",
}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class BatchExportRequest(BaseModel):
    entity_type: str
    entity_ids: List[str]
    output_path: Optional[str] = None

class GenerateScriptsRequest(BaseModel):
    entity_types: Optional[List[str]] = None
    output_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_settings() -> dict:
    """Load plugin settings from the DB-backed settings service."""
    from services.plugin_settings_service import get_all_settings
    return {**DEFAULT_SETTINGS, **get_all_settings("unity-exporter")}


def _entity_dir(entity_type: str, entity_id: str) -> Path:
    """Return the directory containing an entity's files."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
    folder, _prefix = mapping
    return BRAINS_ROOT / folder / entity_id


def _entity_file(entity_type: str, entity_id: str) -> Path:
    """Resolve the canonical markdown file for an entity."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
    folder, prefix = mapping
    return BRAINS_ROOT / folder / entity_id / f"{prefix}{entity_id}.md"


def _parse_entity_markdown(filepath: Path) -> Dict[str, Any]:
    """Parse a Studio entity markdown file.

    Entity markdown files have YAML frontmatter between --- delimiters,
    followed by freeform markdown body content.
    """
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Entity file not found: {filepath.name}")

    text = filepath.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    frontmatter = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}
            body = parts[2].strip()

    return {
        "frontmatter": frontmatter,
        "body": body,
        "raw": text,
    }


def _find_portrait(entity_type: str, entity_id: str) -> Optional[Path]:
    """Find the portrait image for an entity if it exists."""
    entity_dir = _entity_dir(entity_type, entity_id)
    if not entity_dir.exists():
        return None
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        for pattern in (f"portrait{ext}", f"*portrait*{ext}", f"*thumb*{ext}", f"*avatar*{ext}"):
            matches = list(entity_dir.glob(pattern))
            if matches:
                return matches[0]
    # Fallback: any image in the directory
    for ext in (".png", ".jpg", ".jpeg"):
        images = list(entity_dir.glob(f"*{ext}"))
        if images:
            return images[0]
    return None


def _to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase for C# class names."""
    s = re.sub(r'[^a-zA-Z0-9_\s-]', '', s)
    words = re.split(r'[\s_-]+', s)
    return ''.join(w.capitalize() for w in words if w)


def _to_camel_case(s: str) -> str:
    """Convert a string to camelCase for C# field names."""
    pascal = _to_pascal_case(s)
    if not pascal:
        return "unnamed"
    return pascal[0].lower() + pascal[1:]


def _infer_csharp_type(key: str, value: Any) -> str:
    """Infer the C# type for a field based on its key name and value."""
    key_lower = key.lower().replace(" ", "_")

    # Check explicit mapping first
    if key_lower in CSHARP_TYPE_MAP:
        return CSHARP_TYPE_MAP[key_lower]

    # Infer from value type
    if isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, list):
        if value and isinstance(value[0], int):
            return "List<int>"
        elif value and isinstance(value[0], float):
            return "List<float>"
        return "List<string>"
    elif isinstance(value, dict):
        return "string"  # Serialize nested objects as JSON string

    return "string"


def _stable_guid(seed_string: str) -> str:
    """Generate a stable Unity-compatible GUID from a seed string."""
    return hashlib.md5(seed_string.encode("utf-8")).hexdigest()


def _stable_file_id(seed_string: str) -> int:
    """Generate a stable Unity fileID from a seed string."""
    h = hashlib.sha256(seed_string.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big") % 2147483647


def _format_csharp_value(value: Any, csharp_type: str) -> str:
    """Format a Python value as a C# literal for ScriptableObject YAML."""
    if value is None:
        if csharp_type == "string":
            return ""
        elif csharp_type == "int":
            return "0"
        elif csharp_type == "float":
            return "0"
        elif csharp_type == "bool":
            return "0"
        return ""

    if csharp_type == "bool":
        return "1" if value else "0"
    elif csharp_type == "int":
        try:
            return str(int(value))
        except (ValueError, TypeError):
            return "0"
    elif csharp_type == "float":
        try:
            return str(float(value))
        except (ValueError, TypeError):
            return "0"
    elif csharp_type.startswith("List<"):
        if isinstance(value, list):
            return json.dumps(value)
        return "[]"
    elif csharp_type in ("Sprite", "GameObject"):
        return "{fileID: 0}"
    else:
        return str(value) if value else ""


# ---------------------------------------------------------------------------
# C# Code Generation
# ---------------------------------------------------------------------------

def _generate_csharp_class(entity_type: str, fields: Dict[str, Any], settings: dict) -> str:
    """Generate a C# ScriptableObject class for an entity type."""
    namespace = settings.get("namespace", "CityOfBrains.Data")
    class_name = _to_pascal_case(entity_type) + "Data"
    menu_name = _to_pascal_case(entity_type)

    # Build field definitions
    field_lines = []
    serialized_fields = []

    for key, value in fields.items():
        if key.startswith("_") or key in ("id", "type", "template"):
            continue

        csharp_type = _infer_csharp_type(key, value)
        field_name = _to_camel_case(key)

        # Avoid C# reserved words
        if field_name in ("class", "event", "object", "string", "int", "float", "bool", "new", "override", "base"):
            field_name = f"entity{field_name.capitalize()}"

        # Use [TextArea] for long text fields
        is_textarea = isinstance(value, str) and len(str(value)) > 100
        is_textarea = is_textarea or key.lower() in ("description", "backstory", "background", "bio", "notes", "history", "lore", "dialogue", "summary")

        if csharp_type in ("Sprite", "GameObject"):
            serialized_fields.append((csharp_type, field_name, False))
        elif is_textarea and csharp_type == "string":
            serialized_fields.append((csharp_type, field_name, True))
        else:
            field_lines.append((csharp_type, field_name))

    # Build the class
    lines = []
    lines.append(f"// Auto-generated by City of Brains Studio — Unity Exporter")
    lines.append(f"// Entity Type: {entity_type}")
    lines.append(f"// Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"// DO NOT EDIT — regenerate from Studio if schema changes")
    lines.append(f"")
    lines.append(f"using System;")
    lines.append(f"using System.Collections.Generic;")
    lines.append(f"using UnityEngine;")
    lines.append(f"")
    lines.append(f"namespace {namespace}")
    lines.append(f"{{")
    lines.append(f"    [CreateAssetMenu(fileName = \"New {menu_name}\", menuName = \"CityOfBrains/{menu_name}\")]")
    lines.append(f"    public class {class_name} : ScriptableObject")
    lines.append(f"    {{")
    lines.append(f"        [Header(\"Identity\")]")
    lines.append(f"        public string entityId;")
    lines.append(f"        public string entityName;")
    lines.append(f"")

    # Group fields by category
    current_header = None
    for csharp_type, field_name in field_lines:
        # Determine header category
        header = _categorize_field(field_name)
        if header != current_header:
            lines.append(f"")
            lines.append(f"        [Header(\"{header}\")]")
            current_header = header
        lines.append(f"        public {csharp_type} {field_name};")

    # Serialized / special fields
    if serialized_fields:
        lines.append(f"")
        lines.append(f"        [Header(\"Assets\")]")
        for csharp_type, field_name, is_textarea in serialized_fields:
            if is_textarea:
                lines.append(f"        [TextArea(3, 10)]")
                lines.append(f"        public {csharp_type} {field_name};")
            else:
                lines.append(f"        public {csharp_type} {field_name};")

    lines.append(f"    }}")
    lines.append(f"}}")
    lines.append(f"")

    return "\n".join(lines)


def _categorize_field(field_name: str) -> str:
    """Categorize a field name into a Unity Inspector header group."""
    fn = field_name.lower()
    if any(w in fn for w in ("name", "title", "id", "type", "tag", "label")):
        return "Core"
    if any(w in fn for w in ("age", "gender", "race", "height", "weight", "appearance")):
        return "Attributes"
    if any(w in fn for w in ("str", "dex", "int", "wis", "cha", "con", "hp", "mp", "health", "mana",
                              "attack", "defense", "speed", "level", "damage")):
        return "Stats"
    if any(w in fn for w in ("description", "backstory", "bio", "background", "history", "lore", "summary", "notes")):
        return "Narrative"
    if any(w in fn for w in ("portrait", "icon", "image", "sprite", "prefab", "model", "mesh")):
        return "Assets"
    if any(w in fn for w in ("location", "position", "region", "district", "zone", "area")):
        return "Location"
    if any(w in fn for w in ("faction", "ally", "enemy", "relation", "connection", "friend", "rival")):
        return "Relationships"
    if any(w in fn for w in ("item", "inventory", "equipment", "weapon", "armor", "loot")):
        return "Inventory"
    if any(w in fn for w in ("quest", "objective", "reward", "task", "mission")):
        return "Quests"
    if any(w in fn for w in ("skill", "ability", "spell", "power", "talent")):
        return "Abilities"
    return "Properties"


def _generate_scriptable_object_yaml(
    entity_type: str,
    entity_id: str,
    entity_data: Dict[str, Any],
    settings: dict,
) -> str:
    """Generate a Unity .asset file (serialized ScriptableObject) in YAML format."""
    namespace = settings.get("namespace", "CityOfBrains.Data")
    class_name = _to_pascal_case(entity_type) + "Data"
    frontmatter = entity_data.get("frontmatter", {})

    # Generate stable GUIDs
    script_guid = _stable_guid(f"{namespace}.{class_name}")
    file_id = _stable_file_id(f"{entity_type}/{entity_id}")

    # Build the YAML
    lines = []
    lines.append(f"%YAML 1.1")
    lines.append(f"%TAG !u! tag:unity3d.com,2011:")
    lines.append(f"--- !u!114 &{file_id}")
    lines.append(f"MonoBehaviour:")
    lines.append(f"  m_ObjectHideFlags: 0")
    lines.append(f"  m_CorrespondingSourceObject: {{fileID: 0}}")
    lines.append(f"  m_PrefabInstance: {{fileID: 0}}")
    lines.append(f"  m_PrefabAsset: {{fileID: 0}}")
    lines.append(f"  m_GameObject: {{fileID: 0}}")
    lines.append(f"  m_Enabled: 1")
    lines.append(f"  m_EditorHideFlags: 0")
    lines.append(f"  m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}")
    lines.append(f"  m_Name: {entity_id}")
    lines.append(f"  m_EditorClassIdentifier: ")

    # Identity fields
    entity_name = frontmatter.get("name", frontmatter.get("title", entity_id))
    lines.append(f"  entityId: {entity_id}")
    lines.append(f"  entityName: {entity_name}")

    # Data fields from frontmatter
    for key, value in frontmatter.items():
        if key.startswith("_") or key in ("id", "type", "template", "name", "title"):
            continue

        field_name = _to_camel_case(key)
        csharp_type = _infer_csharp_type(key, value)

        # Format value for Unity YAML
        formatted = _format_csharp_value(value, csharp_type)

        if isinstance(value, list):
            lines.append(f"  {field_name}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"  {field_name}: {json.dumps(value)}")
        elif isinstance(value, bool):
            lines.append(f"  {field_name}: {1 if value else 0}")
        elif isinstance(value, (int, float)):
            lines.append(f"  {field_name}: {value}")
        else:
            # Escape multiline strings for Unity YAML
            str_val = str(value) if value is not None else ""
            if "\n" in str_val:
                str_val = str_val.replace("\n", "\\n")
            lines.append(f"  {field_name}: {str_val}")

    lines.append(f"")
    return "\n".join(lines)


def _generate_enum_code(entity_type: str, field_name: str, values: List[str], namespace: str) -> str:
    """Generate a C# enum from a list of string values."""
    enum_name = _to_pascal_case(field_name)

    lines = []
    lines.append(f"// Auto-generated by City of Brains Studio — Unity Exporter")
    lines.append(f"// Enum source: {entity_type}.{field_name}")
    lines.append(f"")
    lines.append(f"namespace {namespace}")
    lines.append(f"{{")
    lines.append(f"    public enum {enum_name}")
    lines.append(f"    {{")

    for i, val in enumerate(values):
        safe_name = _to_pascal_case(val) if val else f"Value{i}"
        if not safe_name:
            safe_name = f"Value{i}"
        comma = "," if i < len(values) - 1 else ""
        lines.append(f"        {safe_name}{comma}")

    lines.append(f"    }}")
    lines.append(f"}}")
    lines.append(f"")

    return "\n".join(lines)


def _collect_all_fields_for_type(entity_type: str) -> Dict[str, Any]:
    """Scan all entities of a type and collect a union of all fields with sample values."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        return {}

    folder, prefix = mapping
    folder_path = BRAINS_ROOT / folder
    if not folder_path.exists():
        return {}

    all_fields: Dict[str, Any] = {}

    for entity_dir in folder_path.iterdir():
        if not entity_dir.is_dir():
            continue
        md_file = entity_dir / f"{prefix}{entity_dir.name}.md"
        if not md_file.exists():
            continue

        try:
            parsed = _parse_entity_markdown(md_file)
            fm = parsed.get("frontmatter", {})
            for key, value in fm.items():
                if key not in all_fields or all_fields[key] is None:
                    all_fields[key] = value
        except Exception:
            continue

    return all_fields


def _list_entities_for_type(entity_type: str) -> List[Dict[str, Any]]:
    """List all entities of a given type with basic info."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        return []

    folder, prefix = mapping
    folder_path = BRAINS_ROOT / folder
    if not folder_path.exists():
        return []

    entities = []
    for entity_dir in sorted(folder_path.iterdir()):
        if not entity_dir.is_dir():
            continue
        md_file = entity_dir / f"{prefix}{entity_dir.name}.md"
        if not md_file.exists():
            continue

        try:
            parsed = _parse_entity_markdown(md_file)
            fm = parsed.get("frontmatter", {})
            name = fm.get("name", fm.get("title", entity_dir.name))
            portrait = _find_portrait(entity_type, entity_dir.name)
            entities.append({
                "id": entity_dir.name,
                "name": name,
                "has_portrait": portrait is not None,
                "field_count": len([k for k in fm.keys() if not k.startswith("_")]),
            })
        except Exception:
            entities.append({
                "id": entity_dir.name,
                "name": entity_dir.name,
                "has_portrait": False,
                "field_count": 0,
            })

    return entities


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status and capability summary."""
    settings = _get_settings()
    unity_path = settings.get("unity_project_path", "")
    has_project = bool(unity_path) and Path(unity_path).exists() if unity_path else False

    available_types = []
    total_entities = 0
    for etype in ENTITY_MAP:
        entities = _list_entities_for_type(etype)
        if entities:
            available_types.append({"type": etype, "count": len(entities)})
            total_entities += len(entities)

    return {
        "plugin": "unity-exporter",
        "version": "0.2.0",
        "status": "ok",
        "unity_project_configured": has_project,
        "unity_project_path": unity_path,
        "namespace": settings.get("namespace", "CityOfBrains.Data"),
        "output_subdir": settings.get("output_subdir", "Assets/Data/CityOfBrains"),
        "available_entity_types": available_types,
        "total_entities": total_entities,
    }


@router.get("/entities/{entity_type}")
async def list_entities(entity_type: str):
    """List all entities of a given type available for export."""
    if entity_type not in ENTITY_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    entities = _list_entities_for_type(entity_type)
    return {
        "entity_type": entity_type,
        "count": len(entities),
        "entities": entities,
    }


@router.get("/preview/{entity_type}/{entity_id}")
async def preview_scriptable_object(entity_type: str, entity_id: str, format: str = "yaml"):
    """Preview the generated ScriptableObject for an entity.

    Returns the .asset YAML or a JSON representation of what would be exported.
    """
    entity_path = _entity_file(entity_type, entity_id)
    parsed = _parse_entity_markdown(entity_path)
    settings = _get_settings()

    asset_yaml = _generate_scriptable_object_yaml(entity_type, entity_id, parsed, settings)

    if format == "json":
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "frontmatter": parsed["frontmatter"],
            "preview_format": "json",
            "class_name": _to_pascal_case(entity_type) + "Data",
            "namespace": settings.get("namespace", "CityOfBrains.Data"),
        }

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "preview_format": "yaml",
        "asset_content": asset_yaml,
        "class_name": _to_pascal_case(entity_type) + "Data",
        "file_name": f"{entity_id}.asset",
    }


@router.get("/csharp/{entity_type}")
async def generate_csharp_class(entity_type: str):
    """Generate the C# ScriptableObject data class for an entity type.

    Scans all entities of the type to build a union of all fields.
    """
    if entity_type not in ENTITY_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    settings = _get_settings()
    all_fields = _collect_all_fields_for_type(entity_type)

    if not all_fields:
        # Return a minimal class even if no entities exist yet
        all_fields = {"name": "Example", "description": ""}

    csharp_code = _generate_csharp_class(entity_type, all_fields, settings)
    class_name = _to_pascal_case(entity_type) + "Data"

    return {
        "entity_type": entity_type,
        "class_name": class_name,
        "file_name": f"{class_name}.cs",
        "field_count": len([k for k in all_fields if not k.startswith("_") and k not in ("id", "type", "template")]),
        "csharp_code": csharp_code,
        "namespace": settings.get("namespace", "CityOfBrains.Data"),
    }


@router.post("/export/{entity_type}/{entity_id}")
async def export_entity(entity_type: str, entity_id: str, output_path: Optional[str] = None):
    """Export a single entity as a Unity .asset ScriptableObject file.

    Writes the .asset file (and optionally the portrait) to the configured
    Unity project path or the specified output path.
    """
    settings = _get_settings()
    entity_path = _entity_file(entity_type, entity_id)
    parsed = _parse_entity_markdown(entity_path)

    # Determine output directory
    if output_path:
        out_dir = Path(output_path)
    else:
        unity_path = settings.get("unity_project_path", "")
        if not unity_path:
            # Fallback: export to a local _exports directory
            out_dir = BRAINS_ROOT / "_Plugins" / "unity-exporter" / "_exports" / entity_type
        else:
            subdir = settings.get("output_subdir", "Assets/Data/CityOfBrains")
            out_dir = Path(unity_path) / subdir / _to_pascal_case(entity_type)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate and write .asset file
    asset_yaml = _generate_scriptable_object_yaml(entity_type, entity_id, parsed, settings)
    asset_file = out_dir / f"{entity_id}.asset"
    asset_file.write_text(asset_yaml, encoding="utf-8")

    exported_files = [str(asset_file)]

    # Generate .meta file for stable GUID
    if settings.get("auto_generate_meta", True):
        guid = _stable_guid(f"{entity_type}/{entity_id}")
        meta_content = (
            f"fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            f"NativeFormatImporter:\n"
            f"  externalObjects: {{}}\n"
            f"  mainObjectFileID: 11400000\n"
            f"  userData: \n"
            f"  assetBundleName: \n"
            f"  assetBundleVariant: \n"
        )
        meta_file = out_dir / f"{entity_id}.asset.meta"
        meta_file.write_text(meta_content, encoding="utf-8")
        exported_files.append(str(meta_file))

    # Copy portrait if enabled
    if settings.get("export_portraits", True):
        portrait = _find_portrait(entity_type, entity_id)
        if portrait:
            portraits_dir = out_dir / "Portraits"
            portraits_dir.mkdir(parents=True, exist_ok=True)
            dest = portraits_dir / f"{entity_id}{portrait.suffix}"
            shutil.copy2(str(portrait), str(dest))
            exported_files.append(str(dest))

            # Meta for portrait
            if settings.get("auto_generate_meta", True):
                p_guid = _stable_guid(f"portrait/{entity_type}/{entity_id}")
                p_meta = (
                    f"fileFormatVersion: 2\n"
                    f"guid: {p_guid}\n"
                    f"TextureImporter:\n"
                    f"  internalIDToNameTable: []\n"
                    f"  externalObjects: {{}}\n"
                    f"  serializedVersion: 12\n"
                    f"  mipmaps:\n"
                    f"    mipMapMode: 0\n"
                    f"    enableMipMap: 0\n"
                    f"  spriteMode: 1\n"
                    f"  spritePixelsToUnits: 100\n"
                    f"  textureType: 8\n"
                    f"  textureShape: 1\n"
                    f"  isReadable: 0\n"
                )
                p_meta_file = portraits_dir / f"{entity_id}{portrait.suffix}.meta"
                p_meta_file.write_text(p_meta, encoding="utf-8")
                exported_files.append(str(p_meta_file))

    logger.info("[unity-exporter] Exported %s/%s -> %s", entity_type, entity_id, asset_file)

    return {
        "status": "ok",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "exported_files": exported_files,
        "asset_path": str(asset_file),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/batch-export")
async def batch_export(req: BatchExportRequest):
    """Export multiple entities of a given type as .asset files."""
    if req.entity_type not in ENTITY_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {req.entity_type}")

    results = []
    errors = []

    for eid in req.entity_ids:
        try:
            result = await export_entity(req.entity_type, eid, req.output_path)
            results.append(result)
        except HTTPException as e:
            errors.append({"entity_id": eid, "error": e.detail})
        except Exception as e:
            errors.append({"entity_id": eid, "error": str(e)})

    logger.info(
        "[unity-exporter] Batch export %s: %d succeeded, %d failed",
        req.entity_type, len(results), len(errors),
    )

    return {
        "status": "ok",
        "entity_type": req.entity_type,
        "total_requested": len(req.entity_ids),
        "exported": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/generate-scripts")
async def generate_scripts(req: GenerateScriptsRequest):
    """Generate all C# ScriptableObject scripts for the requested entity types.

    If no entity_types are specified, generates for all types that have entities.
    Writes .cs files to the Unity project Scripts folder or the specified output path.
    """
    settings = _get_settings()
    target_types = req.entity_types or list(ENTITY_MAP.keys())

    # Determine output directory for scripts
    if req.output_path:
        scripts_dir = Path(req.output_path)
    else:
        unity_path = settings.get("unity_project_path", "")
        if not unity_path:
            scripts_dir = BRAINS_ROOT / "_Plugins" / "unity-exporter" / "_exports" / "Scripts"
        else:
            subdir = settings.get("output_subdir", "Assets/Data/CityOfBrains")
            scripts_dir = Path(unity_path) / subdir / "Scripts"

    scripts_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    enums_generated = []

    for etype in target_types:
        if etype not in ENTITY_MAP:
            continue

        all_fields = _collect_all_fields_for_type(etype)
        if not all_fields:
            continue

        # Generate the main data class
        csharp_code = _generate_csharp_class(etype, all_fields, settings)
        class_name = _to_pascal_case(etype) + "Data"
        script_file = scripts_dir / f"{class_name}.cs"
        script_file.write_text(csharp_code, encoding="utf-8")

        # Generate .meta for the script
        if settings.get("auto_generate_meta", True):
            s_guid = _stable_guid(f"{settings.get('namespace', 'CityOfBrains.Data')}.{class_name}")
            s_meta = (
                f"fileFormatVersion: 2\n"
                f"guid: {s_guid}\n"
                f"MonoImporter:\n"
                f"  externalObjects: {{}}\n"
                f"  serializedVersion: 2\n"
                f"  defaultReferences: []\n"
                f"  executionOrder: 0\n"
                f"  icon: {{instanceID: 0}}\n"
                f"  userData: \n"
                f"  assetBundleName: \n"
                f"  assetBundleVariant: \n"
            )
            meta_file = scripts_dir / f"{class_name}.cs.meta"
            meta_file.write_text(s_meta, encoding="utf-8")

        generated.append({
            "entity_type": etype,
            "class_name": class_name,
            "file": str(script_file),
            "field_count": len([k for k in all_fields if not k.startswith("_") and k not in ("id", "type", "template")]),
        })

        # Generate enums if enabled
        if settings.get("generate_enums", True):
            namespace = settings.get("namespace", "CityOfBrains.Data")
            for key, value in all_fields.items():
                if isinstance(value, str) and key.lower() in ("gender", "race", "class", "faction", "rarity", "element", "status", "alignment", "category"):
                    # Collect all unique values across entities
                    unique_values = set()
                    mapping = ENTITY_MAP[etype]
                    folder_path = BRAINS_ROOT / mapping[0]
                    if folder_path.exists():
                        for edir in folder_path.iterdir():
                            if not edir.is_dir():
                                continue
                            md = edir / f"{mapping[1]}{edir.name}.md"
                            if md.exists():
                                try:
                                    p = _parse_entity_markdown(md)
                                    v = p["frontmatter"].get(key)
                                    if v and isinstance(v, str):
                                        unique_values.add(v)
                                except Exception:
                                    pass

                    if len(unique_values) >= 2:
                        enum_code = _generate_enum_code(etype, key, sorted(unique_values), namespace)
                        enum_name = _to_pascal_case(key)
                        enum_file = scripts_dir / f"{enum_name}.cs"
                        enum_file.write_text(enum_code, encoding="utf-8")
                        enums_generated.append({
                            "enum_name": enum_name,
                            "field": key,
                            "values": sorted(unique_values),
                            "file": str(enum_file),
                        })

    logger.info(
        "[unity-exporter] Generated %d scripts, %d enums",
        len(generated), len(enums_generated),
    )

    return {
        "status": "ok",
        "scripts_directory": str(scripts_dir),
        "scripts_generated": len(generated),
        "enums_generated": len(enums_generated),
        "scripts": generated,
        "enums": enums_generated,
        "namespace": settings.get("namespace", "CityOfBrains.Data"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/export-history")
async def get_export_history():
    """Return the recent export activity log."""
    log_file = BRAINS_ROOT / "_Plugins" / "unity-exporter" / "_export_log.json"
    if not log_file.exists():
        return {"exports": [], "total": 0}

    try:
        data = json.loads(log_file.read_text(encoding="utf-8"))
        exports = data.get("exports", [])
        return {"exports": exports[-50:], "total": len(exports)}
    except Exception:
        return {"exports": [], "total": 0}
