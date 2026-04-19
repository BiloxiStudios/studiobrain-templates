"""
Entity Validator Plugin — FastAPI routes

SBAI-1677: Validate entity YAML frontmatter against JSON Schema definitions
before write.  Returns HTTP 422 with structured per-field errors so only
well-formed entities reach the database.

Endpoints
---------
POST /api/plugins/entity-validator/validate
    Validate a pre-parsed frontmatter dict.

POST /api/plugins/entity-validator/validate/markdown
    Parse raw markdown, extract frontmatter, then validate.

GET  /api/plugins/entity-validator/schemas
    List all registered schema IDs.

GET  /api/plugins/entity-validator/schemas/{entity_type}
    Return the JSON Schema for a specific entity type.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("plugin.entity-validator")

router = APIRouter(prefix="/api/plugins/entity-validator", tags=["entity-validator"])

# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

def _locate_schemas_dir() -> Path:
    """Locate the ``schemas/`` directory.

    Checks ``STUDIOBRAIN_SCHEMAS_DIR`` environment variable first, then walks
    up from this file's location until a ``schemas/`` directory is found.
    Raises ``RuntimeError`` if the directory cannot be located.
    """
    env_override = os.environ.get("STUDIOBRAIN_SCHEMAS_DIR")
    if env_override:
        candidate = Path(env_override).resolve()
        if candidate.is_dir():
            return candidate
        raise RuntimeError(
            f"STUDIOBRAIN_SCHEMAS_DIR is set to '{env_override}' but that "
            "directory does not exist."
        )

    # Walk up to find schemas/ relative to this file
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "schemas"
        if candidate.is_dir():
            return candidate
        current = current.parent
    raise RuntimeError(
        "Could not locate the 'schemas/' directory. "
        "Set the STUDIOBRAIN_SCHEMAS_DIR environment variable to the absolute path."
    )


_SCHEMAS_DIR = _locate_schemas_dir()

# Map entity_type → schema file path
ENTITY_SCHEMAS: Dict[str, Path] = {
    "character": _SCHEMAS_DIR / "character.json",
    "location": _SCHEMAS_DIR / "location.json",
    "item": _SCHEMAS_DIR / "item.json",
    "faction": _SCHEMAS_DIR / "faction.json",
    "brand": _SCHEMAS_DIR / "brand.json",
    "district": _SCHEMAS_DIR / "district.json",
    "job": _SCHEMAS_DIR / "job.json",
    "quest": _SCHEMAS_DIR / "quest.json",
    "event": _SCHEMAS_DIR / "event.json",
    "campaign": _SCHEMAS_DIR / "campaign.json",
    "assembly": _SCHEMAS_DIR / "assembly.json",
    "dialogue": _SCHEMAS_DIR / "dialogue.json",
    "timeline": _SCHEMAS_DIR / "timeline.json",
    "universe": _SCHEMAS_DIR / "universe.json",
    "style_bible": _SCHEMAS_DIR / "style_bible.json",
}


def _load_schema(entity_type: str) -> Dict[str, Any]:
    """Load and return the JSON Schema dict for *entity_type*.

    Raises ``HTTPException(404)`` when no schema is registered for the type.
    """
    schema_path = ENTITY_SCHEMAS.get(entity_type)
    if schema_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"No schema registered for entity type '{entity_type}'. "
                   f"Known types: {sorted(ENTITY_SCHEMAS)}",
        )
    if not schema_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Schema file missing on disk: {schema_path}",
        )
    with schema_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_base_schema() -> Dict[str, Any]:
    base_path = _SCHEMAS_DIR / "_base.json"
    if not base_path.exists():
        return {}
    with base_path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def _validate_frontmatter(
    frontmatter: Dict[str, Any],
    entity_type: str,
    strict: bool = False,
) -> List[Dict[str, Any]]:
    """Validate *frontmatter* against the schema for *entity_type*.

    Returns a list of error dicts (empty list means valid).  Each error has:
        ``field``   — JSON pointer path of the failing field (e.g. "/id")
        ``message`` — human-readable description of the failure
        ``value``   — the offending value (omitted for missing required fields)
    """
    try:
        import jsonschema  # noqa: F401 — availability probe
        from jsonschema import Draft202012Validator, RefResolver
    except ImportError:
        logger.warning(
            "jsonschema not installed; skipping schema validation. "
            "Install with: pip install jsonschema>=4.17"
        )
        return []

    schema = _load_schema(entity_type)

    # Build a resolver that serves $ref lookups from local files, keyed by
    # both the file:// URI and the canonical $id URL so relative refs work
    # whether the referrer uses either form.
    schema_store: Dict[str, Any] = {}
    for path in _SCHEMAS_DIR.glob("*.json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Register under both the local file URI and the declared $id (if any)
        file_uri = path.resolve().as_uri()
        schema_store[file_uri] = doc
        declared_id = doc.get("$id")
        if declared_id:
            schema_store[declared_id] = doc

    base_uri = ENTITY_SCHEMAS[entity_type].resolve().as_uri()
    resolver = RefResolver(base_uri=base_uri, referrer=schema, store=schema_store)

    validator = Draft202012Validator(schema, resolver=resolver)

    errors: List[Dict[str, Any]] = []
    seen: set = set()
    for err in sorted(validator.iter_errors(frontmatter), key=lambda e: list(e.absolute_path)):
        path = "/" + "/".join(str(p) for p in err.absolute_path) if err.absolute_path else "/"
        dedup_key = (path, err.message)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        entry: Dict[str, Any] = {
            "field": path,
            "message": err.message,
        }
        # Include the offending value when it exists (not for missing required)
        if err.absolute_path:
            try:
                entry["value"] = err.instance
            except Exception:
                pass
        errors.append(entry)

    # Strict mode: flag additional properties not defined in the schema
    if strict:
        defined = set(schema.get("properties", {}).keys())
        base_schema = _load_base_schema()
        defined |= set(base_schema.get("properties", {}).keys())
        for key in frontmatter:
            if key not in defined:
                errors.append({
                    "field": f"/{key}",
                    "message": f"Unknown field '{key}' (strict mode enabled).",
                    "value": frontmatter[key],
                })

    return errors


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ValidateFrontmatterRequest(BaseModel):
    entity_type: str = Field(..., description="Entity type (e.g. 'character', 'item').")
    frontmatter: Dict[str, Any] = Field(..., description="Parsed YAML frontmatter as a dict.")
    strict: bool = Field(default=False, description="Reject unknown fields when True.")


class ValidateMarkdownRequest(BaseModel):
    entity_type: str = Field(..., description="Entity type (e.g. 'character', 'item').")
    content: str = Field(..., description="Raw markdown string including YAML frontmatter.")
    strict: bool = Field(default=False, description="Reject unknown fields when True.")


class ValidationError(BaseModel):
    field: str
    message: str
    value: Optional[Any] = None


class ValidationResult(BaseModel):
    valid: bool
    entity_type: str
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_markdown_frontmatter(content: str) -> Dict[str, Any]:
    """Extract and parse the YAML frontmatter block from a markdown string."""
    if not content.strip().startswith("---"):
        raise HTTPException(
            status_code=422,
            detail="Content does not start with a YAML frontmatter delimiter '---'.",
        )
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise HTTPException(
            status_code=422,
            detail="Malformed frontmatter: no closing '---' delimiter found.",
        )
    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"YAML parse error in frontmatter: {exc}",
        ) from exc
    if not isinstance(frontmatter, dict):
        raise HTTPException(
            status_code=422,
            detail="Frontmatter must be a YAML mapping (dict).",
        )
    return frontmatter


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/validate", response_model=ValidationResult, status_code=200)
async def validate_frontmatter(req: ValidateFrontmatterRequest):
    """Validate a pre-parsed frontmatter dict against the entity type's JSON Schema.

    Returns ``200 {"valid": true}`` when the frontmatter is valid.
    Returns ``422`` when the frontmatter fails validation, with a list of
    per-field errors so the caller can surface them to the user.
    """
    errors = _validate_frontmatter(req.frontmatter, req.entity_type, strict=req.strict)
    if errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"Entity frontmatter failed validation for type '{req.entity_type}'.",
                "errors": errors,
            },
        )
    return ValidationResult(valid=True, entity_type=req.entity_type)


@router.post("/validate/markdown", response_model=ValidationResult, status_code=200)
async def validate_markdown(req: ValidateMarkdownRequest):
    """Parse raw markdown, extract YAML frontmatter, and validate against schema.

    Accepts the raw content of an entity markdown file.  Returns ``200``
    when valid or ``422`` with structured errors when invalid.
    """
    frontmatter = _parse_markdown_frontmatter(req.content)

    # If entity_type is omitted from request but present in frontmatter, use it
    entity_type = req.entity_type
    if not entity_type and "entity_type" in frontmatter:
        entity_type = str(frontmatter["entity_type"])

    errors = _validate_frontmatter(frontmatter, entity_type, strict=req.strict)
    if errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"Entity frontmatter failed validation for type '{entity_type}'.",
                "errors": errors,
            },
        )
    return ValidationResult(valid=True, entity_type=entity_type)


@router.get("/schemas", status_code=200)
async def list_schemas():
    """Return the list of registered entity-type schema IDs."""
    return {
        "schemas": sorted(ENTITY_SCHEMAS.keys()),
        "count": len(ENTITY_SCHEMAS),
    }


@router.get("/schemas/{entity_type}", status_code=200)
async def get_schema(entity_type: str):
    """Return the full JSON Schema for *entity_type*."""
    schema = _load_schema(entity_type)
    return schema


@router.get("/health", status_code=200)
async def health():
    """Plugin health check."""
    return {"status": "ok", "plugin": "entity-validator", "version": "1.0.0"}
