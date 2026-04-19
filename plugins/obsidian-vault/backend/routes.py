"""
Obsidian Vault Bridge Plugin -- backend routes.

Provides endpoints for exporting City of Brains entities to an
Obsidian-compatible vault with wikilinks, YAML frontmatter, and
relationship graph preservation.
"""

import json
import logging
import os
import re
import shutil
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import yaml
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger("plugin.obsidian-vault")

router = APIRouter()

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SETTINGS_FILE = os.path.join(DATA_ROOT, "_Plugins", "_plugin_settings.json")
EXPORT_LOG_FILE = os.path.join(PLUGIN_DIR, "export_log.json")

# Map of entity_type (singular, lowercase) -> (directory name, file prefix)
ENTITY_TYPE_MAP = {
    "character":  ("Characters", "CH"),
    "faction":    ("Factions",   "FAC"),
    "location":   ("Locations",  "LOC"),
    "item":       ("Items",      "ITEM"),
    "district":   ("Districts",  "DIST"),
    "brand":      ("Brands",     "BR"),
    "quest":      ("Quests",     "QST"),
    "event":      ("Events",     "EV"),
    "dialogue":   ("Dialogues",  "DLG"),
    "campaign":   ("Campaigns",  "CMP"),
    "job":        ("Jobs",       "JOB"),
}

# Relationship field names that may contain entity references
RELATIONSHIP_FIELDS = [
    "family", "friends", "enemies", "romantic", "allies",
    "neutral", "trade_partners", "leadership", "primary_npcs",
    "associated_brands", "notable_clients_and_contacts",
]

# Fields that contain a single entity reference string
SINGLE_REF_FIELDS = [
    "faction", "primary_location", "district", "parent_location",
    "primary_brand", "faction_control",
]


# ---------------------------------------------------------------------------
# Helpers -- settings
# ---------------------------------------------------------------------------

def _load_settings() -> Dict[str, Any]:
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


def _save_settings(settings: Dict[str, Any]):
    """Persist plugin settings."""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        data = {"plugins": {}}
    if "plugins" not in data:
        data["plugins"] = {}
    data["plugins"]["obsidian-vault"] = settings
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def _get_vault_path() -> str:
    """Return validated vault path or raise."""
    settings = _load_settings()
    vault_path = settings.get("vault_path", "").strip()
    if not vault_path:
        raise HTTPException(status_code=400, detail="Vault path not configured. Set it in plugin settings.")
    return vault_path


# ---------------------------------------------------------------------------
# Helpers -- export log
# ---------------------------------------------------------------------------

def _load_export_log() -> Dict[str, Any]:
    try:
        with open(EXPORT_LOG_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_export_log(log: Dict[str, Any]):
    with open(EXPORT_LOG_FILE, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2)


def _record_export(entity_type: str, entity_id: str, link_count: int, vault_file: str):
    log = _load_export_log()
    key = f"{entity_type}/{entity_id}"
    log[key] = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "link_count": link_count,
        "vault_file": vault_file,
    }
    _save_export_log(log)


# ---------------------------------------------------------------------------
# Helpers -- entity loading
# ---------------------------------------------------------------------------

def _find_entity_file(entity_type: str, entity_id: str) -> Optional[str]:
    """Locate the markdown file for the given entity."""
    mapping = ENTITY_TYPE_MAP.get(entity_type)
    if not mapping:
        return None
    dir_name, prefix = mapping
    entity_dir = os.path.join(DATA_ROOT, dir_name, entity_id)
    if not os.path.isdir(entity_dir):
        return None
    expected = f"{prefix}_{entity_id}.md"
    path = os.path.join(entity_dir, expected)
    if os.path.isfile(path):
        return path
    # Fallback: look for any .md with the prefix
    for fname in os.listdir(entity_dir):
        if fname.startswith(prefix + "_") and fname.endswith(".md"):
            return os.path.join(entity_dir, fname)
    return None


def _parse_entity_file(filepath: str) -> Dict[str, Any]:
    """Parse a City of Brains entity markdown file, returning frontmatter + body."""
    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}
            body = parts[2].strip()

    return {"frontmatter": frontmatter, "body": body, "raw": content}


def _get_entity_images_dir(entity_type: str, entity_id: str) -> Optional[str]:
    """Return path to entity images directory if it exists."""
    mapping = ENTITY_TYPE_MAP.get(entity_type)
    if not mapping:
        return None
    dir_name, _ = mapping
    images_dir = os.path.join(DATA_ROOT, dir_name, entity_id, "images")
    if os.path.isdir(images_dir):
        return images_dir
    return None


# ---------------------------------------------------------------------------
# Helpers -- name resolution
# ---------------------------------------------------------------------------

_entity_name_cache: Dict[str, str] = {}
_cache_built = False


def _build_name_cache():
    """Build a lookup of entity_id -> display name across all entity types."""
    global _entity_name_cache, _cache_built
    if _cache_built:
        return
    for etype, (dir_name, prefix) in ENTITY_TYPE_MAP.items():
        type_dir = os.path.join(DATA_ROOT, dir_name)
        if not os.path.isdir(type_dir):
            continue
        for eid in os.listdir(type_dir):
            eid_dir = os.path.join(type_dir, eid)
            if not os.path.isdir(eid_dir):
                continue
            # Try to read just the frontmatter quickly
            for fname in os.listdir(eid_dir):
                if fname.startswith(prefix + "_") and fname.endswith(".md"):
                    fpath = os.path.join(eid_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as fh:
                            head = fh.read(4096)
                        if head.startswith("---"):
                            parts = head.split("---", 2)
                            if len(parts) >= 2:
                                fm = yaml.safe_load(parts[1]) or {}
                                name = fm.get("name") or fm.get("character_name") or fm.get("location_name") or fm.get("faction_name") or eid
                                _entity_name_cache[eid] = _clean_name(str(name))
                    except Exception:
                        _entity_name_cache[eid] = _id_to_display_name(eid)
                    break
            if eid not in _entity_name_cache:
                _entity_name_cache[eid] = _id_to_display_name(eid)
    _cache_built = True


def _invalidate_name_cache():
    global _entity_name_cache, _cache_built
    _entity_name_cache = {}
    _cache_built = False


def _clean_name(name: str) -> str:
    """Remove characters that Obsidian disallows in page titles."""
    return re.sub(r'[\\/:*?"<>|#\^\[\]]', '', name).strip()


def _id_to_display_name(entity_id: str) -> str:
    """Convert snake_case id to Title Case display name."""
    return entity_id.replace("_", " ").title()


def _resolve_name(entity_id: str) -> str:
    """Resolve an entity_id to a display name for wikilinks."""
    _build_name_cache()
    return _entity_name_cache.get(entity_id, _id_to_display_name(entity_id))


# ---------------------------------------------------------------------------
# Helpers -- Obsidian conversion
# ---------------------------------------------------------------------------

def _make_link(name: str, link_style: str = "wikilink") -> str:
    """Create a wikilink or markdown link for a resolved entity name."""
    clean = _clean_name(name)
    if link_style == "wikilink":
        return f"[[{clean}]]"
    else:
        safe = clean.replace(" ", "%20")
        return f"[{clean}]({safe}.md)"


def _extract_names_from_relationship(items: Any) -> List[str]:
    """Pull entity names out of a relationship list (various formats)."""
    names = []
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                n = item.get("name") or item.get("id") or item.get("nickname") or ""
                if n:
                    names.append(str(n))
            elif isinstance(item, str):
                names.append(item)
    elif isinstance(items, str) and items:
        names.append(items)
    return names


def _build_obsidian_frontmatter(fm: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
    """Build Obsidian-optimized YAML frontmatter from entity frontmatter."""
    obs = {}

    # Basic fields
    name = fm.get("name") or fm.get("character_name") or fm.get("location_name") or fm.get("faction_name") or ""
    if name:
        obs["title"] = str(name)

    # Aliases
    aliases = []
    if fm.get("nickname"):
        aliases.append(str(fm["nickname"]))
    if fm.get("aliases"):
        raw = fm["aliases"]
        if isinstance(raw, list):
            for a in raw:
                aliases.append(str(a) if not isinstance(a, list) else str(a[0]) if a else "")
        elif isinstance(raw, str):
            aliases.append(raw)
    aliases = [a for a in aliases if a]
    if aliases:
        obs["aliases"] = aliases

    # Tags
    tags = [entity_type]
    if fm.get("faction") and isinstance(fm["faction"], str) and fm["faction"] not in ("", "independent", "null", "none"):
        tags.append(fm["faction"].replace(" ", "-").lower())
    if fm.get("status"):
        tags.append(f"status/{fm['status']}")
    if fm.get("narrative_importance"):
        tags.append(f"importance/{fm['narrative_importance']}")
    if fm.get("alignment"):
        tags.append(f"alignment/{fm['alignment']}")
    if fm.get("character_type"):
        tags.append(fm["character_type"])
    if fm.get("faction_type"):
        tags.append(fm["faction_type"])
    if fm.get("location_type"):
        tags.append(fm["location_type"])
    if fm.get("biome"):
        tags.append(fm["biome"])
    # Entity-defined tags
    if fm.get("tags") and isinstance(fm["tags"], list):
        for t in fm["tags"]:
            if isinstance(t, str):
                tags.append(t.replace(" ", "-").lower())
    obs["tags"] = list(dict.fromkeys(tags))  # deduplicate, preserve order

    # Type-specific metadata
    obs["entity_type"] = entity_type
    obs["entity_id"] = fm.get("entity_id") or fm.get("character_id") or fm.get("id") or ""

    if fm.get("age"):
        obs["age"] = fm["age"]
    if fm.get("gender"):
        obs["gender"] = str(fm["gender"])
    if fm.get("species"):
        obs["species"] = str(fm["species"])
    if fm.get("birth_year"):
        obs["birth_year"] = fm["birth_year"]
    if fm.get("death_year"):
        obs["death_year"] = fm["death_year"]
    if fm.get("status"):
        obs["status"] = str(fm["status"])
    if fm.get("district"):
        obs["district"] = str(fm["district"])
    if fm.get("primary_location"):
        obs["primary_location"] = str(fm["primary_location"])
    if fm.get("faction"):
        obs["faction"] = str(fm["faction"])
    if fm.get("occupation"):
        obs["occupation"] = str(fm["occupation"])
    if fm.get("job"):
        jobs = fm["job"]
        if isinstance(jobs, list):
            obs["job"] = [str(j) for j in jobs]
        else:
            obs["job"] = str(jobs)

    # Dates
    obs["exported_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    if fm.get("template_version"):
        obs["cob_template_version"] = str(fm["template_version"])

    return obs


def _convert_body_with_wikilinks(
    body: str,
    fm: Dict[str, Any],
    link_style: str,
) -> tuple[str, int]:
    """
    Process entity body text and frontmatter relationships,
    converting references to Obsidian wikilinks.
    Returns (converted_body, link_count).
    """
    _build_name_cache()
    links_added = set()

    # Build a relationship summary section to append
    rel_sections = []

    for field_name in RELATIONSHIP_FIELDS:
        items = fm.get(field_name)
        if not items:
            continue
        names = _extract_names_from_relationship(items)
        if not names:
            continue

        label = field_name.replace("_", " ").title()
        lines = [f"## {label}"]
        for n in names:
            link = _make_link(n, link_style)
            links_added.add(n)
            # Try to get notes
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        item_name = item.get("name") or item.get("id") or ""
                        if str(item_name) == n:
                            notes = item.get("notes", "")
                            relation = item.get("relation") or item.get("relationship_type") or item.get("relationship") or ""
                            parts = []
                            if relation:
                                parts.append(f"*{str(relation).replace('_', ' ').title()}*")
                            parts.append(link)
                            if notes:
                                note_str = str(notes) if not isinstance(notes, list) else " ".join(str(x) for x in notes)
                                parts.append(f"-- {note_str}")
                            lines.append(f"- {' '.join(parts)}")
                            break
                else:
                    lines.append(f"- {link}")
            else:
                lines.append(f"- {link}")

        rel_sections.append("\n".join(lines))

    # Also convert single-reference fields to links in a metadata-links section
    single_links = []
    for field_name in SINGLE_REF_FIELDS:
        val = fm.get(field_name)
        if val and isinstance(val, str) and val not in ("", "null", "none", "independent", "neutral"):
            resolved = _resolve_name(val)
            link = _make_link(resolved, link_style)
            links_added.add(resolved)
            label = field_name.replace("_", " ").title()
            single_links.append(f"- **{label}**: {link}")

    # Also convert secondary_locations
    sec_locs = fm.get("secondary_locations", [])
    if isinstance(sec_locs, list) and sec_locs:
        for loc in sec_locs:
            if isinstance(loc, str) and loc:
                resolved = _resolve_name(loc)
                link = _make_link(resolved, link_style)
                links_added.add(resolved)
                single_links.append(f"- **Location**: {link}")

    # Build the final body
    converted_body = body

    # Inject wikilinks into body text for known entity names
    for eid, display_name in _entity_name_cache.items():
        if display_name in converted_body:
            link = _make_link(display_name, link_style)
            # Only replace full-word matches, case-sensitive
            pattern = re.compile(r'(?<!\[)' + re.escape(display_name) + r'(?!\])')
            converted_body = pattern.sub(link, converted_body, count=1)
            links_added.add(display_name)

    # Append relationship sections
    if single_links:
        converted_body += "\n\n## Linked Entities\n" + "\n".join(single_links)

    if rel_sections:
        converted_body += "\n\n" + "\n\n".join(rel_sections)

    return converted_body, len(links_added)


def _build_obsidian_markdown(
    entity_type: str,
    entity_id: str,
    link_style: str = "wikilink",
) -> tuple[str, int]:
    """
    Full conversion pipeline: parse entity -> build Obsidian md.
    Returns (markdown_string, link_count).
    """
    filepath = _find_entity_file(entity_type, entity_id)
    if not filepath:
        raise HTTPException(status_code=404, detail=f"Entity file not found: {entity_type}/{entity_id}")

    data = _parse_entity_file(filepath)
    fm = data["frontmatter"]
    body = data["body"]

    # Build frontmatter
    obs_fm = _build_obsidian_frontmatter(fm, entity_type)

    # Convert body
    converted_body, link_count = _convert_body_with_wikilinks(body, fm, link_style)

    # Add primary image embed if available
    image_embed = ""
    primary_img = fm.get("primary_image") or fm.get("primary_asset")
    if primary_img:
        img_name = os.path.basename(str(primary_img))
        if link_style == "wikilink":
            image_embed = f"![[attachments/{img_name}]]\n\n"
        else:
            image_embed = f"![{img_name}](attachments/{img_name})\n\n"

    # Assemble
    fm_str = yaml.dump(obs_fm, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()
    md = f"---\n{fm_str}\n---\n\n{image_embed}{converted_body}\n"

    return md, link_count


# ---------------------------------------------------------------------------
# Helpers -- writing to vault
# ---------------------------------------------------------------------------

def _write_to_vault(
    entity_type: str,
    entity_id: str,
    markdown: str,
    link_count: int,
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    """Write the converted markdown and optionally images into the vault."""
    vault_path = settings["vault_path"]
    folder_per_type = settings.get("folder_per_type", True)
    include_images = settings.get("include_images", True)

    # Resolve display name for filename
    _build_name_cache()
    display_name = _entity_name_cache.get(entity_id, _id_to_display_name(entity_id))
    safe_name = _clean_name(display_name)

    # Target directory
    if folder_per_type:
        mapping = ENTITY_TYPE_MAP.get(entity_type)
        subdir = mapping[0] if mapping else entity_type.title() + "s"
        target_dir = os.path.join(vault_path, subdir)
    else:
        target_dir = vault_path

    os.makedirs(target_dir, exist_ok=True)

    # Write markdown
    md_path = os.path.join(target_dir, f"{safe_name}.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    # Copy images
    images_copied = 0
    if include_images:
        images_dir = _get_entity_images_dir(entity_type, entity_id)
        if images_dir:
            attachments_dir = os.path.join(vault_path, "attachments")
            os.makedirs(attachments_dir, exist_ok=True)
            for img_file in os.listdir(images_dir):
                if img_file.startswith("_") or img_file.lower() == "thumbs.db":
                    continue
                src = os.path.join(images_dir, img_file)
                if os.path.isfile(src):
                    dst = os.path.join(attachments_dir, img_file)
                    shutil.copy2(src, dst)
                    images_copied += 1

    # Record
    _record_export(entity_type, entity_id, link_count, md_path)

    return {
        "file": md_path,
        "display_name": display_name,
        "link_count": link_count,
        "images_copied": images_copied,
    }


# ---------------------------------------------------------------------------
# Helpers -- enumerate all entities
# ---------------------------------------------------------------------------

def _enumerate_all_entities() -> List[Dict[str, str]]:
    """Return list of {type, id, name} for every entity on disk."""
    _build_name_cache()
    entities = []
    for etype, (dir_name, prefix) in ENTITY_TYPE_MAP.items():
        type_dir = os.path.join(DATA_ROOT, dir_name)
        if not os.path.isdir(type_dir):
            continue
        for eid in sorted(os.listdir(type_dir)):
            eid_dir = os.path.join(type_dir, eid)
            if not os.path.isdir(eid_dir):
                continue
            # Verify an entity file exists
            has_file = any(
                f.startswith(prefix + "_") and f.endswith(".md")
                for f in os.listdir(eid_dir)
            )
            if has_file:
                entities.append({
                    "type": etype,
                    "id": eid,
                    "name": _entity_name_cache.get(eid, _id_to_display_name(eid)),
                })
    return entities


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status and vault path info."""
    settings = _load_settings()
    vault_path = settings.get("vault_path", "")
    vault_exists = os.path.isdir(vault_path) if vault_path else False
    return {
        "plugin": "obsidian-vault",
        "version": "1.0.0",
        "vault_path": vault_path,
        "vault_exists": vault_exists,
        "settings": settings,
    }


@router.get("/status")
async def vault_status():
    """Check export status across all entities."""
    settings = _load_settings()
    vault_path = settings.get("vault_path", "")
    vault_exists = os.path.isdir(vault_path) if vault_path else False
    export_log = _load_export_log()
    entities = _enumerate_all_entities()

    results = []
    exported_count = 0
    stale_count = 0
    pending_count = 0

    for entity in entities:
        key = f"{entity['type']}/{entity['id']}"
        log_entry = export_log.get(key)

        if log_entry:
            # Check if source file is newer than export
            src_file = _find_entity_file(entity["type"], entity["id"])
            src_mtime = os.path.getmtime(src_file) if src_file else 0
            export_time_str = log_entry.get("exported_at", "")
            try:
                export_dt = datetime.fromisoformat(export_time_str)
                export_ts = export_dt.timestamp()
            except Exception:
                export_ts = 0

            if src_mtime > export_ts:
                status = "stale"
                stale_count += 1
            else:
                status = "exported"
                exported_count += 1

            results.append({
                **entity,
                "status": status,
                "exported_at": export_time_str,
                "link_count": log_entry.get("link_count", 0),
            })
        else:
            status = "pending"
            pending_count += 1
            results.append({
                **entity,
                "status": status,
                "exported_at": None,
                "link_count": 0,
            })

    return {
        "vault_path": vault_path,
        "vault_exists": vault_exists,
        "total": len(entities),
        "exported": exported_count,
        "stale": stale_count,
        "pending": pending_count,
        "entities": results,
    }


@router.get("/status/{entity_type}/{entity_id}")
async def entity_export_status(entity_type: str, entity_id: str):
    """Check export status for a single entity."""
    export_log = _load_export_log()
    key = f"{entity_type}/{entity_id}"
    log_entry = export_log.get(key)

    src_file = _find_entity_file(entity_type, entity_id)
    if not src_file:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    if log_entry:
        src_mtime = os.path.getmtime(src_file)
        try:
            export_dt = datetime.fromisoformat(log_entry["exported_at"])
            export_ts = export_dt.timestamp()
        except Exception:
            export_ts = 0

        if src_mtime > export_ts:
            status = "stale"
        else:
            status = "exported"
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": status,
            "exported_at": log_entry.get("exported_at"),
            "link_count": log_entry.get("link_count", 0),
            "vault_file": log_entry.get("vault_file", ""),
        }
    else:
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": "pending",
            "exported_at": None,
            "link_count": 0,
            "vault_file": "",
        }


@router.get("/preview/{entity_type}/{entity_id}")
async def preview_export(entity_type: str, entity_id: str):
    """Preview the Obsidian-formatted markdown without writing to vault."""
    settings = _load_settings()
    link_style = settings.get("link_style", "wikilink")
    markdown, link_count = _build_obsidian_markdown(entity_type, entity_id, link_style)
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "link_count": link_count,
        "markdown": markdown,
    }


@router.post("/export/{entity_type}/{entity_id}")
async def export_entity(entity_type: str, entity_id: str):
    """Export a single entity to the Obsidian vault."""
    settings = _load_settings()
    vault_path = _get_vault_path()
    link_style = settings.get("link_style", "wikilink")

    if not os.path.isdir(vault_path):
        os.makedirs(vault_path, exist_ok=True)

    markdown, link_count = _build_obsidian_markdown(entity_type, entity_id, link_style)
    result = _write_to_vault(entity_type, entity_id, markdown, link_count, settings)

    return {
        "success": True,
        "entity_type": entity_type,
        "entity_id": entity_id,
        **result,
    }


class BulkExportRequest(BaseModel):
    entity_types: Optional[List[str]] = None  # None means all types


@router.post("/export-all")
async def export_all(req: BulkExportRequest = None):
    """Bulk export all entities (optionally filtered by type)."""
    settings = _load_settings()
    vault_path = _get_vault_path()
    link_style = settings.get("link_style", "wikilink")

    if not os.path.isdir(vault_path):
        os.makedirs(vault_path, exist_ok=True)

    # Invalidate cache to get fresh data
    _invalidate_name_cache()
    _build_name_cache()

    entities = _enumerate_all_entities()
    type_filter = req.entity_types if req and req.entity_types else None

    results = []
    errors = []

    for entity in entities:
        if type_filter and entity["type"] not in type_filter:
            continue
        try:
            markdown, link_count = _build_obsidian_markdown(
                entity["type"], entity["id"], link_style
            )
            result = _write_to_vault(
                entity["type"], entity["id"], markdown, link_count, settings
            )
            results.append({
                "entity_type": entity["type"],
                "entity_id": entity["id"],
                "name": result["display_name"],
                "link_count": link_count,
                "images_copied": result["images_copied"],
            })
        except Exception as e:
            errors.append({
                "entity_type": entity["type"],
                "entity_id": entity["id"],
                "error": str(e),
            })

    return {
        "success": True,
        "exported": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors,
    }


class SettingsUpdate(BaseModel):
    vault_path: Optional[str] = None
    auto_export: Optional[bool] = None
    include_images: Optional[bool] = None
    link_style: Optional[str] = None
    folder_per_type: Optional[bool] = None


@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    """Update plugin settings."""
    settings = _load_settings()
    for field, value in update.dict(exclude_none=True).items():
        settings[field] = value
    _save_settings(settings)
    return {"success": True, "settings": settings}


@router.get("/entities")
async def list_entities(entity_type: Optional[str] = Query(None)):
    """List all available entities, optionally filtered by type."""
    entities = _enumerate_all_entities()
    if entity_type:
        entities = [e for e in entities if e["type"] == entity_type]
    return {"entities": entities, "total": len(entities)}


@router.get("/graph-data")
async def graph_data():
    """
    Return nodes and edges for an entity relationship graph visualization.
    Suitable for a force-directed graph in the frontend.
    """
    _build_name_cache()
    entities = _enumerate_all_entities()
    export_log = _load_export_log()

    nodes = []
    edges = []
    node_ids = set()

    for entity in entities:
        node_id = entity["id"]
        node_ids.add(node_id)
        key = f"{entity['type']}/{entity['id']}"
        is_exported = key in export_log
        nodes.append({
            "id": node_id,
            "name": entity["name"],
            "type": entity["type"],
            "exported": is_exported,
        })

    # Build edges from relationships
    for entity in entities:
        filepath = _find_entity_file(entity["type"], entity["id"])
        if not filepath:
            continue
        try:
            data = _parse_entity_file(filepath)
            fm = data["frontmatter"]
        except Exception:
            continue

        source_id = entity["id"]

        for field_name in RELATIONSHIP_FIELDS:
            items = fm.get(field_name)
            if not items:
                continue
            names = _extract_names_from_relationship(items)
            for name in names:
                # Try to find a matching entity id
                target_id = None
                for eid, ename in _entity_name_cache.items():
                    if ename.lower() == name.lower() or eid == name.lower().replace(" ", "_"):
                        target_id = eid
                        break
                if target_id and target_id in node_ids and target_id != source_id:
                    edges.append({
                        "source": source_id,
                        "target": target_id,
                        "relationship": field_name,
                    })

        for field_name in SINGLE_REF_FIELDS:
            val = fm.get(field_name)
            if val and isinstance(val, str) and val not in ("", "null", "none", "independent", "neutral"):
                if val in node_ids:
                    edges.append({
                        "source": source_id,
                        "target": val,
                        "relationship": field_name,
                    })

    return {
        "nodes": nodes,
        "edges": edges,
    }
