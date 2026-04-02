---
title: "StudioBrain Entity JSON Schemas"
description: "JSON Schema definitions for all StudioBrain entity types, used by the entity-validator plugin to validate YAML frontmatter before write."
category: "schemas"
version: "1.0"
created_date: "2026-04-01"
last_updated: "2026-04-01"
---

# StudioBrain Entity JSON Schemas

JSON Schema (Draft 2020-12) definitions for all StudioBrain entity types.
These schemas are the **single source of truth** for what constitutes valid YAML
frontmatter on an entity markdown file.

## How Schemas are Used

```
Import / Upload / Edit
        ↓
entity-validator plugin (backend/routes.py)
        ↓  loads schema from schemas/<entity_type>.json
validate frontmatter dict against JSON Schema
        ↓
  VALID → store entity            INVALID → HTTP 422 + field errors
```

The `entity-validator` plugin exposes:

| Endpoint | Method | Description |
|---|---|---|
| `/api/plugins/entity-validator/validate` | POST | Validate a frontmatter dict |
| `/api/plugins/entity-validator/validate/markdown` | POST | Parse + validate raw markdown |
| `/api/plugins/entity-validator/schemas` | GET | List available schemas |
| `/api/plugins/entity-validator/schemas/{entity_type}` | GET | Fetch a specific schema |

## Schema Files

| File | Entity Type | template_category |
|---|---|---|
| `_base.json` | *(shared fields)* | — |
| `character.json` | `character` | `entity` |
| `location.json` | `location` | `entity` |
| `item.json` | `item` | `entity` |
| `faction.json` | `faction` | `entity` |
| `brand.json` | `brand` | `entity` |
| `district.json` | `district` | `entity` |
| `job.json` | `job` | `entity` |
| `quest.json` | `quest` | `entity` |
| `event.json` | `event` | `entity` |
| `campaign.json` | `campaign` | `entity` |
| `assembly.json` | `assembly` | `entity` |
| `dialogue.json` | `dialogue` | `entity` |
| `timeline.json` | `timeline` | `entity` |
| `universe.json` | `universe` | `document` |
| `style_bible.json` | `style_bible` | `document` |

## Required Fields (all entities)

| Field | Type | Constraint |
|---|---|---|
| `id` | string | `^[a-z0-9][a-z0-9_]*$` |
| `entity_type` | string | enum of known entity types |
| `template_version` | string | `^\d+\.\d+$` |
| `template_category` | string | `entity`, `document`, or `core` |
| `created_date` | string | `^\d{4}-\d{2}-\d{2}$` |
| `last_updated` | string | `^\d{4}-\d{2}-\d{2}$` |

## Item-Specific Required Fields

| Field | Type | Constraint |
|---|---|---|
| `item_type` | string | `weapon`, `consumable`, `key_item`, `material`, `collectible`, `cosmetic`, `currency` |

## Adding a New Entity Type

1. Add a new `<entity_type>.json` file in this directory following the same `allOf` + `$ref` pattern.
2. Add the `entity_type` to the `enum` in `_base.json`.
3. Add the new entity type to the `ENTITY_SCHEMAS` map in `plugins/entity-validator/backend/routes.py`.
4. Add the corresponding template in `templates/Standard/` and rules file in `rules/`.
