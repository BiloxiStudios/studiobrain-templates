"""
PDF Bible Exporter — Backend Routes

Provides endpoints for generating print-ready HTML exports of entities.
These HTML documents include @media print CSS and are designed to be
printed to PDF via the browser's native print dialog (Ctrl+P / Cmd+P).

Routes (mounted at /api/ext/pdf-exporter/...):
  GET  /                                  — plugin status
  GET  /templates                         — list available export templates
  GET  /preview/{entity_type}/{entity_id} — HTML preview of a single entity
  GET  /export/{entity_type}/{entity_id}  — downloadable print-ready HTML
  POST /batch                             — batch export multiple entities
"""

import logging

import re

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# ─── Data root resolution ──────────────────────────────────────────────
# backend/routes.py → pdf-exporter/ → _Plugins/ → Brains/
DATA_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# ─── Entity file prefix mapping ───────────────────────────────────────
FILE_PREFIX_MAP = {
    "character": "CH_",
    "location": "LOC_",
    "brand": "BR_",
    "district": "DIST_",
    "faction": "FAC_",
    "item": "ITEM_",
    "job": "JOB_",
    "quest": "QUEST_",
    "event": "EVENT_",
    "campaign": "CAMP_",
    "assembly": "ASSM_",
}

FOLDER_NAME_MAP = {
    "character": "Characters",
    "location": "Locations",
    "brand": "Brands",
    "district": "Districts",
    "faction": "Factions",
    "item": "Items",
    "job": "Jobs",
    "quest": "Quests",
    "event": "Events",
    "campaign": "Campaigns",
    "assembly": "Assemblies",
}

# Entity name field mapping
NAME_FIELD_MAP = {
    "character": "character_name",
    "location": "name",
    "brand": "brand_name",
    "district": "district_name",
    "faction": "name",
    "item": "item_name",
    "job": "job_name",
    "quest": "quest_name",
    "event": "event_name",
    "campaign": "campaign_name",
    "assembly": "assembly_name",
}

# ─── Template definitions ─────────────────────────────────────────────

TEMPLATES = {
    "character-sheet": {
        "id": "character-sheet",
        "name": "Character Sheet",
        "description": "Full character dossier with portrait, stats, relationships, and backstory",
        "entity_types": ["character"],
        "icon": "user",
        "sections": [
            "header", "portrait", "overview", "physical",
            "personality", "relationships", "backstory", "inventory", "dialogue"
        ],
    },
    "location-guide": {
        "id": "location-guide",
        "name": "Location Guide",
        "description": "Detailed location profile with images, atmosphere, and points of interest",
        "entity_types": ["location"],
        "icon": "map-pin",
        "sections": [
            "header", "image", "overview", "atmosphere",
            "features", "hazards", "npcs", "connections"
        ],
    },
    "faction-dossier": {
        "id": "faction-dossier",
        "name": "Faction Dossier",
        "description": "Intelligence briefing on a faction: leadership, territory, operations",
        "entity_types": ["faction"],
        "icon": "shield",
        "sections": [
            "header", "overview", "leadership", "territory",
            "operations", "relationships", "resources"
        ],
    },
    "item-catalog": {
        "id": "item-catalog",
        "name": "Item Catalog Entry",
        "description": "Detailed item specification with properties and lore",
        "entity_types": ["item"],
        "icon": "package",
        "sections": [
            "header", "image", "overview", "properties",
            "lore", "acquisition"
        ],
    },
    "entity-summary": {
        "id": "entity-summary",
        "name": "Entity Summary",
        "description": "Compact summary card for any entity type",
        "entity_types": ["character", "location", "faction", "item", "brand",
                         "district", "job", "quest", "event", "campaign", "assembly"],
        "icon": "file-text",
        "sections": ["header", "image", "overview", "details"],
    },
    "world-bible": {
        "id": "world-bible",
        "name": "World Bible",
        "description": "Complete world document: all characters, locations, factions compiled into one export",
        "entity_types": ["character", "location", "faction", "item"],
        "icon": "book-open",
        "sections": ["cover", "toc", "characters", "locations", "factions", "items"],
    },
}

# ─── Request models ───────────────────────────────────────────────────

class BatchExportRequest(BaseModel):
    entity_type: str
    entity_ids: List[str]
    template: str = "entity-summary"
    include_toc: bool = True

# ─── Helper functions ─────────────────────────────────────────────────

def get_plugin_settings() -> Dict[str, Any]:
    """Read pdf-exporter settings from the DB-backed settings service."""
    from services.plugin_settings_service import get_all_settings
    defaults = {
        "studio_name": "City of Brains Studio",
        "studio_logo_url": "",
        "primary_color": "#3b82f6",
        "secondary_color": "#1e293b",
        "include_images": True,
        "include_relationships": True,
        "page_size": "Letter",
        "custom_css": "",
    }
    defaults.update(get_all_settings("pdf-exporter"))
    return defaults

def load_entity(entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """Load an entity's YAML frontmatter and markdown body from disk."""
    folder = FOLDER_NAME_MAP.get(entity_type)
    prefix = FILE_PREFIX_MAP.get(entity_type)
    if not folder or prefix is None:
        return None

    filepath = DATA_ROOT / folder / entity_id / f"{prefix}{entity_id}.md"
    if not filepath.is_file():
        return None

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error("Failed to read %s: %s", filepath, exc)
        return None

    frontmatter: Dict[str, Any] = {}
    markdown_body: str = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}
            markdown_body = parts[2].strip()

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "frontmatter": frontmatter,
        "markdown": markdown_body,
    }

def get_entity_name(entity_type: str, frontmatter: Dict[str, Any], entity_id: str) -> str:
    """Extract display name from frontmatter, falling back to a formatted ID."""
    name_field = NAME_FIELD_MAP.get(entity_type, "name")
    name = frontmatter.get(name_field)
    if not name:
        name = frontmatter.get("name")
    if not name:
        # Convert entity_id to title case
        name = entity_id.replace("_", " ").replace("-", " ").title()
    return str(name)

def get_entity_image_path(entity_type: str, entity_id: str, frontmatter: Dict[str, Any]) -> Optional[str]:
    """Get the primary image URL for an entity."""
    primary = frontmatter.get("primary_image", "")
    if primary:
        # Return as a backend-served file URL
        return f"http://localhost:8201/api/files/{primary}"

    images = frontmatter.get("images", [])
    if images and isinstance(images, list) and len(images) > 0:
        folder = FOLDER_NAME_MAP.get(entity_type, "")
        return f"http://localhost:8201/api/files/{folder}/{entity_id}/images/{images[0]}"

    return None

def list_entities_of_type(entity_type: str) -> List[Dict[str, str]]:
    """List all entity IDs and names for a given type."""
    folder = FOLDER_NAME_MAP.get(entity_type)
    prefix = FILE_PREFIX_MAP.get(entity_type)
    if not folder or prefix is None:
        return []

    type_dir = DATA_ROOT / folder
    if not type_dir.is_dir():
        return []

    entities = []
    for child in sorted(type_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        md_file = child / f"{prefix}{child.name}.md"
        if md_file.is_file():
            data = load_entity(entity_type, child.name)
            name = child.name.replace("_", " ").title()
            if data:
                name = get_entity_name(entity_type, data["frontmatter"], child.name)
            entities.append({"id": child.name, "name": name})

    return entities

def format_value(value: Any, indent: int = 0) -> str:
    """Format a YAML value for display in HTML."""
    if value is None:
        return '<span class="null-value">--</span>'
    if isinstance(value, bool):
        return '<span class="bool-value">Yes</span>' if value else '<span class="bool-value">No</span>'
    if isinstance(value, list):
        if not value:
            return '<span class="null-value">--</span>'
        if all(isinstance(v, str) for v in value):
            return ", ".join(str(v) for v in value)
        items = []
        for v in value:
            if isinstance(v, dict):
                parts = []
                for dk, dv in v.items():
                    if dv is not None and dv != "" and dv != []:
                        parts.append(f"<strong>{dk}:</strong> {format_value(dv)}")
                items.append("<br>".join(parts))
            else:
                items.append(str(v))
        return "<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>"
    if isinstance(value, dict):
        if not value:
            return '<span class="null-value">--</span>'
        parts = []
        for k, v in value.items():
            if v is not None and v != "" and v != []:
                parts.append(f"<strong>{k}:</strong> {format_value(v)}")
        return "<br>".join(parts) if parts else '<span class="null-value">--</span>'
    return str(value)

# ─── CSS Generation ───────────────────────────────────────────────────

def generate_print_css(settings: Dict[str, Any]) -> str:
    """Generate the print-optimized CSS for exports."""
    primary = settings.get("primary_color", "#3b82f6")
    secondary = settings.get("secondary_color", "#1e293b")
    page_size = settings.get("page_size", "Letter").lower()
    custom_css = settings.get("custom_css", "")

    return f"""
    @page {{
        size: {page_size};
        margin: 0.75in;
    }}

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #1a1a2e;
        background: #ffffff;
    }}

    .export-container {{
        max-width: 8.5in;
        margin: 0 auto;
        padding: 20px 0;
    }}

    /* ── Header ────────────────────────────── */
    .export-header {{
        border-bottom: 3px solid {primary};
        padding-bottom: 16px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }}

    .export-header .title-block h1 {{
        font-size: 28pt;
        font-weight: 700;
        color: {secondary};
        letter-spacing: -0.5px;
        margin: 0 0 4px 0;
    }}

    .export-header .title-block .subtitle {{
        font-size: 11pt;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 500;
    }}

    .export-header .studio-brand {{
        text-align: right;
        font-size: 9pt;
        color: #94a3b8;
    }}

    .export-header .studio-brand img {{
        max-height: 40px;
        margin-bottom: 4px;
    }}

    /* ── Portrait / Image ─────────────────── */
    .entity-portrait {{
        float: right;
        margin: 0 0 16px 24px;
        max-width: 240px;
    }}

    .entity-portrait img {{
        width: 100%;
        border-radius: 8px;
        border: 2px solid {primary};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}

    .entity-portrait .caption {{
        text-align: center;
        font-size: 8pt;
        color: #94a3b8;
        margin-top: 4px;
    }}

    /* ── Sections ──────────────────────────── */
    .section {{
        margin-bottom: 24px;
        page-break-inside: avoid;
    }}

    .section-title {{
        font-size: 14pt;
        font-weight: 700;
        color: {primary};
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .section-content {{
        font-size: 11pt;
        line-height: 1.7;
    }}

    /* ── Stat Block ────────────────────────── */
    .stat-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 8px 24px;
        margin-bottom: 16px;
    }}

    .stat-item {{
        display: flex;
        align-items: baseline;
        padding: 4px 0;
        border-bottom: 1px dotted #e2e8f0;
    }}

    .stat-label {{
        font-weight: 600;
        color: {secondary};
        font-size: 9pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        min-width: 120px;
        flex-shrink: 0;
    }}

    .stat-value {{
        font-size: 11pt;
        color: #334155;
    }}

    .stat-value .null-value {{
        color: #cbd5e1;
        font-style: italic;
    }}

    /* ── Relationship Cards ───────────────── */
    .relationship-list {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 12px;
    }}

    .relationship-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid {primary};
        border-radius: 4px;
        padding: 10px 14px;
        page-break-inside: avoid;
    }}

    .relationship-card .rel-name {{
        font-weight: 700;
        color: {secondary};
        font-size: 11pt;
    }}

    .relationship-card .rel-role {{
        font-size: 9pt;
        color: {primary};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .relationship-card .rel-notes {{
        font-size: 10pt;
        color: #64748b;
        margin-top: 4px;
    }}

    /* ── Dialogue Samples ─────────────────── */
    .dialogue-block {{
        background: #f8fafc;
        border-left: 3px solid {primary};
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 0 4px 4px 0;
        page-break-inside: avoid;
    }}

    .dialogue-context {{
        font-size: 9pt;
        color: #94a3b8;
        font-style: italic;
        margin-bottom: 4px;
    }}

    .dialogue-line {{
        font-size: 11pt;
        color: #1e293b;
        font-style: italic;
    }}

    /* ── Table of Contents ─────────────────── */
    .toc {{
        margin-bottom: 32px;
        page-break-after: always;
    }}

    .toc h2 {{
        font-size: 20pt;
        color: {secondary};
        margin-bottom: 16px;
        border-bottom: 2px solid {primary};
        padding-bottom: 8px;
    }}

    .toc-section {{
        margin-bottom: 12px;
    }}

    .toc-section-title {{
        font-size: 12pt;
        font-weight: 700;
        color: {primary};
        margin-bottom: 4px;
    }}

    .toc-entry {{
        display: flex;
        justify-content: space-between;
        padding: 3px 0;
        border-bottom: 1px dotted #e2e8f0;
        font-size: 10pt;
    }}

    .toc-entry a {{
        color: #334155;
        text-decoration: none;
    }}

    .toc-page {{
        color: #94a3b8;
    }}

    /* ── Cover Page ────────────────────────── */
    .cover-page {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 90vh;
        text-align: center;
        page-break-after: always;
    }}

    .cover-page h1 {{
        font-size: 36pt;
        color: {secondary};
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 8px;
    }}

    .cover-page .cover-subtitle {{
        font-size: 14pt;
        color: {primary};
        text-transform: uppercase;
        letter-spacing: 4px;
        font-weight: 500;
        margin-bottom: 40px;
    }}

    .cover-page .cover-meta {{
        font-size: 10pt;
        color: #94a3b8;
    }}

    .cover-page .cover-logo img {{
        max-height: 80px;
        margin-bottom: 24px;
    }}

    .cover-page .cover-divider {{
        width: 120px;
        height: 3px;
        background: {primary};
        margin: 24px auto;
    }}

    /* ── Entity separator ─────────────────── */
    .entity-separator {{
        page-break-before: always;
    }}

    /* ── Category header ──────────────────── */
    .category-header {{
        page-break-before: always;
        padding: 40px 0 20px 0;
        border-bottom: 3px solid {primary};
        margin-bottom: 24px;
    }}

    .category-header h2 {{
        font-size: 24pt;
        color: {secondary};
        text-transform: uppercase;
        letter-spacing: 3px;
    }}

    /* ── Markdown body ─────────────────────── */
    .markdown-body {{
        font-size: 11pt;
        line-height: 1.7;
    }}

    .markdown-body h1,
    .markdown-body h2,
    .markdown-body h3 {{
        color: {secondary};
        margin-top: 16px;
        margin-bottom: 8px;
    }}

    .markdown-body p {{
        margin-bottom: 8px;
    }}

    .markdown-body ul, .markdown-body ol {{
        padding-left: 24px;
        margin-bottom: 8px;
    }}

    /* ── Footer ────────────────────────────── */
    .export-footer {{
        border-top: 1px solid #e2e8f0;
        padding-top: 12px;
        margin-top: 32px;
        font-size: 8pt;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
    }}

    /* ── Print overrides ───────────────────── */
    @media print {{
        body {{
            background: white;
        }}

        .export-container {{
            max-width: none;
            padding: 0;
        }}

        .no-print {{
            display: none !important;
        }}

        .entity-portrait img {{
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}

        .section {{
            page-break-inside: avoid;
        }}

        .entity-separator {{
            page-break-before: always;
        }}
    }}

    /* ── Screen-only toolbar ───────────────── */
    @media screen {{
        .print-toolbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: {secondary};
            color: #e2e8f0;
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 9999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}

        .print-toolbar .toolbar-title {{
            font-weight: 600;
            font-size: 14px;
        }}

        .print-toolbar button {{
            background: {primary};
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }}

        .print-toolbar button:hover {{
            opacity: 0.9;
        }}

        .export-container {{
            margin-top: 60px;
        }}
    }}

    {custom_css}
    """

# ─── HTML Renderers ───────────────────────────────────────────────────

def render_character_sheet(data: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """Render a full character sheet HTML."""
    fm = data["frontmatter"]
    md = data["markdown"]
    entity_id = data["entity_id"]
    name = get_entity_name("character", fm, entity_id)
    image_url = get_entity_image_path("character", entity_id, fm) if settings.get("include_images") else None

    # Build portrait section
    portrait_html = ""
    if image_url:
        portrait_html = f"""
        <div class="entity-portrait">
            <img src="{image_url}" alt="{name}" onerror="this.parentElement.style.display='none'">
            <div class="caption">{name}</div>
        </div>"""

    # Build stat grid for physical attributes
    physical_fields = [
        ("Age", fm.get("age")),
        ("Species", fm.get("species")),
        ("Gender", fm.get("gender")),
        ("Height", fm.get("height")),
        ("Build", format_value(fm.get("build"))),
        ("Hair", fm.get("hair_color", {}).get("name") if isinstance(fm.get("hair_color"), dict) else fm.get("hair_color")),
        ("Eyes", fm.get("eye_color", {}).get("name") if isinstance(fm.get("eye_color"), dict) else fm.get("eye_color")),
        ("Birth Year", fm.get("birth_year")),
        ("Character Type", fm.get("character_type")),
        ("Faction", fm.get("faction")),
    ]

    physical_html = '<div class="stat-grid">'
    for label, value in physical_fields:
        if value is not None and value != "" and value != "--":
            physical_html += f"""
            <div class="stat-item">
                <span class="stat-label">{label}</span>
                <span class="stat-value">{format_value(value)}</span>
            </div>"""
    physical_html += "</div>"

    # Distinguishing features
    features = fm.get("distinguishing_features", [])
    features_html = ""
    if features:
        features_html = '<div class="section"><h3 class="section-title">Distinguishing Features</h3><div class="section-content"><ul>'
        for feat in features:
            if isinstance(feat, list):
                features_html += f"<li>{', '.join(str(f) for f in feat)}</li>"
            elif feat:
                features_html += f"<li>{feat}</li>"
        features_html += "</ul></div></div>"

    # Bio summary
    bio = fm.get("ai_bio_summary", [])
    bio_html = ""
    if bio:
        if isinstance(bio, list):
            bio_text = " ".join(str(b) for b in bio)
        else:
            bio_text = str(bio)
        bio_html = f'<div class="section"><h3 class="section-title">Biography</h3><div class="section-content"><p>{bio_text}</p></div></div>'

    # Profile description
    profile = fm.get("ai_profile_description", [])
    profile_html = ""
    if profile:
        if isinstance(profile, list):
            profile_text = " ".join(str(p) for p in profile)
        else:
            profile_text = str(profile)
        profile_html = f'<div class="section"><h3 class="section-title">Profile Description</h3><div class="section-content"><p>{profile_text}</p></div></div>'

    # Fears
    fears = fm.get("fears", [])
    fears_html = ""
    if fears:
        fears_html = '<div class="section"><h3 class="section-title">Fears</h3><div class="section-content"><ul>'
        for fear in fears:
            if isinstance(fear, list):
                fears_html += f"<li>{', '.join(str(f) for f in fear)}</li>"
            elif fear:
                fears_html += f"<li>{fear}</li>"
        fears_html += "</ul></div></div>"

    # Relationships (friends, family, enemies)
    relationships_html = ""
    if settings.get("include_relationships", True):
        for rel_type, rel_label in [("friends", "Allies & Friends"), ("family", "Family"), ("enemies", "Enemies & Rivals")]:
            rels = fm.get(rel_type, [])
            if rels and isinstance(rels, list):
                relationships_html += f'<div class="section"><h3 class="section-title">{rel_label}</h3><div class="relationship-list">'
                for rel in rels:
                    if isinstance(rel, dict):
                        rel_name = rel.get("name", "Unknown")
                        if isinstance(rel_name, list):
                            rel_name = ", ".join(str(n) for n in rel_name)
                        rel_role = rel.get("relation", rel.get("nickname", ""))
                        if isinstance(rel_role, list):
                            rel_role = ", ".join(str(r) for r in rel_role)
                        rel_notes = rel.get("notes", "")
                        if isinstance(rel_notes, list):
                            rel_notes = " ".join(str(n) for n in rel_notes)
                        rel_reason = rel.get("reason", "")
                        if isinstance(rel_reason, list):
                            rel_reason = " ".join(str(r) for r in rel_reason)
                        note_text = rel_notes or rel_reason
                        relationships_html += f"""
                        <div class="relationship-card">
                            <div class="rel-name">{rel_name}</div>
                            <div class="rel-role">{rel_role}</div>
                            {"<div class='rel-notes'>" + note_text + "</div>" if note_text else ""}
                        </div>"""
                relationships_html += "</div></div>"

    # Dialogue samples
    dialogue_html = ""
    dialogues = fm.get("dialogue_samples", [])
    if dialogues and isinstance(dialogues, list):
        dialogue_html = '<div class="section"><h3 class="section-title">Dialogue Samples</h3><div class="section-content">'
        for sample in dialogues[:6]:  # Limit to 6 samples
            if isinstance(sample, dict):
                ctx = sample.get("context", "")
                if isinstance(ctx, list):
                    ctx = " ".join(str(c) for c in ctx)
                line = sample.get("line", "")
                if isinstance(line, list):
                    line = " ".join(str(l) for l in line)
                dialogue_html += f"""
                <div class="dialogue-block">
                    <div class="dialogue-context">{ctx}</div>
                    <div class="dialogue-line">"{line}"</div>
                </div>"""
        dialogue_html += "</div></div>"

    # Voice style
    voice = fm.get("ai_voice_style", [])
    voice_html = ""
    if voice:
        if isinstance(voice, list):
            voice_text = " ".join(str(v) for v in voice)
        else:
            voice_text = str(voice)
        voice_html = f'<div class="section"><h3 class="section-title">Voice Style</h3><div class="section-content"><p>{voice_text}</p></div></div>'

    # Inventory
    inventory = fm.get("inventory_items", [])
    inventory_html = ""
    if inventory and isinstance(inventory, list) and any(inventory):
        inventory_html = '<div class="section"><h3 class="section-title">Inventory</h3><div class="section-content">'
        inventory_html += format_value(inventory)
        inventory_html += "</div></div>"

    # Markdown body
    body_html = ""
    if md.strip():
        body_html = f'<div class="section"><h3 class="section-title">Notes</h3><div class="section-content markdown-body">{render_markdown_simple(md)}</div></div>'

    return f"""
    {portrait_html}
    <div class="section">
        <h3 class="section-title">Attributes</h3>
        {physical_html}
    </div>
    {features_html}
    {bio_html}
    {profile_html}
    {fears_html}
    {voice_html}
    {relationships_html}
    {dialogue_html}
    {inventory_html}
    {body_html}
    """

def render_location_sheet(data: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """Render a location guide HTML."""
    fm = data["frontmatter"]
    md = data["markdown"]
    entity_id = data["entity_id"]
    name = get_entity_name("location", fm, entity_id)
    image_url = get_entity_image_path("location", entity_id, fm) if settings.get("include_images") else None

    portrait_html = ""
    if image_url:
        portrait_html = f"""
        <div class="entity-portrait">
            <img src="{image_url}" alt="{name}" onerror="this.parentElement.style.display='none'">
        </div>"""

    stat_fields = [
        ("Type", fm.get("location_type")),
        ("District", fm.get("district")),
        ("Biome", fm.get("biome")),
        ("Condition", fm.get("condition")),
        ("Enterable", fm.get("enterable")),
        ("Exterior Access", fm.get("exterior_access")),
        ("Faction Control", fm.get("faction_control")),
        ("Infection Status", fm.get("infection_status")),
        ("Building Type", fm.get("building_type")),
        ("Business Name", fm.get("business_name")),
        ("Business Type", fm.get("business_type")),
        ("Lighting", fm.get("lighting")),
        ("Crowd Behavior", fm.get("crowd_behavior")),
    ]

    stats_html = '<div class="stat-grid">'
    for label, value in stat_fields:
        if value is not None and value != "" and value != []:
            stats_html += f"""
            <div class="stat-item">
                <span class="stat-label">{label}</span>
                <span class="stat-value">{format_value(value)}</span>
            </div>"""
    stats_html += "</div>"

    desc = fm.get("description", "")
    desc_html = ""
    if desc and str(desc).strip():
        desc_html = f'<div class="section"><h3 class="section-title">Description</h3><div class="section-content"><p>{desc}</p></div></div>'

    # Hazards
    hazards = fm.get("hazards", [])
    hazards_html = ""
    if hazards:
        hazards_html = f'<div class="section"><h3 class="section-title">Hazards</h3><div class="section-content">{format_value(hazards)}</div></div>'

    # Interactive features
    features = fm.get("interactive_features", [])
    features_html = ""
    if features:
        features_html = f'<div class="section"><h3 class="section-title">Interactive Features</h3><div class="section-content">{format_value(features)}</div></div>'

    # Ambient sounds
    sounds = fm.get("ambient_sounds", [])
    sounds_html = ""
    if sounds:
        sounds_html = f'<div class="section"><h3 class="section-title">Ambient Sounds</h3><div class="section-content">{format_value(sounds)}</div></div>'

    body_html = ""
    if md.strip():
        body_html = f'<div class="section"><h3 class="section-title">Notes</h3><div class="section-content markdown-body">{render_markdown_simple(md)}</div></div>'

    return f"""
    {portrait_html}
    <div class="section">
        <h3 class="section-title">Location Details</h3>
        {stats_html}
    </div>
    {desc_html}
    {hazards_html}
    {features_html}
    {sounds_html}
    {body_html}
    """

def render_faction_sheet(data: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """Render a faction dossier HTML."""
    fm = data["frontmatter"]
    md = data["markdown"]
    entity_id = data["entity_id"]
    name = get_entity_name("faction", fm, entity_id)

    stat_fields = [
        ("Status", fm.get("status")),
        ("Ideology", fm.get("ideology")),
        ("Faction Type", fm.get("faction_type")),
    ]

    stats_html = '<div class="stat-grid">'
    for label, value in stat_fields:
        if value is not None and value != "":
            stats_html += f"""
            <div class="stat-item">
                <span class="stat-label">{label}</span>
                <span class="stat-value">{format_value(value)}</span>
            </div>"""
    stats_html += "</div>"

    # Leadership
    leadership = fm.get("leadership", [])
    leadership_html = ""
    if leadership:
        leadership_html = f'<div class="section"><h3 class="section-title">Leadership</h3><div class="section-content">{format_value(leadership)}</div></div>'

    # Territory
    territory = fm.get("territory", [])
    territory_html = ""
    if territory:
        territory_html = f'<div class="section"><h3 class="section-title">Territory</h3><div class="section-content">{format_value(territory)}</div></div>'

    # Goals
    goals = fm.get("goals", [])
    goals_html = ""
    if goals:
        goals_html = f'<div class="section"><h3 class="section-title">Goals</h3><div class="section-content">{format_value(goals)}</div></div>'

    # Allies & Enemies
    rels_html = ""
    if settings.get("include_relationships", True):
        for rel_key, rel_label in [("allies", "Allies"), ("enemies", "Enemies"), ("neutral", "Neutral")]:
            rels = fm.get(rel_key, [])
            if rels:
                rels_html += f'<div class="section"><h3 class="section-title">{rel_label}</h3><div class="section-content">{format_value(rels)}</div></div>'

    # Special capabilities
    caps = fm.get("special_capabilities", [])
    caps_html = ""
    if caps:
        caps_html = f'<div class="section"><h3 class="section-title">Special Capabilities</h3><div class="section-content">{format_value(caps)}</div></div>'

    # Weaknesses
    weak = fm.get("weaknesses", [])
    weak_html = ""
    if weak:
        weak_html = f'<div class="section"><h3 class="section-title">Weaknesses</h3><div class="section-content">{format_value(weak)}</div></div>'

    body_html = ""
    if md.strip():
        body_html = f'<div class="section"><h3 class="section-title">Notes</h3><div class="section-content markdown-body">{render_markdown_simple(md)}</div></div>'

    return f"""
    <div class="section">
        <h3 class="section-title">Faction Overview</h3>
        {stats_html}
    </div>
    {leadership_html}
    {territory_html}
    {goals_html}
    {rels_html}
    {caps_html}
    {weak_html}
    {body_html}
    """

def render_generic_sheet(data: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """Render a generic entity summary HTML."""
    fm = data["frontmatter"]
    md = data["markdown"]
    entity_type = data["entity_type"]
    entity_id = data["entity_id"]
    image_url = get_entity_image_path(entity_type, entity_id, fm) if settings.get("include_images") else None

    portrait_html = ""
    if image_url:
        portrait_html = f"""
        <div class="entity-portrait">
            <img src="{image_url}" alt="{entity_id}" onerror="this.parentElement.style.display='none'">
        </div>"""

    # Render all frontmatter as stat grid, filtering out internal/empty fields
    skip_fields = {"template_version", "comfy_workflows", "data", "images",
                   "primary_image", "audio", "dialogue_files", "fields"}

    stats_html = '<div class="stat-grid">'
    for key, value in fm.items():
        if key in skip_fields:
            continue
        if value is None or value == "" or value == [] or value == {}:
            continue
        if isinstance(value, (list, dict)) and len(str(value)) > 200:
            continue  # Skip very long nested data in summary
        label = key.replace("_", " ").title()
        stats_html += f"""
        <div class="stat-item">
            <span class="stat-label">{label}</span>
            <span class="stat-value">{format_value(value)}</span>
        </div>"""
    stats_html += "</div>"

    body_html = ""
    if md.strip():
        body_html = f'<div class="section"><h3 class="section-title">Notes</h3><div class="section-content markdown-body">{render_markdown_simple(md)}</div></div>'

    return f"""
    {portrait_html}
    <div class="section">
        <h3 class="section-title">Details</h3>
        {stats_html}
    </div>
    {body_html}
    """

def render_markdown_simple(text: str) -> str:
    """Simple markdown-to-HTML conversion for body text."""
    try:
        import markdown
        return markdown.markdown(text, extensions=["tables", "fenced_code"])
    except ImportError:
        # Fallback: basic conversion
        html = text
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = html.replace("\n\n", "</p><p>")
        html = f"<p>{html}</p>"
        return html

TEMPLATE_RENDERERS = {
    "character-sheet": render_character_sheet,
    "location-guide": render_location_sheet,
    "faction-dossier": render_faction_sheet,
    "item-catalog": render_generic_sheet,
    "entity-summary": render_generic_sheet,
}

def select_template(entity_type: str, requested: Optional[str] = None) -> str:
    """Select the best template for an entity type."""
    if requested and requested in TEMPLATES:
        return requested
    # Auto-select based on entity type
    type_defaults = {
        "character": "character-sheet",
        "location": "location-guide",
        "faction": "faction-dossier",
        "item": "item-catalog",
    }
    return type_defaults.get(entity_type, "entity-summary")

def wrap_full_html(title: str, body: str, settings: Dict[str, Any],
                   show_toolbar: bool = True) -> str:
    """Wrap content in a full HTML document with print CSS."""
    studio_name = settings.get("studio_name", "City of Brains Studio")
    logo_url = settings.get("studio_logo_url", "")
    css = generate_print_css(settings)
    now = datetime.now().strftime("%B %d, %Y")

    toolbar_html = ""
    if show_toolbar:
        toolbar_html = f"""
        <div class="print-toolbar no-print">
            <span class="toolbar-title">PDF Bible Exporter -- {title}</span>
            <div>
                <button onclick="window.print()" style="margin-right:8px;">Print / Save PDF</button>
                <button onclick="window.close()" style="background:#475569;">Close</button>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} -- {studio_name}</title>
    <style>{css}</style>
</head>
<body>
    {toolbar_html}
    <div class="export-container">
        {body}
        <div class="export-footer no-print">
            <span>Generated by {studio_name} -- PDF Bible Exporter</span>
            <span>{now}</span>
        </div>
    </div>
</body>
</html>"""

def render_entity_header(entity_type: str, entity_id: str, name: str,
                         settings: Dict[str, Any]) -> str:
    """Render the standard export header for a single entity."""
    studio_name = settings.get("studio_name", "City of Brains Studio")
    logo_url = settings.get("studio_logo_url", "")

    logo_html = ""
    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="{studio_name}">'

    return f"""
    <div class="export-header">
        <div class="title-block">
            <h1>{name}</h1>
            <div class="subtitle">{entity_type.title()}</div>
        </div>
        <div class="studio-brand">
            {logo_html}
            <div>{studio_name}</div>
        </div>
    </div>"""

# ─── API Endpoints ────────────────────────────────────────────────────

@router.get("/")
async def plugin_status():
    """Return plugin status and basic info."""
    return {
        "plugin": "pdf-exporter",
        "version": "1.0.0",
        "status": "active",
        "data_root": str(DATA_ROOT),
        "templates": len(TEMPLATES),
        "entity_types": list(FOLDER_NAME_MAP.keys()),
    }

@router.get("/templates")
async def list_templates():
    """List all available export templates."""
    return {"templates": list(TEMPLATES.values())}

@router.get("/entities/{entity_type}")
async def list_entities(entity_type: str):
    """List all entities of a given type (for batch export UI)."""
    if entity_type not in FOLDER_NAME_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
    entities = list_entities_of_type(entity_type)
    return {"entity_type": entity_type, "count": len(entities), "entities": entities}

@router.get("/preview/{entity_type}/{entity_id}")
async def preview_entity(
    entity_type: str,
    entity_id: str,
    template: Optional[str] = Query(None, description="Template ID to use"),
):
    """Generate an HTML preview of a single entity export."""
    if entity_type not in FOLDER_NAME_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    data = load_entity(entity_type, entity_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    settings = get_plugin_settings()
    template_id = select_template(entity_type, template)
    renderer = TEMPLATE_RENDERERS.get(template_id, render_generic_sheet)
    name = get_entity_name(entity_type, data["frontmatter"], entity_id)

    header = render_entity_header(entity_type, entity_id, name, settings)
    body = renderer(data, settings)

    return {"html": header + body, "name": name, "template": template_id}

@router.get("/export/{entity_type}/{entity_id}")
async def export_entity(
    entity_type: str,
    entity_id: str,
    template: Optional[str] = Query(None, description="Template ID to use"),
):
    """Generate a full print-ready HTML document for a single entity."""
    if entity_type not in FOLDER_NAME_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    data = load_entity(entity_type, entity_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_type}/{entity_id}")

    settings = get_plugin_settings()
    template_id = select_template(entity_type, template)
    renderer = TEMPLATE_RENDERERS.get(template_id, render_generic_sheet)
    name = get_entity_name(entity_type, data["frontmatter"], entity_id)

    header = render_entity_header(entity_type, entity_id, name, settings)
    content = renderer(data, settings)

    full_html = wrap_full_html(name, header + content, settings)
    return HTMLResponse(content=full_html)

@router.post("/batch")
async def batch_export(req: BatchExportRequest):
    """Batch export multiple entities into a single print-ready HTML document."""
    if req.entity_type not in FOLDER_NAME_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {req.entity_type}")

    settings = get_plugin_settings()
    studio_name = settings.get("studio_name", "City of Brains Studio")
    template_id = select_template(req.entity_type, req.template)
    renderer = TEMPLATE_RENDERERS.get(template_id, render_generic_sheet)
    now = datetime.now().strftime("%B %d, %Y")

    # Cover page
    cover = f"""
    <div class="cover-page">
        <div class="cover-logo">
            {"<img src='" + settings["studio_logo_url"] + "'>" if settings.get("studio_logo_url") else ""}
        </div>
        <h1>{req.entity_type.title()}s</h1>
        <div class="cover-subtitle">Export Collection</div>
        <div class="cover-divider"></div>
        <div class="cover-meta">
            {studio_name}<br>
            Generated {now}<br>
            {len(req.entity_ids)} {req.entity_type}(s)
        </div>
    </div>"""

    # Load all entities
    entities_data = []
    errors = []
    for eid in req.entity_ids:
        data = load_entity(req.entity_type, eid)
        if data:
            entities_data.append(data)
        else:
            errors.append(eid)

    if not entities_data:
        raise HTTPException(status_code=404, detail="No entities found")

    # Table of contents
    toc_html = ""
    if req.include_toc and len(entities_data) > 1:
        toc_html = '<div class="toc"><h2>Table of Contents</h2><div class="toc-section">'
        for i, edata in enumerate(entities_data, 1):
            name = get_entity_name(req.entity_type, edata["frontmatter"], edata["entity_id"])
            toc_html += f"""
            <div class="toc-entry">
                <a href="#entity-{edata['entity_id']}">{i}. {name}</a>
            </div>"""
        toc_html += "</div></div>"

    # Render each entity
    body_parts = [cover, toc_html]
    for i, edata in enumerate(entities_data):
        name = get_entity_name(req.entity_type, edata["frontmatter"], edata["entity_id"])
        separator = ' class="entity-separator"' if i > 0 else ""
        entity_html = f'<div id="entity-{edata["entity_id"]}"{separator}>'
        entity_html += render_entity_header(req.entity_type, edata["entity_id"], name, settings)
        entity_html += renderer(edata, settings)
        entity_html += "</div>"
        body_parts.append(entity_html)

    title = f"{req.entity_type.title()}s Collection"
    full_html = wrap_full_html(title, "\n".join(body_parts), settings)
    return HTMLResponse(content=full_html)

@router.post("/world-bible")
async def export_world_bible():
    """Generate a complete world bible with all entity types."""
    settings = get_plugin_settings()
    studio_name = settings.get("studio_name", "City of Brains Studio")
    now = datetime.now().strftime("%B %d, %Y")

    # Cover page
    cover = f"""
    <div class="cover-page">
        <div class="cover-logo">
            {"<img src='" + settings["studio_logo_url"] + "'>" if settings.get("studio_logo_url") else ""}
        </div>
        <h1>World Bible</h1>
        <div class="cover-subtitle">Complete Reference</div>
        <div class="cover-divider"></div>
        <div class="cover-meta">
            {studio_name}<br>
            Generated {now}
        </div>
    </div>"""

    # Collect all entities by type
    bible_types = ["character", "location", "faction", "item"]
    all_entities: Dict[str, List[Dict[str, Any]]] = {}
    total_count = 0

    for etype in bible_types:
        entity_list = list_entities_of_type(etype)
        loaded = []
        for e in entity_list:
            data = load_entity(etype, e["id"])
            if data:
                loaded.append(data)
        all_entities[etype] = loaded
        total_count += len(loaded)

    if total_count == 0:
        raise HTTPException(status_code=404, detail="No entities found in project")

    # Table of contents
    toc = '<div class="toc"><h2>Table of Contents</h2>'
    for etype in bible_types:
        entities = all_entities.get(etype, [])
        if not entities:
            continue
        toc += f'<div class="toc-section"><div class="toc-section-title">{etype.title()}s ({len(entities)})</div>'
        for edata in entities:
            name = get_entity_name(etype, edata["frontmatter"], edata["entity_id"])
            toc += f"""
            <div class="toc-entry">
                <a href="#entity-{etype}-{edata['entity_id']}">{name}</a>
            </div>"""
        toc += "</div>"
    toc += "</div>"

    # Render each category
    body_parts = [cover, toc]
    for etype in bible_types:
        entities = all_entities.get(etype, [])
        if not entities:
            continue

        body_parts.append(f"""
        <div class="category-header">
            <h2>{etype.title()}s</h2>
        </div>""")

        renderer = TEMPLATE_RENDERERS.get(select_template(etype), render_generic_sheet)
        for i, edata in enumerate(entities):
            name = get_entity_name(etype, edata["frontmatter"], edata["entity_id"])
            separator = ' class="entity-separator"' if i > 0 else ""
            entity_html = f'<div id="entity-{etype}-{edata["entity_id"]}"{separator}>'
            entity_html += render_entity_header(etype, edata["entity_id"], name, settings)
            entity_html += renderer(edata, settings)
            entity_html += "</div>"
            body_parts.append(entity_html)

    full_html = wrap_full_html("World Bible", "\n".join(body_parts), settings)
    return HTMLResponse(content=full_html)
