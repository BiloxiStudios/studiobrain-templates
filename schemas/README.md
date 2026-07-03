---
title: "StudioBrain JSON Schemas"
description: "JSON Schema definitions for entity frontmatter, layouts, template packs, plugins, skills, and shared compat metadata."
category: "schemas"
version: "1.1"
created_date: "2026-04-01"
last_updated: "2026-07-03"
---

# StudioBrain JSON Schemas

JSON Schema (Draft 2020-12) definitions for every StudioBrain asset type that
has a structured shape. These schemas are the **single source of truth** for
what constitutes valid frontmatter / manifest content. Third-party authors
should treat them as a contract: anything that validates against the schema
will load in StudioBrain.

## Schema family overview

| File | Validates | Used by |
|---|---|---|
| `_base.json` | Shared YAML frontmatter fields required by every entity | entity-validator plugin, backend write paths |
| `<entity_type>.json` | YAML frontmatter for a single entity type (character, location, item, faction, brand, district, job, quest, event, campaign, assembly, dialogue, timeline, universe, style_bible, biome) | entity-validator plugin |
| `_compat.json` | Shared compat metadata object (semver core version requirements) | Referenced by every asset-level schema below |
| `layout.json` | `templates/Layouts/*.layout.json` — UI layout files | frontend entity editor |
| `pack.json` | `templates/Packs/<id>/pack.json` — template pack manifests | pack installer, marketplace |
| `plugin.json` | `plugins/<id>/plugin.json` — plugin manifests (full / frontend-only / protocol-adapter variants) | plugin loader |
| `skill.yaml.json` | `skills/Standard/*.yaml` and `skills/User/*.yaml` — AI skill frontmatter (parsed YAML mapping) | skill picker |

## How schemas are used

```
Import / Upload / Edit / Install
        ↓
scripts/validate.py (CI + install-time)
        ↓ loads schemas/<name>.json via $ref-aware registry
validate parsed instance against JSON Schema
        ↓
  VALID → store / install asset        INVALID → reject with field errors
```

The validator (`scripts/validate.py`) is the canonical entry point for both
local development and CI. It accepts several flags:

| Flag | Purpose |
|---|---|
| `--core-version X.Y.Z` | Run the semver compat check: refuse any asset whose `compat.min_core_version` is newer than the running core. |
| `--allow-missing-compat` | Don't error on assets that lack `compat.min_core_version`. Used during the migration period; see SBAI-4649. |
| `--no-entity-yaml` | Skip entity markdown frontmatter validation (faster local pass). |
| `--no-compat` | Skip compat enforcement entirely. |

Typical local invocation:

    python3 scripts/validate.py --allow-missing-compat
    python3 scripts/validate.py --core-version 0.3.0

CI runs:

    python3 scripts/validate.py --allow-missing-compat

## Compatibility metadata (`compat` object)

Every layout, pack, plugin, and skill SHOULD declare a top-level `compat`
object telling StudioBrain which core version it requires. The shape is
defined by `schemas/_compat.json` and shared via `$ref` so it is identical
across all four asset types:

```json
"compat": {
  "min_core_version": "0.3.0",
  "max_core_version": null,
  "target_api_version": "layout/v1",
  "tested_core_versions": ["0.3.0"]
}
```

| Field | Type | Meaning |
|---|---|---|
| `min_core_version` | semver string (required) | Minimum core version that can run this asset. |
| `max_core_version` | semver string or null | Maximum core version (inclusive) known to work; null means unbounded. |
| `target_api_version` | `<surface>/v<N>` or null | Optional API/protocol version this asset targets (e.g. `plugin-manifest/v2`, `layout/v1`). |
| `tested_core_versions` | array of semver strings | Informational; versions the author actually tested. |

**Semver ordering.** Comparison uses the release triple only — pre-release
suffixes (`-rc.1`) and build metadata (`+build.42`) are stripped before
ordering. So `1.0.0-rc.1` is treated as `1.0.0` for compat purposes.

**Why required, not optional.** A missing `min_core_version` means the
installer cannot protect the user from installing an asset that won't load.
Strict mode (validator default) treats absence as an error. CI runs in
migration mode (`--allow-missing-compat`) until SBAI-4649 backfills every
existing asset.

## Plugin variants (`type` discriminator)

StudioBrain plugins come in three flavors, distinguished by the top-level
`type` field:

| `type` | What it is | Required keys |
|---|---|---|
| `full` | In-process Python plugin with backend routes/event_handlers and frontend pages/panels | `capabilities` |
| `frontend-only` | No backend routes; uses the generic `plugin_data_routes` for storage | `capabilities.frontend` |
| `protocol-adapter` | WASM module bridging an external service (e.g. ltx-video); implements `adapt_request`, `adapt_response`, `health_check` | `exports`, `service_type` |

The `plugin.json` schema uses `allOf` with `if/then` branches to enforce
the right shape per variant.

## Plugin settings schema (`settings_schema`)

A plugin's `settings_schema` is a free-form object whose keys are setting
ids and values describe the field. Allowed `type` values:

| `type` | Rendered widget | Notes |
|---|---|---|
| `string` | text input | |
| `boolean` | toggle | |
| `integer` / `number` | numeric input | supports `min`/`max`/`step` |
| `select` | dropdown | requires `options` array |
| `color` | color picker | |
| `secret` | masked input | stored separately; use for API keys/tokens |
| `object` | nested fields | use `properties` for sub-shape |

`options` items may be either a plain string (`"markdown"`) or a
`{value, label}` object — both shapes appear in the wild.

## Adding a new entity type

1. Add a new `<entity_type>.json` file in this directory following the same
   `allOf` + `$ref` pattern as `character.json`.
2. Add the `entity_type` to the `enum` in `_base.json`.
3. Add the new entity type to the `ENTITY_SCHEMAS` map in
   `plugins/entity-validator/backend/routes.py`.
4. Add the corresponding template in `templates/Standard/` and rules file in
   `rules/`.
5. If the entity needs a UI layout, add `templates/Layouts/<entity_type>.layout.json`
   (validated against `layout.json`).

## Adding a new schema

1. Pick a kebab-or-snake-case file name (existing convention: `<noun>.json`
   for JSON files, `<noun>.yaml.json` for schemas that validate parsed YAML).
2. Set `$schema` to `https://json-schema.org/draft/2020-12/schema` and
   `$id` to `https://studiobrain.biloxistudios.com/schemas/<filename>`.
3. If the asset has compat requirements, add a `"compat": {"$ref": "./_compat.json"}`
   property and require it.
4. Update this README's "Schema family overview" table.
5. Add a check function in `scripts/validate.py` and wire it into `main()`.

## Schema files

| File | Description |
|---|---|
| `_base.json` | Shared entity frontmatter fields |
| `_compat.json` | Shared compat metadata (min_core_version semver) |
| `character.json` | Character entity schema |
| `location.json` | Location entity schema |
| `item.json` | Item entity schema |
| `faction.json` | Faction entity schema |
| `brand.json` | Brand entity schema |
| `district.json` | District entity schema |
| `job.json` | Job entity schema |
| `quest.json` | Quest entity schema |
| `event.json` | Event entity schema |
| `campaign.json` | Campaign entity schema |
| `assembly.json` | Assembly entity schema |
| `dialogue.json` | Dialogue entity schema |
| `timeline.json` | Timeline entity schema |
| `universe.json` | Universe document schema |
| `style_bible.json` | Style bible document schema |
| `biome.json` | Biome entity schema |
| `layout.json` | UI layout contract (templates/Layouts/*.layout.json) |
| `pack.json` | Template pack contract (templates/Packs/<id>/pack.json) |
| `plugin.json` | Plugin manifest contract (full / frontend-only / protocol-adapter) |
| `skill.yaml.json` | AI skill frontmatter contract (skills/*.yaml) |
