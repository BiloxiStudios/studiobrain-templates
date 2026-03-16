# CLAUDE.md -- studiobrain-templates

## Project Overview

Entity templates, AI generation rules, and plugin SDK for StudioBrain. Pure data repository -- Markdown files with YAML frontmatter define the 17+ entity types, generation constraints, and plugin manifests. No backend code, no frontend code. Licensed under Apache 2.0 (will be public).

**Owner:** Biloxi Studios Inc.
**JIRA:** SBAI (biloxistudios.atlassian.net)
**GitHub:** BiloxiStudios/studiobrain-templates

## Architecture

```
studiobrain-templates/
├── templates/
│   ├── Standard/                       # 14 entity templates (CHARACTER, LOCATION, ITEM, etc.)
│   ├── Core/                           # Core templates (ASSEMBLY, DIALOGUE, QUEST, TIMELINE)
│   ├── Custom/                         # User-created templates (.gitkeep)
│   ├── Layouts/                        # UI layout definitions (JSON)
│   ├── Packs/                          # Template packs (starter-characters, starter-locations, etc.)
│   └── ExampleImplementation/          # Example entities using the templates
├── rules/
│   ├── *.md                            # 17 rule files (CHARACTER_RULES, LOCATION_RULES, etc.)
│   ├── Core/                           # Core rules (assembly_constraints.yaml, dialogue_flow.yaml)
│   ├── Standard/                       # Standard rules (character_consistency, style_guide, world_lore)
│   ├── Custom/                         # User-created rules (.gitkeep)
│   └── User/                           # Per-user rule overrides (.gitkeep)
├── plugins/                            # 22 plugin definitions
│   ├── _plugins.json                   # Plugin registry
│   ├── _plugin_settings.json           # Default settings
│   ├── _shared/plugin-theme.css        # Shared plugin CSS
│   └── <plugin-name>/                  # Each plugin: plugin.json + backend/ + frontend/
├── package.json                        # @studiobrain/templates (npm package)
├── LICENSE                             # Apache 2.0
└── .github/workflows/ci.yml           # YAML frontmatter validation
```

## Development

```bash
# Validate all templates and rules (CI runs this)
pip install pyyaml
python3 scripts/validate.py             # If scripts/ exists, or inline validation

# Manual validation: every .md file in templates/ and rules/ must have valid YAML frontmatter
```

There is no build step. This is a data-only package consumed by the StudioBrain backend at runtime.

## Git Workflow

1. Branch from `main` (e.g., `SBAI-123-feature-name`)
2. Every commit references a JIRA ticket (`SBAI-XXX`)
3. Open PR against `main`; CI validates YAML frontmatter in all templates and rules
4. Merge to `main` publishes the package

## Key Rules

- **NO backend code, NO frontend code.** This repo is pure data (Markdown, YAML, JSON, HTML for plugin UIs). Do not add Python or TypeScript application logic.
- **Every template and rule file must have valid YAML frontmatter.** Files start with `---`, contain a YAML mapping, and close with `---`. CI enforces this.
- **Apache 2.0 license.** This repo will be public. Do not add proprietary code or credentials.
- **Plugins are self-contained.** Each plugin directory has `plugin.json` (manifest), optional `backend/` (routes.py, events.py), and `frontend/` (HTML pages/panels). Plugin backends run inside the StudioBrain backend process.
- **Do not modify `_plugins.json` or `_plugin_settings.json` without updating the corresponding plugin directories.**
- **Template packs** in `templates/Packs/` must include a `pack.json` manifest with metadata.
- When adding a new entity type, add both the template file (in `templates/Standard/`) and a corresponding rules file (in `rules/`).
