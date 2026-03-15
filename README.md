# StudioBrain Templates SDK

> Entity templates, generation rules, and plugin system for StudioBrain.

## Overview

This repository contains the schema definitions that power StudioBrain's dynamic entity system:

- **Templates**: YAML+Markdown entity type definitions (Character, Location, Brand, etc.)
- **Rules**: AI generation rules that guide content creation
- **Plugins**: Plugin system with 22+ plugins for extended functionality

## Structure

```
├── templates/              # Entity type definitions
│   ├── Standard/           # Core templates
│   │   ├── CHARACTER_TEMPLATE.md
│   │   ├── LOCATION_TEMPLATE.md
│   │   ├── BRAND_TEMPLATE.md
│   │   └── ...
│   ├── Layouts/            # UI layout definitions
│   └── ExampleImplementation/
├── rules/                  # AI generation rules
│   ├── RULES_INDEX.md
│   ├── CHARACTER_RULES.md
│   ├── LOCATION_RULES.md
│   └── ...
└── plugins/                # Plugin system
    ├── _plugins.json       # Plugin registry
    ├── hello-world/        # Example plugin
    ├── jira-sync/
    ├── comfyui-workflows/
    └── ...
```

## Usage

Templates are consumed by StudioBrain's type generation system:

1. Templates define entity fields via YAML frontmatter
2. Backend generates TypeScript types + Zod schemas automatically
3. Frontend renders dynamic UIs based on template structure

## Adding a New Entity Type

1. Create `templates/Standard/MYTYPE_TEMPLATE.md`
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
