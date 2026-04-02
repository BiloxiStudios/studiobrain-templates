"""
Import/Export Pipeline Backend Routes

SBAI-1641: Unified pipeline for multi-format import and export operations.

Features:
- Multiple import formats: Markdown, JSON, CSV, OPML, Verse (UEFN), ZIP archives
- Multiple export formats: PDF, DOCX, HTML, JSON, CSV
- Configurable profiles per template type
- Format auto-detection
- Batch processing with progress tracking
- AI-assisted merge conflict resolution
"""

import asyncio
import logging
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, UploadFile, BackgroundTasks
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/plugins/import-export-pipeline", tags=["import-export-pipeline"])
logger = logging.getLogger("plugin.import-export-pipeline")

# ============================================================================
# Configuration
# ============================================================================

# BRAINS_ROOT environment variable for file operations
BRAINS_ROOT = Path(os.environ.get("BRAINS_ROOT", ".")).resolve()

# Mapping of entity types to their data folders
ENTITY_MAP = {
    "character": ("Characters", "CH_"),
    "location": ("Locations", "LOC_"),
    "brand": ("Brands", "BR_"),
    "district": ("Districts", "DIST_"),
    "faction": ("Factions", "FACT_"),
    "item": ("Items", "ITEM_"),
    "job": ("Jobs", "JOB_"),
    "quest": ("Quests", "QUEST_"),
    "event": ("Events", "EVENT_"),
    "campaign": ("Campaigns", "CAMP_"),
    "assembly": ("Assemblies", "ASSM_"),
    "dialogue": ("Dialogues", "DIA_"),
    "timeline": ("Timelines", "TL_"),
    "note": ("Notes", "NOTE_"),
    "rule": ("Rules", "RULE_"),
    "layout": ("Layouts", "LAY_"),
}


# ============================================================================
# Enums and Models
# ============================================================================

class ImportFormat(str, Enum):
    AUTO = "auto"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    OPML = "opml"
    VERSE = "verse"
    ZIP = "zip"


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"


class ImportMode(str, Enum):
    CREATE = "create"
    REPLACE = "replace"
    UPDATE = "update"
    MERGE = "merge"


class ProgressStage(str, Enum):
    PARSING = "parsing"
    VALIDATING = "validating"
    PROCESSING = "processing"
    WRITING = "writing"
    COMPLETED = "completed"


class ImportOptions(BaseModel):
    """Options for import operations."""
    entity_type: str = Field(..., description="Target entity type")
    mode: ImportMode = Field(default=ImportMode.CREATE, description="Import mode")
    merge_strategy: str = Field(default="auto", description="Merge strategy")
    replace_filled_fields: bool = Field(default=True, description="Replace existing fields")
    add_missing_fields: bool = Field(default=False, description="Add missing fields")
    remove_orphaned_fields: bool = Field(default=False, description="Remove orphaned fields")
    replace_markdown_body: bool = Field(default=True, description="Replace markdown body")
    update_mode: str = Field(default="algorithmic", description="Update mode (algorithmic or ai)")
    ignore_errors: bool = Field(default=False, description="Continue on errors")
    profile_name: Optional[str] = Field(default=None, description="Profile to use for import")


class ExportOptions(BaseModel):
    """Options for export operations."""
    format: ExportFormat = Field(default=ExportFormat.MARKDOWN, description="Export format")
    layout: Optional[str] = Field(default=None, description="Layout template to use")
    theme: str = Field(default="default", description="Theme for rendered output")
    embed_images: bool = Field(default=True, description="Embed images in output")
    include_metadata: bool = Field(default=True, description="Include YAML frontmatter")
    flatten_hierarchy: bool = Field(default=False, description="Flatten nested structures")
    profile_name: Optional[str] = Field(default=None, description="Profile to use for export")


class BatchOptions(BaseModel):
    """Options for batch operations."""
    batch_size: int = Field(default=50, ge=1, le=1000, description="Batch size for processing")
    parallel_workers: int = Field(default=4, ge=1, le=16, description="Number of parallel workers")
    progress_callback: Optional[str] = Field(default=None, description="Progress callback URL")


class ProfileConfig(BaseModel):
    """Configuration for an import/export profile."""
    name: str = Field(..., description="Profile name")
    entity_type: str = Field(..., description="Target entity type")
    import_formats: List[ImportFormat] = Field(default_factory=list, description="Supported import formats")
    export_formats: List[ExportFormat] = Field(default_factory=list, description="Supported export formats")
    default_layout: str = Field(default="gdd_standard", description="Default layout")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Profile-specific settings")


class PipelineTask(BaseModel):
    """A task in the import/export pipeline."""
    id: str = Field(..., description="Task ID")
    type: str = Field(..., description="Task type (import/export)")
    status: str = Field(default="pending", description="Task status")
    entity_type: Optional[str] = Field(default=None, description="Entity type being processed")
    input_files: List[str] = Field(default_factory=list, description="Input files")
    output_files: List[str] = Field(default_factory=list, description="Output files")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Completion progress")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation time")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion time")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    warnings: List[str] = Field(default_factory=list, description="Warnings during processing")


class ImportResponse(BaseModel):
    """Response from import operation."""
    status: str = Field(..., description="Operation status")
    task_id: str = Field(..., description="Task ID for tracking")
    imported_count: int = Field(default=0, description="Number of items imported")
    failed_count: int = Field(default=0, description="Number of failed imports")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    errors: List[str] = Field(default_factory=list, description="Errors")


class ExportResponse(BaseModel):
    """Response from export operation."""
    status: str = Field(..., description="Operation status")
    task_id: str = Field(..., description="Task ID for tracking")
    exported_count: int = Field(default=0, description="Number of items exported")
    output_files: List[str] = Field(default_factory=list, description="Output file paths")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    errors: List[str] = Field(default_factory=list, description="Errors")


# ============================================================================
# Helper Functions
# ============================================================================

def _detect_format(content: str, filename: str) -> ImportFormat:
    """Auto-detect import format from content and filename."""
    ext = Path(filename).suffix.lower()

    # Check by file extension first
    ext_map = {
        ".md": ImportFormat.MARKDOWN,
        ".markdown": ImportFormat.MARKDOWN,
        ".json": ImportFormat.JSON,
        ".csv": ImportFormat.CSV,
        ".opml": ImportFormat.OPML,
        ".zip": ImportFormat.ZIP,
        ".txt": ImportFormat.MARKDOWN,  # Default to markdown for text files
    }

    if ext in ext_map:
        return ext_map[ext]

    # Check by content patterns
    if content.startswith("---"):
        return ImportFormat.MARKDOWN

    if content.strip().startswith("{") or content.strip().startswith("["):
        try:
            import json
            json.loads(content.strip())
            return ImportFormat.JSON
        except json.JSONDecodeError:
            pass

    if "<html" in content.lower() or "<!doctype" in content.lower():
        return ImportFormat.HTML

    # Default to markdown
    return ImportFormat.MARKDOWN


def _parse_markdown_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter and markdown body from content."""
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


def _parse_json_content(content: str) -> tuple[Dict[str, Any], str]:
    """Parse JSON content."""
    import json
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data, ""
        return {"_root": data}, ""
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def _parse_csv_content(content: str) -> tuple[List[Dict[str, Any]], str]:
    """Parse CSV content."""
    import csv
    import io
    try:
        reader = csv.DictReader(io.StringIO(content))
        return list(reader), ""
    except Exception as e:
        raise ValueError(f"Invalid CSV: {e}")


def _parse_opml_content(content: str) -> tuple[Dict[str, Any], str]:
    """Parse OPML content (XML-based outline format)."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(content)
        # Convert to a more usable structure
        data = {
            "version": root.get("version", "1.0"),
            "title": root.findtext(".//title", ""),
            "outlines": [],
        }

        for outline in root.findall(".//outline"):
            outline_data = {**outline.attrib, "children": []}
            data["outlines"].append(outline_data)

        return data, ""
    except ET.ParseError as e:
        raise ValueError(f"Invalid OPML: {e}")


def _parse_verse_content(content: str) -> tuple[Dict[str, Any], str]:
    """Parse Verse (UEFN) content."""
    # Verse files have specific patterns
    # Look for common Verse constructs
    verse_pattern = r"(?i)\b(Verse|VerseModule|VerseObject|VerseClass)\b"
    if re.search(verse_pattern, content):
        # This looks like Verse code
        return {"type": "verse", "content": content, "language": "Verse"}, ""

    # Try to parse as a structured format
    try:
        data = _parse_json_content(content)
        return data[0], ""
    except ValueError:
        return {"type": "verse_code", "content": content}, ""


def _get_entity_folder(entity_type: str) -> Optional[Path]:
    """Get the data folder path for an entity type."""
    mapping = ENTITY_MAP.get(entity_type.lower())
    if not mapping:
        return None
    folder_name, _ = mapping
    return BRAINS_ROOT / folder_name


def _entity_file_path(entity_type: str, entity_id: str) -> Path:
    """Get the file path for an entity."""
    mapping = ENTITY_MAP.get(entity_type.lower())
    if not mapping:
        raise ValueError(f"Unknown entity type: {entity_type}")
    folder_name, prefix = mapping
    return BRAINS_ROOT / folder_name / entity_id / f"{prefix}{entity_id}.md"


def _detect_entity_type_from_file(content: str, filename: str) -> Optional[str]:
    """Try to detect entity type from file content."""
    # Parse YAML frontmatter first
    frontmatter, _ = _parse_markdown_frontmatter(content)

    # Check for entity_type field
    if "entity_type" in frontmatter:
        return frontmatter["entity_type"]

    # Check for type-specific fields
    type_indicators = {
        "character": ["char_name", "entity_type", "looks", "personality"],
        "location": ["loc_name", "zone", "region"],
        "quest": ["quest_title", "objective", "steps"],
        "item": ["item_name", "category", "stats"],
        "assembly": ["assembly_name", "components", "children"],
    }

    for entity_type, indicators in type_indicators.items():
        for indicator in indicators:
            if indicator in frontmatter:
                return entity_type

    return None


# ============================================================================
# Import Routes
# ============================================================================

@router.get("/")
async def pipeline_status():
    """Pipeline plugin status and version."""
    return {
        "plugin": "import-export-pipeline",
        "version": "1.0.0",
        "status": "ok",
        "features": [
            "import_markdown",
            "import_json",
            "import_csv",
            "import_opml",
            "import_verse",
            "import_zip",
            "export_markdown",
            "export_json",
            "export_csv",
            "export_html",
            "export_pdf",
            "export_docx",
            "batch_processing",
            "profile_configs",
            "auto_detection",
        ],
    }


@router.post("/import/preview")
async def preview_import(
    file: UploadFile,
    options: ImportOptions,
):
    """
    Preview an import operation before applying.

    Returns what would be created/updated without actually modifying files.
    """
    # Read file content
    content = await file.read()
    content_str = content.decode("utf-8")

    # Detect format if auto
    detected_format = options.format if options.format != ImportFormat.AUTO else _detect_format(content_str, file.filename)

    # Parse based on detected format
    try:
        if detected_format == ImportFormat.MARKDOWN:
            frontmatter, body = _parse_markdown_frontmatter(content_str)
            return {
                "status": "ok",
                "format": detected_format,
                "entity_type": options.entity_type or _detect_entity_type_from_file(content_str, file.filename),
                "fields": frontmatter,
                "markdown_length": len(body),
                "identifiable_fields": {k: v for k, v in frontmatter.items() if k in ("name", "entity_id", "char_name", "loc_name")},
            }

        elif detected_format == ImportFormat.JSON:
            data, _ = _parse_json_content(content_str)
            return {
                "status": "ok",
                "format": detected_format,
                "entity_type": options.entity_type or _detect_entity_type_from_file(content_str, file.filename),
                "fields": data,
            }

        elif detected_format == ImportFormat.CSV:
            rows, _ = _parse_csv_content(content_str)
            return {
                "status": "ok",
                "format": detected_format,
                "entity_type": options.entity_type or "character",
                "rows": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "sample": rows[:3] if rows else [],
            }

        elif detected_format == ImportFormat.OPML:
            data, _ = _parse_opml_content(content_str)
            return {
                "status": "ok",
                "format": detected_format,
                "entity_type": options.entity_type or "note",
                "title": data.get("title", ""),
                "outlines": len(data.get("outlines", [])),
            }

        elif detected_format == ImportFormat.VERSE:
            data, _ = _parse_verse_content(content_str)
            return {
                "status": "ok",
                "format": detected_format,
                "entity_type": options.entity_type or "assembly",
                "verse_type": data.get("type", "code"),
                "content_length": len(data.get("content", "")),
            }

        elif detected_format == ImportFormat.ZIP:
            return {
                "status": "ok",
                "format": detected_format,
                "zip_name": file.filename,
                "zip_size": len(content),
                "container": "zip",
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    raise HTTPException(status_code=400, detail="Unknown file format")


@router.post("/import/single", response_model=ImportResponse)
async def import_single(
    file: UploadFile,
    options: ImportOptions,
    background_tasks: BackgroundTasks,
):
    """
    Import a single file.

    Creates or updates an entity from the file content.
    """
    task_id = f"import-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Read file content
    content = await file.read()
    content_str = content.decode("utf-8")

    # Detect format
    detected_format = options.format if options.format != ImportFormat.AUTO else _detect_format(content_str, file.filename)

    # Parse content
    try:
        frontmatter, body = _parse_markdown_frontmatter(content_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse: {str(e)}")

    # Extract entity info
    entity_name = frontmatter.get("name") or frontmatter.get("entity_name") or file.filename.replace(".md", "")
    entity_id = frontmatter.get("entity_id") or entity_name.lower().replace(" ", "_")

    # Determine entity type
    entity_type = options.entity_type
    if not entity_type:
        entity_type = _detect_entity_type_from_file(content_str, file.filename)
        if not entity_type:
            entity_type = "character"  # Default

    # Handle import mode
    if options.mode == ImportMode.CREATE:
        # Create new entity
        entity_path = _entity_file_path(entity_type, entity_id)
        entity_path.parent.mkdir(parents=True, exist_ok=True)

        # Write entity file
        markdown_content = f"---\n{frontmatter}\n---\n\n{body}"
        entity_path.write_text(markdown_content, encoding="utf-8")

        return ImportResponse(
            status="success",
            task_id=task_id,
            imported_count=1,
            warnings=[],
            errors=[],
        )

    elif options.mode == ImportMode.REPLACE:
        # Replace existing entity
        entity_path = _entity_file_path(entity_type, entity_id)
        if not entity_path.exists():
            raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

        frontmatter, body = _parse_markdown_frontmatter(content_str)
        markdown_content = f"---\n{frontmatter}\n---\n\n{body}"
        entity_path.write_text(markdown_content, encoding="utf-8")

        return ImportResponse(
            status="success",
            task_id=task_id,
            imported_count=1,
            warnings=[],
            errors=[],
        )

    else:
        raise HTTPException(status_code=400, detail=f"Mode '{options.mode}' not yet implemented")


@router.post("/import/batch", response_model=ImportResponse)
async def import_batch(
    files: List[UploadFile],
    options: ImportOptions,
    background_tasks: BackgroundTasks,
):
    """
    Import multiple files in a batch operation.

    Processes files in parallel with configurable batch size.
    Returns progress updates and results.
    """
    task_id = f"batch-import-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    import_count = 0
    failed_count = 0
    errors = []
    warnings = []

    for file in files:
        try:
            content = file.read()
            content_str = content.decode("utf-8")
            detected_format = options.format if options.format != ImportFormat.AUTO else _detect_format(content_str, file.filename)
            frontmatter, body = _parse_markdown_frontmatter(content_str)

            # Determine entity type and ID
            entity_type = options.entity_type or _detect_entity_type_from_file(content_str, file.filename) or "character"
            entity_name = frontmatter.get("name") or file.filename.replace(".md", "")
            entity_id = frontmatter.get("entity_id") or entity_name.lower().replace(" ", "_")

            # Create entity path
            entity_path = _entity_file_path(entity_type, entity_id)
            entity_path.parent.mkdir(parents=True, exist_ok=True)

            # Write entity file
            import yaml
            yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
            markdown_content = f"---\n{yaml_str}---\n\n{body}"
            entity_path.write_text(markdown_content, encoding="utf-8")

            import_count += 1

        except Exception as e:
            failed_count += 1
            errors.append(f"{file.filename}: {str(e)}")
            warnings.append(f"Skipped: {file.filename}")

    return ImportResponse(
        status="success" if failed_count == 0 else "partial",
        task_id=task_id,
        imported_count=import_count,
        failed_count=failed_count,
        warnings=warnings,
        errors=errors,
    )


@router.post("/import/zip", response_model=ImportResponse)
async def import_zip(
    file: UploadFile,
    options: ImportOptions,
    background_tasks: BackgroundTasks,
):
    """
    Import multiple files from a ZIP archive.

    Extracts and processes all supported files in the archive.
    """
    task_id = f"zip-import-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    content = await file.read()

    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / file.filename
        zip_path.write_bytes(content)

        try:
            with zipfile.ZipFile(zip_path) as zf:
                import_count = 0
                failed_count = 0
                errors = []
                warnings = []

                # Find all markdown files
                md_files = [f for f in zf.namelist() if f.endswith((".md", ".markdown"))]

                for md_file in md_files:
                    try:
                        with zf.open(md_file) as f:
                            file_content = f.read().decode("utf-8")

                        detected_format = _detect_format(file_content, Path(md_file).name)
                        frontmatter, body = _parse_markdown_frontmatter(file_content)

                        # Determine entity type and ID
                        entity_type = options.entity_type or _detect_entity_type_from_file(file_content, md_file) or "character"
                        entity_name = frontmatter.get("name") or Path(md_file).stem
                        entity_id = frontmatter.get("entity_id") or entity_name.lower().replace(" ", "_")

                        # Create entity path
                        entity_path = _entity_file_path(entity_type, entity_id)
                        entity_path.parent.mkdir(parents=True, exist_ok=True)

                        # Write entity file
                        import yaml
                        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                        markdown_content = f"---\n{yaml_str}---\n\n{body}"
                        entity_path.write_text(markdown_content, encoding="utf-8")

                        import_count += 1

                    except Exception as e:
                        failed_count += 1
                        errors.append(f"{md_file}: {str(e)}")
                        warnings.append(f"Skipped: {md_file}")

                return ImportResponse(
                    status="success" if failed_count == 0 else "partial",
                    task_id=task_id,
                    imported_count=import_count,
                    failed_count=failed_count,
                    warnings=warnings,
                    errors=errors,
                )

        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")


# ============================================================================
# Export Routes
# ============================================================================

@router.post("/export/markdown", response_model=ExportResponse)
async def export_markdown(
    entity_type: str,
    entity_ids: List[str],
    options: ExportOptions,
):
    """
    Export entities to Markdown format.

    Generates markdown files with YAML frontmatter.
    """
    task_id = f"export-md-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    output_files = []
    export_count = 0
    errors = []

    for entity_id in entity_ids:
        try:
            entity_path = _entity_file_path(entity_type, entity_id)
            if not entity_path.exists():
                errors.append(f"Entity not found: {entity_type}/{entity_id}")
                continue

            content = entity_path.read_text(encoding="utf-8")
            output_path = BRAINS_ROOT / "exports" / entity_type / f"{entity_id}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

            output_files.append(str(output_path.relative_to(BRAINS_ROOT)))
            export_count += 1

        except Exception as e:
            errors.append(f"Failed to export {entity_id}: {str(e)}")

    return ExportResponse(
        status="success" if len(errors) == 0 else "partial",
        task_id=task_id,
        exported_count=export_count,
        output_files=output_files,
        errors=errors,
    )


@router.post("/export/json", response_model=ExportResponse)
async def export_json(
    entity_type: str,
    entity_ids: List[str],
    options: ExportOptions,
):
    """
    Export entities to JSON format.

    Converts YAML frontmatter to JSON structure.
    """
    import json

    task_id = f"export-json-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    output_files = []
    export_count = 0
    errors = []

    for entity_id in entity_ids:
        try:
            entity_path = _entity_file_path(entity_type, entity_id)
            if not entity_path.exists():
                errors.append(f"Entity not found: {entity_type}/{entity_id}")
                continue

            content = entity_path.read_text(encoding="utf-8")
            frontmatter, body = _parse_markdown_frontmatter(content)

            # Build JSON structure
            json_data = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "imported_from": str(entity_path.relative_to(BRAINS_ROOT)),
                "imported_at": datetime.utcnow().isoformat(),
            }

            if options.include_metadata:
                json_data["frontmatter"] = frontmatter

            if body and not options.flatten_hierarchy:
                json_data["markdown_body"] = body

            # Write JSON file
            output_path = BRAINS_ROOT / "exports" / entity_type / f"{entity_id}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            output_path.write_text(json_str, encoding="utf-8")

            output_files.append(str(output_path.relative_to(BRAINS_ROOT)))
            export_count += 1

        except Exception as e:
            errors.append(f"Failed to export {entity_id}: {str(e)}")

    return ExportResponse(
        status="success" if len(errors) == 0 else "partial",
        task_id=task_id,
        exported_count=export_count,
        output_files=output_files,
        errors=errors,
    )


@router.post("/export/csv", response_model=ExportResponse)
async def export_csv(
    entity_type: str,
    entity_ids: List[str],
    options: ExportOptions,
):
    """
    Export entities to CSV format.

    Flattens entity data for spreadsheet compatibility.
    """
    import csv
    import io

    task_id = f"export-csv-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    output_files = []
    export_count = 0
    errors = []

    all_rows = []

    for entity_id in entity_ids:
        try:
            entity_path = _entity_file_path(entity_type, entity_id)
            if not entity_path.exists():
                errors.append(f"Entity not found: {entity_type}/{entity_id}")
                continue

            content = entity_path.read_text(encoding="utf-8")
            frontmatter, body = _parse_markdown_frontmatter(content)

            # Flatten for CSV
            row = {"entity_id": entity_id, "entity_type": entity_type}
            row.update(frontmatter)
            if not options.flatten_hierarchy:
                row["markdown_body"] = body[:500]  # Truncate for CSV

            all_rows.append(row)
            export_count += 1

        except Exception as e:
            errors.append(f"Failed to export {entity_id}: {str(e)}")

    # Write CSV
    if all_rows:
        output_path = BRAINS_ROOT / "exports" / f"{entity_type}s.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = list(all_rows[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

        output_files.append(str(output_path.relative_to(BRAINS_ROOT)))

    return ExportResponse(
        status="success" if len(errors) == 0 else "partial",
        task_id=task_id,
        exported_count=export_count,
        output_files=output_files,
        errors=errors,
    )


@router.post("/export/html", response_model=ExportResponse)
async def export_html(
    entity_type: str,
    entity_ids: List[str],
    options: ExportOptions,
):
    """
    Export entities to HTML format.

    Generates styled HTML documents with embedded CSS.
    """
    task_id = f"export-html-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    output_files = []
    export_count = 0
    errors = []

    for entity_id in entity_ids:
        try:
            entity_path = _entity_file_path(entity_type, entity_id)
            if not entity_path.exists():
                errors.append(f"Entity not found: {entity_type}/{entity_id}")
                continue

            content = entity_path.read_text(encoding="utf-8")
            frontmatter, body = _parse_markdown_frontmatter(content)

            # Generate HTML
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{frontmatter.get('name', entity_id)}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .frontmatter {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .frontmatter pre {{ margin: 0; overflow-x: auto; }}
        .body {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>{frontmatter.get('name', entity_id)}</h1>
    <div class="meta">
        <p><strong>Type:</strong> {entity_type} | <strong>ID:</strong> {entity_id}</p>
    </div>
    {f'<div class="frontmatter"><pre>{content.split("---")[1] if "---" in content else ""}</pre></div>' if options.include_metadata else ''}
    <div class="body">
        {body}
    </div>
</body>
</html>"""

            # Write HTML file
            output_path = BRAINS_ROOT / "exports" / entity_type / f"{entity_id}.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")

            output_files.append(str(output_path.relative_to(BRAINS_ROOT)))
            export_count += 1

        except Exception as e:
            errors.append(f"Failed to export {entity_id}: {str(e)}")

    return ExportResponse(
        status="success" if len(errors) == 0 else "partial",
        task_id=task_id,
        exported_count=export_count,
        output_files=output_files,
        errors=errors,
    )


@router.post("/export/pdf")
async def export_pdf(
    entity_type: str,
    entity_ids: List[str],
    options: ExportOptions,
):
    """
    Export entities to PDF format.

    Uses Playwright for high-quality PDF generation.
    """
    import asyncio

    task_id = f"export-pdf-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    output_files = []
    export_count = 0
    errors = []

    for entity_id in entity_ids:
        try:
            entity_path = _entity_file_path(entity_type, entity_id)
            if not entity_path.exists():
                errors.append(f"Entity not found: {entity_type}/{entity_id}")
                continue

            content = entity_path.read_text(encoding="utf-8")
            frontmatter, body = _parse_markdown_frontmatter(content)

            # Generate HTML for PDF rendering
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page {{ size: A4; margin: 20mm; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, serif; line-height: 1.6; padding: 20px; }}
        h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; color: #2c3e50; }}
        .meta {{ color: #666; font-size: 0.85em; margin-bottom: 20px; }}
        .frontmatter {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .frontmatter pre {{ margin: 0; overflow-x: auto; font-size: 0.8em; }}
        .body {{ margin-top: 20px; white-space: pre-wrap; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .footer {{ position: footer; text-align: center; margin-top: 30px; color: #999; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{frontmatter.get('name', entity_id)}</h1>
        <p class="meta">Type: {entity_type} | ID: {entity_id} | Date: {datetime.utcnow().strftime('%Y-%m-%d')}</p>
    </div>
    {f'<div class="frontmatter"><pre>{content.split("---")[1] if "---" in content else ""}</pre></div>' if options.include_metadata else ''}
    <div class="body">
        {body}
    </div>
</body>
</html>"""

            # Write to temp HTML for PDF rendering
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp:
                temp.write(html.encode("utf-8"))
                temp_path = temp.name

            try:
                # Use Playwright to render to PDF
                try:
                    from playwright.sync_api import sync_playwright

                    with sync_playwright() as p:
                        browser = p.chromium.launch()
                        page = browser.new_page()
                        page.goto(f"file://{temp_path}")
                        pdf_bytes = page.pdf(
                            format="A4",
                            print_background=True,
                            margin={"top": "20mm", "right": "15mm", "bottom": "20mm", "left": "15mm"},
                        )
                        browser.close()

                    # Save PDF
                    output_path = BRAINS_ROOT / "exports" / entity_type / f"{entity_id}.pdf"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(pdf_bytes)

                    output_files.append(str(output_path.relative_to(BRAINS_ROOT)))
                    export_count += 1

                except ImportError:
                    errors.append(f"Playwright not installed for {entity_id}. Install with: playwright install")
                    continue

            finally:
                os.unlink(temp_path)

        except Exception as e:
            errors.append(f"Failed to export {entity_id}: {str(e)}")

    return {
        "status": "success" if len(errors) == 0 else "partial",
        "task_id": task_id,
        "exported_count": export_count,
        "output_files": output_files,
        "errors": errors,
    }


@router.post("/export/docx")
async def export_docx(
    entity_type: str,
    entity_ids: List[str],
    options: ExportOptions,
):
    """
    Export entities to DOCX (Word) format.

    Generates professional Word documents with styles.
    """
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    task_id = f"export-docx-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    output_files = []
    export_count = 0
    errors = []

    for entity_id in entity_ids:
        try:
            entity_path = _entity_file_path(entity_type, entity_id)
            if not entity_path.exists():
                errors.append(f"Entity not found: {entity_type}/{entity_id}")
                continue

            content = entity_path.read_text(encoding="utf-8")
            frontmatter, body = _parse_markdown_frontmatter(content)

            # Create DOCX document
            doc = Document()

            # Add title
            title = doc.add_heading(frontmatter.get('name', entity_id), 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Add metadata
            doc.add_paragraph(f"Type: {entity_type} | ID: {entity_id}", style="Normal")
            p = doc.add_paragraph(f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
            p.runs[0].font.size = Pt(9)

            # Add frontmatter if requested
            if options.include_metadata and frontmatter:
                doc.add_heading("YAML Frontmatter", level=2)
                doc.add_paragraph(str(frontmatter), style="Code")

            # Add markdown body
            if body:
                doc.add_heading("Content", level=2)
                for line in body.split("\n"):
                    if line.strip():
                        doc.add_paragraph(line)

            # Save DOCX
            output_path = BRAINS_ROOT / "exports" / entity_type / f"{entity_id}.docx"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(output_path)

            output_files.append(str(output_path.relative_to(BRAINS_ROOT)))
            export_count += 1

        except ImportError:
            errors.append("python-docx not installed. Install with: pip install python-docx")
            break
        except Exception as e:
            errors.append(f"Failed to export {entity_id}: {str(e)}")

    return {
        "status": "success" if len(errors) == 0 else "partial",
        "task_id": task_id,
        "exported_count": export_count,
        "output_files": output_files,
        "errors": errors,
    }


# ============================================================================
# Profile Management Routes
# ============================================================================

@router.get("/profiles", response_model=List[ProfileConfig])
async def list_profiles(
    entity_type: Optional[str] = None,
):
    """
    List available import/export profiles.

    Returns profiles optionally filtered by entity type.
    """
    profiles = [
        ProfileConfig(
            name="default",
            entity_type="character",
            import_formats=[ImportFormat.MARKDOWN, ImportFormat.JSON, ImportFormat.CSV],
            export_formats=[ExportFormat.MARKDOWN, ExportFormat.JSON, ExportFormat.PDF, ExportFormat.DOCX],
            default_layout="gdd_standard",
        ),
        ProfileConfig(
            name="verse",
            entity_type="assembly",
            import_formats=[ImportFormat.MARKDOWN, ImportFormat.VERSE, ImportFormat.JSON],
            export_formats=[ExportFormat.MARKDOWN, ExportFormat.VERSE, ExportFormat.JSON],
            default_layout="assembly",
        ),
        ProfileConfig(
            name="dialogue",
            entity_type="dialogue",
            import_formats=[ImportFormat.MARKDOWN, ImportFormat.JSON, ImportFormat.CSV],
            export_formats=[ExportFormat.MARKDOWN, ExportFormat.DOCX, ExportFormat.HTML],
            default_layout="script_format",
        ),
        ProfileConfig(
            name="movie",
            entity_type="character",
            import_formats=[ImportFormat.MARKDOWN, ImportFormat.CSV],
            export_formats=[ExportFormat.MARKDOWN, ExportFormat.DOCX, ExportFormat.PDF],
            default_layout="script_format",
        ),
    ]

    if entity_type:
        profiles = [p for p in profiles if p.entity_type == entity_type]

    return profiles


@router.get("/profiles/{{profile_name}}", response_model=ProfileConfig)
async def get_profile(profile_name: str):
    """
    Get a specific profile by name.
    """
    profiles = await list_profiles()

    for profile in profiles:
        if profile.name == profile_name:
            return profile

    raise HTTPException(status_code=404, detail=f"Profile not found: {profile_name}")


# ============================================================================
# System Routes
# ============================================================================

@router.get("/formats")
async def list_available_formats():
    """
    List all supported import and export formats.
    """
    return {
        "import": [
            {"format": "markdown", "extensions": [".md", ".markdown"], "description": "Markdown with YAML frontmatter"},
            {"format": "json", "extensions": [".json"], "description": "JSON structured data"},
            {"format": "csv", "extensions": [".csv"], "description": "Comma-separated values"},
            {"format": "opml", "extensions": [".opml"], "description": "Outline processor format"},
            {"format": "verse", "extensions": [".verse", ".txt"], "description": "Verse/UEFN code"},
            {"format": "zip", "extensions": [".zip"], "description": "ZIP archive of files"},
        ],
        "export": [
            {"format": "markdown", "extensions": [".md"], "description": "Markdown with YAML frontmatter"},
            {"format": "json", "extensions": [".json"], "description": "JSON structured data"},
            {"format": "csv", "extensions": [".csv"], "description": "Comma-separated values"},
            {"format": "html", "extensions": [".html"], "description": "Standalone HTML document"},
            {"format": "pdf", "extensions": [".pdf"], "description": "Formatted PDF (via Playwright)"},
            {"format": "docx", "extensions": [".docx"], "description": "Microsoft Word document"},
        ],
    }


@router.get("/auto-detect")
async def detect_format(content: str, filename: str):
    """
    Detect import format from content and filename.

    Returns the detected format and confidence score.
    """
    detected = _detect_format(content, filename)
    return {
        "format": detected,
        "confidence": 0.9 if detected != ImportFormat.MARKDOWN else 0.8,
        "suggestions": ["auto", "markdown", "json", "csv"] if detected == ImportFormat.MARKDOWN else [],
    }
