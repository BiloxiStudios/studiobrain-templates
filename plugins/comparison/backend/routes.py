"""
Comparison Plugin — Backend Routes

Provides side-by-side entity comparison capabilities:
- Entity vs Entity: Compare two entities of the same type
- Version vs Version: Compare same entity at different git commits
- Template vs Entity: Show entity customizations vs template defaults

All file paths are configurable via the BRAINS_ROOT environment variable.
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from difflib import unified_diff

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger("plugin.comparison")

# ---------------------------------------------------------------------------
# Configuration (env var based, no hardcoded paths)
# ---------------------------------------------------------------------------

BRAINS_ROOT = Path(os.environ.get("BRAINS_ROOT", ".")).resolve()

# Mapping of entity_type -> (folder_name, file_prefix)
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entity_file(entity_type: str, entity_id: str) -> Path:
    """Resolve the canonical markdown file for an entity."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
    folder, prefix = mapping
    return BRAINS_ROOT / folder / entity_id / f"{prefix}{entity_id}.md"


def _relative_path(full_path: Path) -> str:
    """Return the path relative to BRAINS_ROOT."""
    try:
        return str(full_path.relative_to(BRAINS_ROOT))
    except ValueError:
        # Path is not under BRAINS_ROOT, return absolute path
        return str(full_path)


async def _run_git(*args: str, check: bool = True, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a git command asynchronously."""
    cmd = ["git"] + list(args)
    if cwd:
        cmd = ["git", "-C", str(cwd)] + list(args)
    logger.debug("git %s", " ".join(cmd))

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(cwd) if cwd else None,
        ),
    )
    if check and result.returncode != 0:
        logger.error("git error: %s", result.stderr.strip())
        raise HTTPException(status_code=500, detail=f"Git error: {result.stderr.strip()}")
    return result


def _parse_markdown_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter and markdown body from a markdown file."""
    if not content.strip():
        return {}, ""

    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, content

    # Find closing ---
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, content

    # Parse YAML frontmatter
    try:
        import yaml
        frontmatter = yaml.safe_load("\n".join(lines[1:end_idx])) or {}
    except Exception:
        frontmatter = {}

    # Markdown body starts after ---
    body_lines = lines[end_idx + 1:]
    body = "\n".join(body_lines) if body_lines else ""

    return frontmatter, body


async def _get_entity_content(entity_type: str, entity_id: str, commit_sha: Optional[str] = None) -> Dict[str, Any]:
    """Get entity content from file or git history."""
    entity_path = _entity_file(entity_type, entity_id)

    if not entity_path.exists():
        # Try to get from git history if commit specified
        if commit_sha:
            rel_path = _relative_path(entity_path)
            try:
                result = await _run_git("show", f"{commit_sha}:{rel_path}", check=False)
                if result.returncode == 0:
                    return _parse_markdown_frontmatter(result.stdout)
            except Exception:
                pass
        raise HTTPException(status_code=404, detail=f"Entity file not found: {rel_path}")

    content = entity_path.read_text(encoding="utf-8")
    return _parse_markdown_frontmatter(content)


async def _get_git_diff(commit1: str, commit2: str, file_path: str, cwd: Path, context: int = 3) -> str:
    """Get unified diff between two commits for a file."""
    try:
        result = await _run_git(
            "diff",
            f"-U{context}",
            commit1,
            commit2,
            "--",
            file_path,
            check=False,
            cwd=cwd,
        )
        return result.stdout
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Route Models
# ---------------------------------------------------------------------------

class EntityComparisonRequest(BaseModel):
    entity_type: str
    entity_id1: str
    entity_id2: str


class VersionComparisonRequest(BaseModel):
    entity_type: str
    entity_id: str
    commit1: str
    commit2: str


class TemplateComparisonRequest(BaseModel):
    entity_type: str
    entity_id: str


# ---------------------------------------------------------------------------
# Comparison Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status / health check."""
    return {
        "plugin": "comparison",
        "version": "1.0.0",
        "status": "ok",
        "brains_root": str(BRAINS_ROOT),
    }


@router.post("/compare/entities")
async def compare_entities(request: EntityComparisonRequest):
    """
    Compare two entities of the same type.

    Returns side-by-side field comparison showing differences.
    """
    entity_type = request.entity_type
    entity_id1 = request.entity_id1
    entity_id2 = request.entity_id2

    # Get both entities
    try:
        data1 = await _get_entity_content(entity_type, entity_id1)
        data2 = await _get_entity_content(entity_type, entity_id2)
    except HTTPException as e:
        return {"status": "error", "message": str(e.detail)}

    fields1 = data1.get("frontmatter", {})
    fields2 = data2.get("frontmatter", {})
    body1 = data1.get("body", "")
    body2 = data2.get("body", "")

    # Calculate field differences
    all_keys = set(fields1.keys()) | set(fields2.keys())
    field_diffs = {}

    for key in all_keys:
        val1 = fields1.get(key)
        val2 = fields2.get(key)

        if val1 == val2:
            status = "same"
        elif val1 is None:
            status = "added"
        elif val2 is None:
            status = "removed"
        else:
            status = "modified"

        field_diffs[key] = {
            "status": status,
            "entity1_value": val1,
            "entity2_value": val2,
        }

    # Calculate markdown body diff
    body_diff = ""
    if body1 != body2:
        body_diff = "\n".join(unified_diff(
            body1.splitlines(keepends=True),
            body2.splitlines(keepends=True),
            fromfile=f"{entity_id1}.md",
            tofile=f"{entity_id2}.md",
            n=3,
        ))

    return {
        "status": "ok",
        "entity_type": entity_type,
        "comparison_type": "entity-vs-entity",
        "entity1": {
            "entity_id": entity_id1,
            "name": fields1.get(f"{entity_type}_name", fields1.get("name", "Unknown")),
            "fields": fields1,
            "markdown_length": len(body1),
        },
        "entity2": {
            "entity_id": entity_id2,
            "name": fields2.get(f"{entity_type}_name", fields2.get("name", "Unknown")),
            "fields": fields2,
            "markdown_length": len(body2),
        },
        "field_differences": field_diffs,
        "markdown_diff": body_diff,
        "summary": {
            "fields_same": len([k for k, v in field_diffs.items() if v["status"] == "same"]),
            "fields_modified": len([k for k, v in field_diffs.items() if v["status"] == "modified"]),
            "fields_added": len([k for k, v in field_diffs.items() if v["status"] == "added"]),
            "fields_removed": len([k for k, v in field_diffs.items() if v["status"] == "removed"]),
        },
    }


@router.post("/compare/versions")
async def compare_versions(request: VersionComparisonRequest):
    """
    Compare same entity at two different git commits.

    Shows field and content differences between versions.
    """
    entity_type = request.entity_type
    entity_id = request.entity_id
    commit1 = request.commit1
    commit2 = request.commit2
    context = 3  # Default context lines

    # Validate commits exist
    for commit in [commit1, commit2]:
        verify = await _run_git("cat-file", "-t", commit, check=False, cwd=BRAINS_ROOT)
        if verify.stdout.strip() != "commit":
            raise HTTPException(status_code=404, detail=f"Commit not found: {commit}")

    # Get entity file path
    entity_path = _entity_file(entity_type, entity_id)
    rel_path = _relative_path(entity_path)

    # Get content from both commits
    data1 = await _get_entity_content(entity_type, entity_id, commit1)
    data2 = await _get_entity_content(entity_type, entity_id, commit2)

    fields1 = data1.get("frontmatter", {})
    fields2 = data2.get("frontmatter", {})
    body1 = data1.get("body", "")
    body2 = data2.get("body", "")

    # Calculate field differences
    all_keys = set(fields1.keys()) | set(fields2.keys())
    field_diffs = {}

    for key in all_keys:
        val1 = fields1.get(key)
        val2 = fields2.get(key)

        if val1 == val2:
            status = "same"
        elif val1 is None:
            status = "added"
        elif val2 is None:
            status = "removed"
        else:
            status = "modified"

        field_diffs[key] = {
            "status": status,
            "version1_value": val1,
            "version2_value": val2,
        }

    # Get git diff for the file
    file_diff = await _get_git_diff(commit1, commit2, rel_path, BRAINS_ROOT, context)

    return {
        "status": "ok",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "comparison_type": "version-vs-version",
        "version1": {
            "commit": commit1,
            "name": fields1.get(f"{entity_type}_name", fields1.get("name", "Unknown")),
            "fields": fields1,
            "markdown_length": len(body1),
        },
        "version2": {
            "commit": commit2,
            "name": fields2.get(f"{entity_type}_name", fields2.get("name", "Unknown")),
            "fields": fields2,
            "markdown_length": len(body2),
        },
        "field_differences": field_diffs,
        "file_diff": file_diff,
        "summary": {
            "fields_same": len([k for k, v in field_diffs.items() if v["status"] == "same"]),
            "fields_modified": len([k for k, v in field_diffs.items() if v["status"] == "modified"]),
            "fields_added": len([k for k, v in field_diffs.items() if v["status"] == "added"]),
            "fields_removed": len([k for k, v in field_diffs.items() if v["status"] == "removed"]),
        },
    }


@router.post("/compare/template")
async def compare_template(request: TemplateComparisonRequest):
    """
    Compare entity against its template defaults.

    Shows which fields have been customized from the template.
    """
    entity_type = request.entity_type
    entity_id = request.entity_id

    # Get the entity
    data = await _get_entity_content(entity_type, entity_id)
    entity_fields = data.get("frontmatter", {})
    entity_body = data.get("body", "")

    # Get the template
    template_path = BRAINS_ROOT / "templates" / "Standard" / f"{entity_type.upper()}_TEMPLATE.md"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template not found: {template_path}")

    template_content = template_path.read_text(encoding="utf-8")
    template_fields, template_body = _parse_markdown_frontmatter(template_content)

    # Calculate differences
    all_keys = set(entity_fields.keys()) | set(template_fields.keys())
    differences = {}

    for key in sorted(all_keys):
        entity_val = entity_fields.get(key)
        template_val = template_fields.get(key)

        if entity_val == template_val:
            status = "unchanged"
        elif entity_val is None:
            status = "template_value_only"
        elif template_val is None:
            status = "entity_value_only"
        elif entity_val != template_val:
            status = "customized"
        else:
            status = "unchanged"

        differences[key] = {
            "status": status,
            "template_default": template_val,
            "entity_value": entity_val,
        }

    # Markdown comparison
    body_diff = ""
    if entity_body != template_body:
        body_diff = "\n".join(unified_diff(
            template_body.splitlines(keepends=True),
            entity_body.splitlines(keepends=True),
            fromfile=f"{entity_type.upper()}_TEMPLATE.md",
            tofile=f"{entity_id}.md",
            n=3,
        ))

    # Calculate customization stats
    customized_fields = [k for k, v in differences.items() if v["status"] in ("customized", "entity_value_only")]
    unchanged_fields = [k for k, v in differences.items() if v["status"] == "unchanged"]
    template_defaults_used = [k for k, v in differences.items() if v["status"] == "template_value_only"]

    return {
        "status": "ok",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "comparison_type": "entity-vs-template",
        "template": {
            "name": f"{entity_type.upper()}_TEMPLATE.md",
            "path": str(template_path.relative_to(BRAINS_ROOT)),
            "fields": template_fields,
            "markdown_length": len(template_body),
        },
        "entity": {
            "entity_id": entity_id,
            "name": entity_fields.get(f"{entity_type}_name", entity_fields.get("name", "Unknown")),
            "fields": entity_fields,
            "markdown_length": len(entity_body),
        },
        "differences": differences,
        "markdown_diff": body_diff,
        "summary": {
            "total_fields": len(all_keys),
            "customized": len(customized_fields),
            "unchanged": len(unchanged_fields),
            "using_template_defaults": len(template_defaults_used),
        },
        "customization_stats": {
            "customized_fields": customized_fields,
            "unchanged_fields": unchanged_fields,
            "template_defaults_used": template_defaults_used,
        },
    }


@router.post("/compare/batch")
async def compare_batch(request: EntityComparisonRequest):
    """
    Batch comparison endpoint for frontend efficiency.

    Runs all three comparison types and returns aggregated results.
    """
    entity_type = request.entity_type
    entity_id1 = request.entity_id1
    entity_id2 = request.entity_id2

    results = {
        "status": "ok",
        "entity_type": entity_type,
        "entity1": entity_id1,
        "entity2": entity_id2,
    }

    # Run comparisons
    try:
        entity_result = await compare_entities(request)
        results["entity_comparison"] = entity_result
    except Exception as e:
        results["entity_comparison_error"] = str(e)

    return results
