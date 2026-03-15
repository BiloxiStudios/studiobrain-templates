"""
Production Kanban Plugin — backend routes.

Provides API endpoints for the kanban board: listing entities grouped
by production status, moving entities between columns, and retrieving
board statistics.
"""

import os
import re
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger("plugin.kanban-board")
router = APIRouter()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

DEFAULT_COLUMNS = ["Concept", "In Progress", "Review", "Complete"]
DEFAULT_WIP_LIMITS = [0, 10, 5, 0]
DEFAULT_ENTITY_TYPES = ["character", "location", "item", "faction", "brand", "district", "job"]
DEFAULT_STATUS_FIELD = "status"

# Map entity type to file prefix used in the data directory
TYPE_PREFIX_MAP = {
    "character": "CH",
    "location": "LOC",
    "item": "ITEM",
    "faction": "FAC",
    "brand": "BR",
    "district": "DIST",
    "job": "JOB",
}

# Map entity type to display color (for the frontend)
TYPE_COLOR_MAP = {
    "character": "#3b82f6",
    "location": "#22c55e",
    "item": "#f97316",
    "faction": "#a855f7",
    "brand": "#ec4899",
    "district": "#14b8a6",
    "job": "#eab308",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_type_dir(entity_type: str) -> str:
    """Return the directory name for a given entity type."""
    return entity_type.capitalize() + "s"


def _get_entity_file(entity_type: str, entity_id: str) -> str:
    """Return absolute path to an entity's markdown file."""
    type_dir = _get_type_dir(entity_type)
    prefix = TYPE_PREFIX_MAP.get(entity_type, entity_type.upper())
    return os.path.join(DATA_ROOT, type_dir, entity_id, f"{prefix}_{entity_id}.md")


def _parse_frontmatter(filepath: str) -> dict:
    """Read a markdown file and extract YAML frontmatter as a dict."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    # Lightweight YAML-ish parsing for the fields we care about.
    # We avoid importing yaml at module level to keep things simple;
    # fall back to a basic key: value parser.
    try:
        import yaml
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        data = {}
        for line in match.group(1).split("\n"):
            if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                key, _, val = line.partition(":")
                val = val.strip().strip("'\"")
                data[key.strip()] = val
        return data


def _write_frontmatter_field(filepath: str, field: str, value: str) -> bool:
    """Update a single YAML frontmatter field in-place."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        return False

    match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not match:
        return False

    fm_text = match.group(2)

    # Check if the field already exists (top-level only)
    field_pattern = re.compile(r"^(" + re.escape(field) + r":\s*)(.*)$", re.MULTILINE)
    if field_pattern.search(fm_text):
        fm_text = field_pattern.sub(rf"\g<1>{value}", fm_text)
    else:
        # Append the field
        fm_text += f"\n{field}: {value}"

    new_content = match.group(1) + fm_text + match.group(3) + content[match.end():]

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(new_content)
    return True


def _scan_entities(entity_type: str, status_field: str = DEFAULT_STATUS_FIELD):
    """Scan all entities of a given type and return a list of dicts."""
    type_dir = os.path.join(DATA_ROOT, _get_type_dir(entity_type))
    if not os.path.isdir(type_dir):
        return []

    prefix = TYPE_PREFIX_MAP.get(entity_type, entity_type.upper())
    results = []

    for entry in os.listdir(type_dir):
        entry_path = os.path.join(type_dir, entry)
        if not os.path.isdir(entry_path):
            continue

        md_file = os.path.join(entry_path, f"{prefix}_{entry}.md")
        if not os.path.isfile(md_file):
            continue

        fm = _parse_frontmatter(md_file)
        name = (
            fm.get("name")
            or fm.get("character_name")
            or fm.get("business_name")
            or fm.get("item_name")
            or fm.get("faction_name")
            or fm.get("brand_name")
            or fm.get("district_name")
            or fm.get("job_name")
            or entry.replace("_", " ").title()
        )

        status_raw = fm.get(status_field, "")
        if isinstance(status_raw, str):
            status = status_raw.strip().strip("'\"")
        else:
            status = str(status_raw) if status_raw else ""

        # Look for a portrait/image
        image_url = None
        images_dir = os.path.join(entry_path, "images")
        if os.path.isdir(images_dir):
            for img in os.listdir(images_dir):
                if img.lower().startswith("portrait") or img.lower().startswith("thumb"):
                    image_url = f"/api/entity/{entity_type}/{entry}/image/{img}"
                    break
            # Fallback: first image file
            if not image_url:
                for img in os.listdir(images_dir):
                    if img.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        image_url = f"/api/entity/{entity_type}/{entry}/image/{img}"
                        break

        results.append({
            "id": entry,
            "type": entity_type,
            "name": name,
            "status": status,
            "color": TYPE_COLOR_MAP.get(entity_type, "#94a3b8"),
            "image": image_url,
            "description": fm.get("description", ""),
            "tags": fm.get("tags", []),
        })

    return results


def _normalize_status(status: str, columns: list[str]) -> str:
    """Map an entity's status to the closest column name."""
    if not status:
        return columns[0] if columns else "Concept"

    status_lower = status.lower().replace("-", " ").replace("_", " ")

    # Direct match
    for col in columns:
        if col.lower() == status_lower:
            return col

    # Partial / alias matching
    aliases = {
        "concept": ["concept", "draft", "idea", "backlog", "new", "planned"],
        "in progress": ["in progress", "active", "wip", "modeling", "rigging",
                        "texturing", "development", "working", "in_progress"],
        "review": ["review", "qa", "testing", "feedback", "pending",
                   "quarantined", "quarantined_active"],
        "complete": ["complete", "done", "final", "finished", "approved",
                     "published", "released", "shipped"],
    }

    for col in columns:
        col_lower = col.lower()
        if col_lower in aliases:
            if status_lower in aliases[col_lower]:
                return col

    # Fallback heuristic: check if status contains any alias keyword
    for col in columns:
        col_lower = col.lower()
        if col_lower in aliases:
            for alias in aliases[col_lower]:
                if alias in status_lower or status_lower in alias:
                    return col

    # Default to first column
    return columns[0] if columns else "Concept"


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class MoveRequest(BaseModel):
    entity_type: str
    entity_id: str
    new_status: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin health check."""
    return {"plugin": "kanban-board", "version": "1.0.0", "status": "ok"}


@router.get("/columns")
async def get_columns():
    """Return configured columns with WIP limits."""
    columns = DEFAULT_COLUMNS
    wip_limits = DEFAULT_WIP_LIMITS

    result = []
    for i, col in enumerate(columns):
        result.append({
            "name": col,
            "wip_limit": wip_limits[i] if i < len(wip_limits) else 0,
        })
    return {"columns": result}


@router.get("/board")
async def get_board(entity_type: Optional[str] = Query(None)):
    """
    Return all entities grouped by kanban column.

    Optionally filter by entity_type (e.g., ?entity_type=character).
    """
    columns = DEFAULT_COLUMNS
    types_to_scan = (
        [entity_type] if entity_type and entity_type in DEFAULT_ENTITY_TYPES
        else DEFAULT_ENTITY_TYPES
    )

    # Initialize board with empty columns
    board = {col: [] for col in columns}

    for etype in types_to_scan:
        entities = _scan_entities(etype, DEFAULT_STATUS_FIELD)
        for entity in entities:
            col = _normalize_status(entity["status"], columns)
            entity["column"] = col
            board[col].append(entity)

    # Sort each column by name
    for col in board:
        board[col].sort(key=lambda e: (e["type"], e["name"].lower()))

    return {
        "columns": columns,
        "board": board,
        "entity_types": types_to_scan,
        "total": sum(len(v) for v in board.values()),
    }


@router.post("/move")
async def move_entity(req: MoveRequest):
    """Move an entity to a new status/column."""
    filepath = _get_entity_file(req.entity_type, req.entity_id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Entity not found: {req.entity_type}/{req.entity_id}")

    # Map the column name to a status value to write
    status_value = req.new_status.lower().replace(" ", "_")

    success = _write_frontmatter_field(filepath, DEFAULT_STATUS_FIELD, status_value)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update entity frontmatter")

    logger.info(
        "Kanban move: %s/%s -> %s",
        req.entity_type, req.entity_id, req.new_status,
    )

    return {
        "success": True,
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "new_status": req.new_status,
    }


@router.get("/stats")
async def get_stats(entity_type: Optional[str] = Query(None)):
    """Return column counts and completion percentages."""
    columns = DEFAULT_COLUMNS
    types_to_scan = (
        [entity_type] if entity_type and entity_type in DEFAULT_ENTITY_TYPES
        else DEFAULT_ENTITY_TYPES
    )

    counts = {col: 0 for col in columns}
    type_counts = {}

    for etype in types_to_scan:
        entities = _scan_entities(etype, DEFAULT_STATUS_FIELD)
        type_counts[etype] = len(entities)
        for entity in entities:
            col = _normalize_status(entity["status"], columns)
            counts[col] += 1

    total = sum(counts.values())
    last_col = columns[-1] if columns else "Complete"

    return {
        "columns": [
            {
                "name": col,
                "count": counts[col],
                "percentage": round(counts[col] / total * 100, 1) if total > 0 else 0,
            }
            for col in columns
        ],
        "total": total,
        "completed": counts.get(last_col, 0),
        "completion_rate": round(counts.get(last_col, 0) / total * 100, 1) if total > 0 else 0,
        "by_type": type_counts,
    }


@router.get("/entity-status/{entity_type}/{entity_id}")
async def get_entity_status(entity_type: str, entity_id: str):
    """Get the current kanban status for a single entity."""
    filepath = _get_entity_file(entity_type, entity_id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Entity not found")

    fm = _parse_frontmatter(filepath)
    raw_status = fm.get(DEFAULT_STATUS_FIELD, "")
    if isinstance(raw_status, str):
        raw_status = raw_status.strip().strip("'\"")

    columns = DEFAULT_COLUMNS
    current_column = _normalize_status(raw_status, columns)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "raw_status": raw_status,
        "column": current_column,
        "columns": columns,
        "color": TYPE_COLOR_MAP.get(entity_type, "#94a3b8"),
    }
