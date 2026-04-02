# StudioBrain Templates SDK

> Entity templates, generation rules, and plugin system for StudioBrain.

## Overview

This repository contains the schema definitions that power StudioBrain's dynamic entity system:

- **Templates**: YAML+Markdown entity type definitions (Character, Location, Brand, etc.)
- **Maps**: Map/level templates (3D Level, Dungeon Grid, Location Scout)
- **Documents**: Document templates (Style Bible, Lore, etc.)
- **Rules**: AI generation rules that guide content creation
- **Plugins**: Plugin system with 22+ plugins for extended functionality
- **Schemas**: JSON Schema definitions for entity frontmatter validation
- **Skills**: Agent skill definitions

## Structure

```
├── _TEMPLATES/             # Entity type definitions
│   ├── Standard/           # Core entity templates
│   │   ├── CHARACTER_TEMPLATE.md
│   │   ├── LOCATION_TEMPLATE.md
│   │   ├── BRAND_TEMPLATE.md
│   │   └── ...
│   ├── Core/               # Core templates (Assembly, Dialogue, Quest, Timeline)
│   ├── Layouts/            # UI layout definitions
│   ├── Packs/              # Bundled template sets
│   ├── Custom/             # User-created templates
│   └── ExampleImplementation/
├── _MAPS/                  # Map templates
│   ├── 3D_Level_MAP_TEMPLATE.md
│   ├── Dungeon_Grid_MAP_TEMPLATE.md
│   └── Location_Scout_MAP_TEMPLATE.md
├── _DOCUMENTS/             # Document templates
│   └── STYLE_BIBLE_TEMPLATE.md
├── _RULES/                 # AI generation rules
│   ├── Standard/           # Core rules + rule files
│   │   ├── RULES_INDEX.md
│   │   ├── CHARACTER_RULES.md
│   │   ├── LOCATION_RULES.md
│   │   └── ...
│   ├── Custom/             # User-customized rules
│   └── User/               # Per-user rule overrides
├── _PLUGINS/               # Plugin system
│   ├── _plugins.json       # Plugin registry
│   ├── hello-world/        # Example plugin
│   ├── jira-sync/
│   ├── comfyui-workflows/
│   └── ...
├── _SCHEMAS/               # JSON Schema definitions
│   ├── character.json
│   ├── location.json
│   └── ...
└── _SKILLS/                # Agent skill definitions
```

## Usage

Templates are consumed by StudioBrain's type generation system:

1. Templates define entity fields via YAML frontmatter
2. Backend generates TypeScript types + Zod schemas automatically
3. Frontend renders dynamic UIs based on template structure

## Adding a New Entity Type

1. Create `_TEMPLATES/Standard/MYTYPE_TEMPLATE.md`
2. Define YAML frontmatter with fields
3. Types auto-generate on next build

## Related Repositories

| Repo | Description |
|------|-------------|
| [studiobrain-app](https://github.com/BiloxiStudios/studiobrain-app) | Web application |
| [studiobrain-ai](https://github.com/BiloxiStudios/studiobrain-ai) | AI service |
| [studiobrain-desktop](https://github.com/BiloxiStudios/studiobrain-desktop) | Desktop + mobile apps |

## License

Private. Copyright (c) 2024-2026 Biloxi Studios Inc.
