---
title: "StudioBrain JSON Schemas"
description: "JSON Schema definitions for entity frontmatter, layouts, template packs, plugins, skills, and shared compat metadata."
category: "schemas"
version: "2.0"
created_date: "2026-04-01"
last_updated: "2026-08-17"
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
| `--fixtures` | Validate fixture files in `schemas/fixtures/` (valid_* should pass, invalid_* should fail). |

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
| `full` | In-process Python plugin with backend routes/event_handlers and frontend pages/panels | `capabilities` (v1) or `surfaces` (v2) |
| `frontend-only` | No backend routes; uses the generic `plugin_data_routes` for storage | `capabilities.frontend` (v1) or `surfaces` (v2) |
| `protocol-adapter` | WASM module bridging an external service (e.g. ltx-video); implements `adapt_request`, `adapt_response`, `health_check` | `exports`, `service_type` |

The `plugin.json` schema uses `allOf` with `if/then` branches to enforce
the right shape per variant, plus a `manifest_version` field to distinguish
v1 (legacy capabilities-based) from v2 (explicit surfaces-based) manifests.

## Plugin Manifest v2 Contract (SBAI-7182)

The v2 manifest contract introduces explicit per-surface metadata. Key changes:

### `manifest_version` field

```json
{
  "manifest_version": 2,
  "compat": {
    "target_api_version": "plugin-manifest/v2"
  }
}
```

| Value | Meaning |
|---|---|
| `1` (or omitted) | Legacy v1 manifest using `capabilities` object |
| `2` | V2 manifest with explicit `surfaces` array |

### `surfaces` array (v2 only)

Replaces the nested `capabilities.frontend.pages/panels` with a flat, typed array:

```json
"surfaces": [
  {
    "type": "page",
    "id": "dashboard",
    "label": "Plugin Dashboard",
    "artifact": {"path": "frontend/pages/dashboard.html"},
    "placement": {
      "location": "plugins-nav",
      "section": "plugins",
      "order": 1,
      "icon": "layout-dashboard"
    },
    "capabilities": ["entity:read", "settings:own"],
    "permissions": ["entity:read", "settings:read"]
  },
  {
    "type": "panel",
    "id": "entity-notes",
    "label": "Entity Notes",
    "artifact": {"path": "frontend/panels/notes.html"},
    "placement": {
      "location": "entity-sidebar",
      "section": "annotations",
      "order": 10,
      "icon": "sticky-note",
      "visibility": "entity-selected"
    },
    "capabilities": ["entity:read", "entity:write:notes"],
    "context": {
      "entity_types": ["character", "location"],
      "requires_selection": true,
      "min_selection_count": 1
    }
  },
  {
    "type": "command",
    "id": "bulk-tag",
    "label": "Bulk Tag Entities",
    "artifact": {"path": "frontend/commands/bulk-tag.js", "type": "module"},
    "placement": {"location": "command-palette"},
    "context": {"requires_selection": true, "max_selection_count": 100}
  },
  {
    "type": "settings",
    "id": "plugin-config",
    "label": "Configuration",
    "artifact": {"path": "frontend/settings/config.html"},
    "placement": {"location": "settings-panel"}
  },
  {
    "type": "widget",
    "id": "quick-stats",
    "label": "Quick Stats",
    "artifact": {"path": "frontend/widgets/quick-stats.html"},
    "placement": {"location": "dashboard-main"}
  }
]
```

### Surface types

| Type | Description | Placement locations |
|---|---|---|
| `page` | Full-page dashboard mounted in nav | `plugins-nav`, custom sections |
| `panel` | Embedded widget in entity view | `entity-sidebar`, `entity-tab`, `dashboard-sidebar`, `page-toolbar` |
| `command` | Command-palette action | `command-palette` |
| `settings` | Settings panel | `settings-panel` |
| `widget` | Dashboard widget | `dashboard-main`, `dashboard-sidebar` |

### Per-surface metadata

Each surface declares:

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | Surface type (see above) |
| `id` | string | yes | Unique ID within plugin (snake_case/kebab-case) |
| `label` | string | yes | Human-readable label |
| `description` | string | no | What this surface does |
| `artifact.path` | string | yes | Relative path to HTML/JS file |
| `artifact.type` | string | no | `"html"` (default) or `"module"` |
| `artifact.entry_point` | string | no | JS export name (default: `"default"`) |
| `placement.location` | string | yes | Where it mounts |
| `placement.section` | string | no | Section within location |
| `placement.order` | integer | no | Sort order (lower = first) |
| `placement.icon` | string | no | Icon identifier |
| `placement.visibility` | string | no | `"always"`, `"entity-selected"`, `"has-permission"`, `"has-setting"` |
| `capabilities[]` | string[] | yes | Explicit granular capabilities (e.g. `entity:read:character`); use `[]` when none are required |
| `permissions[]` | string[] | yes | Explicit permission grants; use `[]` when none are required |
| `context.entity_types[]` | string[] | no | Entity types supported |
| `context.requires_selection` | boolean | no | Requires active selection |
| `context.min_selection_count` | integer | no | Minimum selected items |
| `context.max_selection_count` | integer | no | Maximum selected items |

### V2 routes and event handlers (alternative to `capabilities.backend`)

V2 supports explicit route/event handler declarations:

```json
"routes": [
  {"method": "GET", "path": "/stats", "handler": "backend/routes.py:get_stats", "permissions": ["analytics:read"]},
  {"method": "POST", "path": "/tags/bulk", "handler": "backend/routes.py:bulk_tag_entities"}
],
"event_handlers": [
  {"event": "entity.created", "handler": "backend/events.py:on_entity_created", "entity_types": ["character", "location"]},
  {"event": "entity.updated", "handler": "backend/events.py:on_entity_updated"}
]
```

### Backwards compatibility (v1 → v2 migration)

**V1 manifests remain valid** with `manifest_version: 1` (explicit or implicit). Migration to v2 is optional but recommended for new plugins.

To migrate v1 → v2:
1. Add `"manifest_version": 2`
2. Convert `capabilities.frontend.pages[]` → `surfaces[]` with `type: "page"`
3. Convert `capabilities.frontend.panels[]` → `surfaces[]` with `type: "panel"`
4. Move `capabilities.backend.routes` → `routes[]` (or keep under `capabilities.backend`)
5. Add `target_api_version: "plugin-manifest/v2"` to `compat`

See `schemas/fixtures/` for example v1 and v2 manifests.

## Plugin v2 build + publish pipeline (SBAI-7183)

`manifest_version: 2` plugins are built, smoke-tested, and published to R2 by
CI (`.github/workflows/ci.yml`), per the publish design in
`PLUGIN-ARCHITECTURE-DESIGN.md` Q3. v1 (legacy `capabilities`) manifests are
excluded from this pipeline — they stay archived and unsupported (SBAI-6815).

Three-job pipeline, split for one reason: security.

| Job | Trigger | Secrets | What it does |
|---|---|---|---|
| `check-plugin-ci-security` | push + pull_request (incl. forks) | none | Statically proves no pull_request-reachable job in this workflow can read a publish/signing secret (`scripts/check_workflow_secret_isolation.py`), round-trip-tests the index signing scheme with a throwaway keypair (`scripts/verify_index_signature.py --selftest`), and runs the unit test suite (`scripts/tests/`). |
| `build-smoke-plugins` | push + pull_request (incl. forks) | none | Validates every v2 manifest, resolves and smoke-tests every declared surface artifact, stages a publish-ready tree + checksummed index under `dist/` (`scripts/build_plugin_artifacts.py`). Uploaded as a build artifact for inspection on every PR. |
| `publish-plugins-to-r2` | push to `main` only | R2 + signing creds | Rebuilds `dist/` fresh from the merged commit, signs the index (`scripts/sign_index.py`), uploads immutable versioned objects to R2 plus the signed index (`scripts/publish_to_r2.py`), and commits the signed index back to the repo root. |

Because the first two jobs need zero secrets, running arbitrary plugin code
(HTML/JS surface artifacts) from a pull request through validate → build →
smoke is safe even for forked contributors. `check-plugin-ci-security` is
itself a live enforcement gate, not just documentation — it fails any PR
that tries to widen secret access into a pull_request-reachable job.

**R2 key layout** (bucket `sb-content`, per the sb-cf 2026-08-16 ruling —
one shared bucket, kind-prefixed keys):

```
plugins/<id>/<version>/plugin.json
plugins/<id>/<version>/<artifact paths as declared in surfaces[].artifact.path>
plugins/_plugins.index.json      # always the latest signed index (mutable)
```

**Immutability**: once `plugins/<id>/<version>/...` is published, its
content can never change — `publish_to_r2.py` HEADs every object first and
hard-fails the publish job if a re-run would overwrite an existing object
with different bytes. Bump the plugin's `version` instead. Re-running on the
same commit is safe (identical content is skipped, not re-uploaded).

**Reproducibility & idempotent reruns** (manager review, SBAI-7183): the
entire signed index is a deterministic function of the commit —
`generated_at` comes from the commit's author timestamp (`--built-at`) and
`signature.signed_at` pins to that same `generated_at` (never wall-clock),
so building and signing the same commit twice yields byte-identical
`_plugins.index.json`. The publish job's commit-back step commits from the
current tip of `origin/main` (not the run's checkout), so a rerun of an
unchanged commit finds its identical index already on main and no-ops
instead of non-fast-forward-failing the push.

**Index signing is a separate trust domain from per-plugin trust tiers.**
The signature on `_plugins.index.json` (Ed25519, `scripts/sign_index.py`,
public keys in `schemas/keys/plugin-index-trusted-keys.json`) proves *this
index was produced by trusted CI* — it says nothing about whether any
individual plugin inside it is Biloxi-vetted. Per-plugin `first_party` /
`trusted_vendor` / `partner` signatures (SBAI-4630, verified in core's
`plugin_signature.rs`) are a completely different key, signed by the
commercial `sb-plugin-sign` tool from a key in Azure Key Vault — that
private key must never be reachable from this public repo's CI, and this
pipeline never touches it.

**Prerequisites for `publish-plugins-to-r2`** (provisioned 2026-08-19,
SBAI-7183/SBAI-7505 — the `sb-content` bucket is a fresh, dedicated bucket
distinct from the unrelated `sb-cf-pivot-assets` bucket the cloud Worker
already uses for other content; studiobrain-cloud's `CONTENT_ARTIFACTS`
binding, SBAI-6854, should point at this same `sb-content` bucket when it's
wired up so both sides read/write the same plugin objects):
- R2 bucket `sb-content`, public read enabled via the managed `r2.dev`
  domain (plugin artifacts and the index are meant to be fetched directly by
  desktop/mobile/cloud clients — see Q3 "Browse"/"Install").
- Environment secrets on the `plugins-publish` GitHub Environment (branch
  policy restricted to `main`): `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` (a
  bucket-scoped Cloudflare API token, read+write on `sb-content` only — no
  other bucket, no account-wide R2), `R2_SECRET_ACCESS_KEY` (SHA-256 of that
  token, per Cloudflare's S3-compat derivation), `R2_BUCKET=sb-content`.
  Credentials in Vaultwarden "Cloudflare R2 — sb-content bucket (SBAI-7183/7505
  templates plugin publish)".
- Repo variable (not a secret — it's a public read-only URL)
  `R2_PUBLIC_BASE_URL`, passed to `build_plugin_artifacts.py --public-base-url`
  so every artifact in the index gets a full, directly-fetchable `url` in
  addition to its `r2_key`. Currently the bucket's `r2.dev` domain; may move
  to a custom domain (e.g. matching `releases.studiobrain.ai`'s pattern)
  without changing the index shape — only the variable's value changes.
- `PLUGIN_INDEX_SIGNING_KEY` (Vaultwarden "StudioBrain Templates CI -
  PLUGIN_INDEX_SIGNING_KEY (SBAI-7183)"; public half in
  `schemas/keys/plugin-index-trusted-keys.json`).

Verified end-to-end against the real bucket on 2026-08-19: build (empty
index — zero real v2 plugins exist yet, work item 6/SBAI-6818) → sign →
verify → publish → public read-back via `r2.dev` → idempotent rerun
(overwrite-only for the mutable index; the immutability guard for versioned
plugin artifacts is covered by `scripts/tests/test_publish_to_r2.py` and
will exercise for real once the first real plugin lands).

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
| `plugin.json` | Plugin manifest contract (full / frontend-only / protocol-adapter; v1 and v2) |
| `skill.yaml.json` | AI skill frontmatter contract (skills/*.yaml) |
| `fixtures/` | Test fixtures for plugin.json v2 schema validation (valid/invalid v1 and v2 manifests) |
