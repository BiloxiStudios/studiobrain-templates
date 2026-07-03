"""StudioBrain Templates — pip-installable data package.

Provides filesystem paths to bundled templates, rules, plugins, schemas,
skills, and layouts so that the StudioBrain backend can discover them at runtime.

All content types live under templates/ with subdirectories:
  Standard/           — core entity templates
  Standard/Documents/ — document templates (template_category: document)
  Standard/Maps/      — map templates (template_category: map)
  Core/               — core tool templates (assembly, dialogue, etc.)
  Custom/             — user overrides (not in this repo)
  Packs/              — installable template packs
  Layouts/            — UI layout definitions (JSON)

Usage::

    from studiobrain_templates import TEMPLATES_DIR, RULES_DIR, PLUGINS_DIR

    for md in TEMPLATES_DIR.rglob("*_TEMPLATE.md"):
        ...
"""

from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent

TEMPLATES_DIR: Path = _PKG_ROOT / "templates"
"""Path to the ``templates/`` tree (Standard, Core, Custom, Packs, Layouts, ...)."""

RULES_DIR: Path = _PKG_ROOT / "rules"
"""Path to the ``rules/`` tree."""

PLUGINS_DIR: Path = _PKG_ROOT / "plugins"
"""Path to the ``plugins/`` tree."""

SCHEMAS_DIR: Path = _PKG_ROOT / "schemas"
"""Path to the ``schemas/`` tree (JSON Schema for entity frontmatter validation,
layout/pack/plugin/skill contracts, and compat metadata)."""

SKILLS_DIR: Path = _PKG_ROOT / "skills"
"""Path to the ``skills/`` tree (AI skill YAML definitions with frontmatter
validated against schemas/skill.yaml.json)."""

LAYOUTS_DIR: Path = TEMPLATES_DIR / "Layouts"
"""Path to the ``templates/Layouts/`` tree (UI layout JSON, validated against
schemas/layout.json)."""

PACKS_DIR: Path = TEMPLATES_DIR / "Packs"
"""Path to the ``templates/Packs/`` tree (template pack manifests, validated
against schemas/pack.json)."""

__all__ = [
    "TEMPLATES_DIR",
    "RULES_DIR",
    "PLUGINS_DIR",
    "SCHEMAS_DIR",
    "SKILLS_DIR",
    "LAYOUTS_DIR",
    "PACKS_DIR",
]
