"""
Unreal Engine Exporter Plugin — backend routes.

Provides API endpoints for previewing, generating, and exporting
Unreal Engine DataAssets, DataTables, and C++ USTRUCT headers from
City of Brains entity data.
"""

import os
import re
import csv
import io
import json
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

logger = logging.getLogger("plugin.unreal-exporter")
router = APIRouter()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

SUPPORTED_ENTITY_TYPES = [
    "character", "location", "item", "faction", "brand", "district", "job",
]

TYPE_PREFIX_MAP = {
    "character": "CH",
    "location": "LOC",
    "item": "ITEM",
    "faction": "FAC",
    "brand": "BR",
    "district": "DIST",
    "job": "JOB",
}

# Map Python/YAML types to Unreal C++ types
UE_TYPE_MAP = {
    "str": "FString",
    "string": "FString",
    "int": "int32",
    "integer": "int32",
    "float": "float",
    "number": "float",
    "bool": "bool",
    "boolean": "bool",
    "list": "TArray<FString>",
    "array": "TArray<FString>",
    "dict": "FString",     # Serialize complex objects as JSON strings
    "object": "FString",
}

# Fields to skip when generating USTRUCTs (internal metadata)
SKIP_FIELDS = {
    "id", "entity_id", "created_at", "updated_at", "version",
    "file_path", "markdown_content",
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


def _scan_entities(entity_type: str) -> list[dict]:
    """Scan all entities of a given type and return a list of frontmatter dicts."""
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
        fm["_entity_id"] = entry
        fm["_entity_type"] = entity_type
        results.append(fm)

    return results


def _get_entity_name(fm: dict) -> str:
    """Extract the display name from frontmatter."""
    return (
        fm.get("name")
        or fm.get("character_name")
        or fm.get("business_name")
        or fm.get("item_name")
        or fm.get("faction_name")
        or fm.get("brand_name")
        or fm.get("district_name")
        or fm.get("job_name")
        or fm.get("location_name")
        or fm.get("_entity_id", "Unknown").replace("_", " ").title()
    )


def _infer_ue_type(value) -> str:
    """Infer an Unreal Engine C++ type from a Python value."""
    if isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int32"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, list):
        return "TArray<FString>"
    elif isinstance(value, dict):
        return "FString"
    else:
        return "FString"


def _sanitize_ue_name(name: str) -> str:
    """Sanitize a string to be a valid C++ identifier."""
    # PascalCase conversion
    parts = re.split(r'[_\s\-]+', name)
    result = "".join(p.capitalize() for p in parts if p)
    # Remove non-alphanumeric
    result = re.sub(r'[^a-zA-Z0-9]', '', result)
    # Ensure it doesn't start with a digit
    if result and result[0].isdigit():
        result = "_" + result
    return result


def _sanitize_field_name(name: str) -> str:
    """Convert a frontmatter key to a valid C++ field name (PascalCase)."""
    parts = re.split(r'[_\s\-]+', name)
    return "".join(p.capitalize() for p in parts if p)


def _value_to_ue_literal(value) -> str:
    """Convert a Python value to a string suitable for UE DataTable CSV."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        # Serialize arrays as JSON strings for DataTable import
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _build_schema_from_entities(entities: list[dict]) -> dict[str, str]:
    """
    Analyze all entities of a type to determine the merged field schema.
    Returns dict of { field_name: ue_cpp_type }.
    """
    schema = {}
    for fm in entities:
        for key, value in fm.items():
            if key.startswith("_") or key in SKIP_FIELDS:
                continue
            ue_type = _infer_ue_type(value)
            # Keep the broadest type if conflicting
            if key not in schema:
                schema[key] = ue_type
            elif schema[key] != ue_type:
                # Promote to FString on conflict
                schema[key] = "FString"
    return schema


def _generate_ustruct(entity_type: str, schema: dict[str, str],
                      struct_prefix: str = "F",
                      module_name: str = "CityOfBrains",
                      as_table_row: bool = True) -> str:
    """Generate a complete C++ USTRUCT header from a field schema."""
    struct_name = f"{struct_prefix}{_sanitize_ue_name(entity_type)}Data"
    base_class = " : public FTableRowBase" if as_table_row else ""
    api_macro = f"{module_name.upper()}_API " if module_name else ""

    lines = []
    lines.append(f"// Auto-generated by City of Brains - Unreal Engine Exporter")
    lines.append(f"// Entity Type: {entity_type}")
    lines.append(f"// Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"")
    lines.append(f"#pragma once")
    lines.append(f"")
    lines.append(f'#include "CoreMinimal.h"')
    if as_table_row:
        lines.append(f'#include "Engine/DataTable.h"')
    lines.append(f'#include "{struct_name}.generated.h"')
    lines.append(f"")
    lines.append(f"USTRUCT(BlueprintType)")
    lines.append(f"struct {api_macro}{struct_name}{base_class}")
    lines.append(f"{{")
    lines.append(f"    GENERATED_BODY()")
    lines.append(f"")

    for field_key, ue_type in schema.items():
        field_name = _sanitize_field_name(field_key)
        lines.append(f"    /** {field_key} */")
        lines.append(f"    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = \"{_sanitize_ue_name(entity_type)}\")")
        lines.append(f"    {ue_type} {field_name};")
        lines.append(f"")

    lines.append(f"}};")
    return "\n".join(lines)


def _build_dataasset_json(entity_type: str, fm: dict, schema: dict[str, str]) -> dict:
    """Build an Unreal-compatible DataAsset JSON payload from entity frontmatter."""
    struct_name = f"F{_sanitize_ue_name(entity_type)}Data"
    entity_id = fm.get("_entity_id", "unknown")
    name = _get_entity_name(fm)

    properties = {}
    for field_key in schema:
        value = fm.get(field_key)
        if value is None:
            continue
        prop_name = _sanitize_field_name(field_key)
        if isinstance(value, (list, dict)):
            properties[prop_name] = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, bool):
            properties[prop_name] = value
        elif isinstance(value, (int, float)):
            properties[prop_name] = value
        else:
            properties[prop_name] = str(value)

    return {
        "Type": struct_name,
        "Name": f"DA_{_sanitize_ue_name(entity_type)}_{_sanitize_ue_name(entity_id)}",
        "Label": name,
        "EntityType": entity_type,
        "EntityId": entity_id,
        "Properties": properties,
        "ExportedAt": datetime.utcnow().isoformat() + "Z",
        "Source": "CityOfBrains",
    }


def _build_datatable_csv(entity_type: str, entities: list[dict],
                         schema: dict[str, str]) -> str:
    """Build a DataTable-compatible CSV string from all entities of a type."""
    output = io.StringIO()

    # Header row: first column is always "---" (row name) for UE DataTable import
    field_keys = list(schema.keys())
    header = ["---"] + [_sanitize_field_name(k) for k in field_keys]
    writer = csv.writer(output)
    writer.writerow(header)

    for fm in entities:
        entity_id = fm.get("_entity_id", "unknown")
        row_name = f"{_sanitize_ue_name(entity_type)}_{_sanitize_ue_name(entity_id)}"
        row = [row_name]
        for field_key in field_keys:
            value = fm.get(field_key)
            row.append(_value_to_ue_literal(value))
        writer.writerow(row)

    return output.getvalue()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class BatchExportRequest(BaseModel):
    entity_types: list[str] = []
    format: str = "both"          # "dataasset", "datatable", "both"
    output_path: Optional[str] = None


class SingleExportRequest(BaseModel):
    format: str = "dataasset"     # "dataasset" or "json"
    output_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status and overview."""
    return {
        "plugin": "unreal-exporter",
        "version": "1.0.0",
        "status": "ok",
        "supported_entity_types": SUPPORTED_ENTITY_TYPES,
        "endpoints": [
            "GET  /                           - This status page",
            "GET  /preview/{type}/{id}        - Preview DataAsset JSON",
            "GET  /ustruct/{type}             - Generate C++ USTRUCT header",
            "GET  /datatable/{type}           - Export DataTable CSV",
            "POST /export/{type}/{id}         - Export single DataAsset",
            "POST /batch-export               - Batch export entities",
            "GET  /schema/{type}              - Get inferred field schema",
            "GET  /entity-types               - List available entity types with counts",
        ],
    }


@router.get("/entity-types")
async def get_entity_types():
    """List available entity types with entity counts."""
    result = []
    for etype in SUPPORTED_ENTITY_TYPES:
        entities = _scan_entities(etype)
        if entities:
            result.append({
                "type": etype,
                "count": len(entities),
                "struct_name": f"F{_sanitize_ue_name(etype)}Data",
            })
    return {"entity_types": result}


@router.get("/schema/{entity_type}")
async def get_schema(entity_type: str):
    """Get the inferred UE type schema for an entity type."""
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")

    entities = _scan_entities(entity_type)
    if not entities:
        raise HTTPException(status_code=404, detail=f"No entities found for type: {entity_type}")

    schema = _build_schema_from_entities(entities)
    return {
        "entity_type": entity_type,
        "entity_count": len(entities),
        "fields": [
            {"name": k, "ue_type": v, "display_name": _sanitize_field_name(k)}
            for k, v in schema.items()
        ],
    }


@router.get("/preview/{entity_type}/{entity_id}")
async def preview_dataasset(entity_type: str, entity_id: str):
    """Preview the DataAsset JSON for a specific entity."""
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")

    filepath = _get_entity_file(entity_type, entity_id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    fm = _parse_frontmatter(filepath)
    fm["_entity_id"] = entity_id
    fm["_entity_type"] = entity_type

    # Build schema from all entities of this type for consistency
    all_entities = _scan_entities(entity_type)
    schema = _build_schema_from_entities(all_entities)

    dataasset = _build_dataasset_json(entity_type, fm, schema)
    return dataasset


@router.get("/ustruct/{entity_type}")
async def generate_ustruct(
    entity_type: str,
    prefix: str = Query("F", description="Struct name prefix"),
    module: str = Query("CityOfBrains", description="UE module name"),
    as_table_row: bool = Query(True, description="Inherit from FTableRowBase"),
):
    """Generate a C++ USTRUCT header file for the given entity type."""
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")

    entities = _scan_entities(entity_type)
    if not entities:
        raise HTTPException(status_code=404, detail=f"No entities found for type: {entity_type}")

    schema = _build_schema_from_entities(entities)
    header_code = _generate_ustruct(
        entity_type, schema,
        struct_prefix=prefix,
        module_name=module,
        as_table_row=as_table_row,
    )

    return PlainTextResponse(content=header_code, media_type="text/plain")


@router.get("/datatable/{entity_type}")
async def export_datatable_csv(entity_type: str):
    """Export all entities of a type as a DataTable-compatible CSV."""
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")

    entities = _scan_entities(entity_type)
    if not entities:
        raise HTTPException(status_code=404, detail=f"No entities found for type: {entity_type}")

    schema = _build_schema_from_entities(entities)
    csv_content = _build_datatable_csv(entity_type, entities, schema)

    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="DT_{_sanitize_ue_name(entity_type)}.csv"'
        },
    )


@router.post("/export/{entity_type}/{entity_id}")
async def export_single(entity_type: str, entity_id: str, req: Optional[SingleExportRequest] = None):
    """Export a single entity as a DataAsset JSON file."""
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: {entity_type}")

    filepath = _get_entity_file(entity_type, entity_id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    fm = _parse_frontmatter(filepath)
    fm["_entity_id"] = entity_id
    fm["_entity_type"] = entity_type

    all_entities = _scan_entities(entity_type)
    schema = _build_schema_from_entities(all_entities)
    dataasset = _build_dataasset_json(entity_type, fm, schema)

    # Determine output path
    output_path = None
    if req and req.output_path:
        output_path = req.output_path
    else:
        # Default: write to a local export directory next to the plugin
        export_dir = os.path.join(os.path.dirname(__file__), "..", "exports", entity_type)
        os.makedirs(export_dir, exist_ok=True)
        asset_name = dataasset["Name"]
        output_path = os.path.join(export_dir, f"{asset_name}.json")

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(dataasset, fh, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

    logger.info("Exported DataAsset: %s -> %s", f"{entity_type}/{entity_id}", output_path)

    return {
        "success": True,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "asset_name": dataasset["Name"],
        "output_path": os.path.abspath(output_path),
        "format": "dataasset_json",
    }


@router.post("/batch-export")
async def batch_export(req: BatchExportRequest):
    """
    Batch export multiple entity types as DataAssets and/or DataTables.

    If entity_types is empty, exports all supported types that have entities.
    """
    types_to_export = req.entity_types if req.entity_types else SUPPORTED_ENTITY_TYPES
    export_format = req.format or "both"

    # Determine base output directory
    base_dir = req.output_path if req.output_path else os.path.join(
        os.path.dirname(__file__), "..", "exports"
    )
    os.makedirs(base_dir, exist_ok=True)

    results = {
        "exported_types": [],
        "total_entities": 0,
        "total_files": 0,
        "errors": [],
        "output_path": os.path.abspath(base_dir),
    }

    for etype in types_to_export:
        if etype not in SUPPORTED_ENTITY_TYPES:
            results["errors"].append(f"Skipped unsupported type: {etype}")
            continue

        entities = _scan_entities(etype)
        if not entities:
            continue

        schema = _build_schema_from_entities(entities)
        type_result = {
            "type": etype,
            "entity_count": len(entities),
            "files": [],
        }

        # Export DataAsset JSON files
        if export_format in ("dataasset", "both"):
            asset_dir = os.path.join(base_dir, "DataAssets", _sanitize_ue_name(etype))
            os.makedirs(asset_dir, exist_ok=True)

            for fm in entities:
                try:
                    dataasset = _build_dataasset_json(etype, fm, schema)
                    asset_path = os.path.join(asset_dir, f"{dataasset['Name']}.json")
                    with open(asset_path, "w", encoding="utf-8") as fh:
                        json.dump(dataasset, fh, indent=2, ensure_ascii=False)
                    type_result["files"].append(asset_path)
                    results["total_files"] += 1
                except Exception as e:
                    results["errors"].append(
                        f"Failed to export {etype}/{fm.get('_entity_id', '?')}: {str(e)}"
                    )

        # Export DataTable CSV
        if export_format in ("datatable", "both"):
            dt_dir = os.path.join(base_dir, "DataTables")
            os.makedirs(dt_dir, exist_ok=True)

            try:
                csv_content = _build_datatable_csv(etype, entities, schema)
                csv_path = os.path.join(dt_dir, f"DT_{_sanitize_ue_name(etype)}.csv")
                with open(csv_path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(csv_content)
                type_result["files"].append(csv_path)
                results["total_files"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to export DataTable for {etype}: {str(e)}")

        # Generate USTRUCT header
        if export_format in ("both", "dataasset"):
            header_dir = os.path.join(base_dir, "Source")
            os.makedirs(header_dir, exist_ok=True)

            try:
                header_code = _generate_ustruct(etype, schema)
                struct_name = f"F{_sanitize_ue_name(etype)}Data"
                header_path = os.path.join(header_dir, f"{struct_name}.h")
                with open(header_path, "w", encoding="utf-8") as fh:
                    fh.write(header_code)
                type_result["files"].append(header_path)
                results["total_files"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to generate USTRUCT for {etype}: {str(e)}")

        results["total_entities"] += len(entities)
        results["exported_types"].append(type_result)

    logger.info(
        "Batch export complete: %d types, %d entities, %d files",
        len(results["exported_types"]),
        results["total_entities"],
        results["total_files"],
    )

    return results
