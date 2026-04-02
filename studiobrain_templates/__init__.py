"""StudioBrain Templates — pip-installable data package.

Provides filesystem paths to bundled template, rule, plugin, and schema
files so that the StudioBrain backend can discover them at runtime without
relying on ephemeral container filesystem copies.

Usage::

    from studiobrain_templates import TEMPLATES_DIR, RULES_DIR, PLUGINS_DIR, SCHEMAS_DIR

    # Iterate Standard templates
    for md in (TEMPLATES_DIR / "Standard").glob("*_TEMPLATE.md"):
        ...
"""

from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent

TEMPLATES_DIR: Path = _PKG_ROOT / "templates"
"""Path to the ``templates/`` tree (Standard, Core, Custom, Packs, …)."""

RULES_DIR: Path = _PKG_ROOT / "rules"
"""Path to the ``rules/`` tree."""

PLUGINS_DIR: Path = _PKG_ROOT / "plugins"
"""Path to the ``plugins/`` tree."""

SCHEMAS_DIR: Path = _PKG_ROOT / "schemas"
"""Path to the ``schemas/`` tree (JSON Schema for entity frontmatter)."""

__all__ = ["TEMPLATES_DIR", "RULES_DIR", "PLUGINS_DIR", "SCHEMAS_DIR"]
