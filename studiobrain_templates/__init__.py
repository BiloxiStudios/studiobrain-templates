"""StudioBrain Templates — pip-installable data package.

Provides filesystem paths to bundled template, rule, plugin, schema, map,
document, and skill files so that the StudioBrain backend can discover them
at runtime without relying on ephemeral container filesystem copies.

Usage::

    from studiobrain_templates import (
        TEMPLATES_DIR, RULES_DIR, PLUGINS_DIR, SCHEMAS_DIR,
        MAPS_DIR, DOCUMENTS_DIR, SKILLS_DIR,
    )

    # Iterate Standard templates
    for md in (TEMPLATES_DIR / "Standard").glob("*_TEMPLATE.md"):
        ...
"""

from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent

TEMPLATES_DIR: Path = _PKG_ROOT / "_TEMPLATES"
"""Path to the ``_TEMPLATES/`` tree (Standard, Core, Custom, Packs, …)."""

RULES_DIR: Path = _PKG_ROOT / "_RULES"
"""Path to the ``_RULES/`` tree (Standard, Custom, User)."""

PLUGINS_DIR: Path = _PKG_ROOT / "_PLUGINS"
"""Path to the ``_PLUGINS/`` tree."""

SCHEMAS_DIR: Path = _PKG_ROOT / "_SCHEMAS"
"""Path to the ``_SCHEMAS/`` tree (JSON Schema for entity frontmatter)."""

MAPS_DIR: Path = _PKG_ROOT / "_MAPS"
"""Path to the ``_MAPS/`` tree (3D Level, Dungeon Grid, Location Scout, …)."""

DOCUMENTS_DIR: Path = _PKG_ROOT / "_DOCUMENTS"
"""Path to the ``_DOCUMENTS/`` tree (Style Bible, Lore, …)."""

SKILLS_DIR: Path = _PKG_ROOT / "_SKILLS"
"""Path to the ``_SKILLS/`` tree (agent skill definitions)."""

__all__ = [
    "TEMPLATES_DIR",
    "RULES_DIR",
    "PLUGINS_DIR",
    "SCHEMAS_DIR",
    "MAPS_DIR",
    "DOCUMENTS_DIR",
    "SKILLS_DIR",
]
