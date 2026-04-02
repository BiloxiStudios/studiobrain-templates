"""StudioBrain Templates — pip-installable data package.

Provides filesystem paths to bundled template, rule, plugin, schema,
map, document, and skill files so that the StudioBrain backend can
discover them at runtime.

Usage::

    from studiobrain_templates import TEMPLATES_DIR, MAPS_DIR, DOCUMENTS_DIR

    for md in (TEMPLATES_DIR / "Standard").glob("*_TEMPLATE.md"):
        ...
    for md in MAPS_DIR.glob("*_MAP_TEMPLATE.md"):
        ...
"""

from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent

TEMPLATES_DIR: Path = _PKG_ROOT / "templates"
"""Path to the ``templates/`` tree (Standard, Core, Custom, Packs, ...)."""

MAPS_DIR: Path = _PKG_ROOT / "maps"
"""Path to the ``maps/`` tree (map templates: dungeon, world, geographic, etc.)."""

DOCUMENTS_DIR: Path = _PKG_ROOT / "documents"
"""Path to the ``documents/`` tree (document templates: style bible, GDD, etc.)."""

SKILLS_DIR: Path = _PKG_ROOT / "skills"
"""Path to the ``skills/`` tree (agent skill definitions)."""

RULES_DIR: Path = _PKG_ROOT / "rules"
"""Path to the ``rules/`` tree."""

PLUGINS_DIR: Path = _PKG_ROOT / "plugins"
"""Path to the ``plugins/`` tree."""

SCHEMAS_DIR: Path = _PKG_ROOT / "schemas"
"""Path to the ``schemas/`` tree (JSON Schema for entity frontmatter)."""

__all__ = [
    "TEMPLATES_DIR", "MAPS_DIR", "DOCUMENTS_DIR", "SKILLS_DIR",
    "RULES_DIR", "PLUGINS_DIR", "SCHEMAS_DIR",
]
