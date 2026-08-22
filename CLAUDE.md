# CLAUDE.md -- studiobrain-templates

## Repo Boundaries

This repo is **studiobrain-templates** — **data only**. Entity templates, document templates, map templates, layouts, rules, skills, taxonomies, and `*.provider.yaml` / ability / canvas catalog files. Apache 2.0, public. Consumed by core and cloud editions.

This repo is **NOT a plugin home**. Do not add plugin source, WASM, Workers, or a plugin catalog here.

| Plugin / community home | Role |
|---|---|
| `BiloxiStudios/studiobrain-plugins` | Official / trusted-vendor / partner plugins. WIT guests + official Workers. Signed WASM. Private. |
| `BiloxiStudios/studiobrain-community` | Community data and community plugins (rename of `studiobrain-community-plugins`). Public registry. Open PRs go there. |

**NEVER PR community data or community plugins into this repo.** Send those to `studiobrain-community`.

For the full 7-repo boundary model, canonical crate ownership, and forbidden patterns, see the authoritative reference in **studiobrain-docs** (do not edit that file from this repo):

**`studiobrain-docs/plans/SBAI-2015-repo-boundaries-canonical.md`**

Quick reference:

| Field | Value |
|---|---|
| **License** | Apache 2.0 |
| **Visibility** | Public |
| **Role** | Entity/document/map templates, layouts, rules, skills, provider/ability/canvas catalog data. Pure data (Markdown + YAML frontmatter + JSON layouts). |
| **Consumers** | studiobrain-core (CatalogSync), studiobrain-cloud (marketplace), studiobrain-app (pre-bundled Standard pack) |
| **Contents** | No backend code, no frontend code, no Rust, no binaries, no plugin runtimes |

### Forbidden in this repo
- ❌ Backend code (Python application / Rust / Node services)
- ❌ Frontend components
- ❌ Plugin source, WASM, Workers, or an installable plugin catalog
- ❌ Community plugin/data submissions (those belong in `studiobrain-community`)
- ❌ Compiled artifacts or binary blobs
- ❌ Commercial AI logic of any kind

### Required in this repo
- ✅ `TEMPLATE.md` files with YAML frontmatter (entities, documents, maps)
- ✅ Layout JSONs for form rendering via widget registry
- ✅ `pack.json` manifests for template packs (may *list* official plugin ids; they do not ship plugin code)
- ✅ Provider / ability / canvas catalog YAML

## Project Overview

Entity templates and AI generation rules for StudioBrain. Pure data repository -- Markdown files with YAML frontmatter define the 17+ entity types and generation constraints. No backend code, no frontend code, no plugins. Licensed under Apache 2.0 (public).

**Owner:** Biloxi Studios Inc.
**JIRA:** SBAI (biloxistudios.atlassian.net)
**GitHub:** BiloxiStudios/studiobrain-templates

## Architecture

```
studiobrain-templates/
├── templates/
│   ├── Standard/                       # Entity templates (CHARACTER, LOCATION, ITEM, etc.)
│   ├── Core/                           # Core templates (ASSEMBLY, DIALOGUE, QUEST, TIMELINE)
│   ├── Custom/                         # User-created templates (.gitkeep)
│   ├── Layouts/                        # UI layout definitions (JSON)
│   ├── Packs/                          # Template packs (starter-characters, starter-locations, etc.)
│   ├── Providers/                      # Provider catalog YAML
│   └── ExampleImplementation/          # Example entities using the templates
├── rules/
│   ├── *.md                            # Rule files (CHARACTER_RULES, LOCATION_RULES, etc.)
│   ├── Core/                           # Core rules (assembly_constraints.yaml, dialogue_flow.yaml)
│   ├── Standard/                       # Standard rules (character_consistency, style_guide, world_lore)
│   ├── Custom/                         # User-created rules (.gitkeep)
│   └── User/                           # Per-user rule overrides (.gitkeep)
├── skills/                             # AI skill YAML
├── taxonomies/                         # Controlled vocabularies
├── schemas/                            # JSON Schema contracts for the data above
├── catalog-index.json                  # Badge index; CI republishes to R2 hourly + on merge
├── package.json                        # @studiobrain/templates (npm package)
├── LICENSE                             # Apache 2.0
└── .github/workflows/ci.yml           # YAML/schema validation + catalog-index → R2
```

## Development

```bash
# Validate all templates and rules (CI runs this)
pip install pyyaml
python3 scripts/validate.py             # If scripts/ exists, or inline validation

# Manual validation: every .md file in templates/ and rules/ must have valid YAML frontmatter
```

There is no application build step. This is a data-only package. CI regenerates `catalog-index.json` and uploads it to R2 at `catalog/catalog-index.json` on merge to main and hourly.

## Git Workflow

1. Branch from `main` (e.g., `SBAI-123-feature-name`)
2. Every commit references a JIRA ticket (`SBAI-XXX`)
3. Open PR against `main`; CI validates YAML frontmatter in all templates and rules
4. Merge to `main` republishes `catalog-index.json` to R2

## Key Rules

- **NO backend code, NO frontend code, NO Rust, NO binaries, NO commercial AI.** This repo is pure data (Markdown, YAML, JSON).
- **NO plugins.** Official plugins live in `studiobrain-plugins` (WIT + Worker). Community data/plugins go to `studiobrain-community`. Never PR community data here.
- **Every template and rule file must have valid YAML frontmatter.** Files start with `---`, contain a YAML mapping, and close with `---`. CI enforces this.
- **Apache 2.0 license.** This repo is public. Do not add proprietary code or credentials.
- **Template packs** in `templates/Packs/` must include a `pack.json` manifest with metadata. A pack may list official plugin ids (resolved from the plugins repo / R2), but must not embed plugin trees.
- When adding a new entity type, add both the template file (in `templates/Standard/`) and a corresponding rules file (in `rules/`).


## Cloudflare Worker Convention (`packages/cloudflare-worker/`)

*Owner-accepted ADR (2026-08-14, group:studiobrain).* Full ADR:
`/mnt/tank/Studio/Brains/crews/sbcrew/sbcrew-charters/ADR-cloudflare-worker-convention.md`

This repo is data-only and does **not** host a Cloudflare Worker package. Official plugin Workers live in `studiobrain-plugins` / `studiobrain-cloud`. If a Worker is ever needed for catalog edge glue, it belongs in the owning runtime repo — not here.

1. **Canonical path** — CF-specific code lives in `packages/cloudflare-worker/` in that
   repo's canonical home. The name is deliberately verbose (chosen over `cf`) so no
   decoder is needed.
2. **Only CF-specific code goes there** — Worker entrypoint, wrangler config/bindings,
   DO/R2/D1 glue, container shims. Code that only exists because the target is Workers.
3. **Portable TS does NOT go there** — Logic moved from Rust that is not CF-specific
   extends `studiobrain-sdk` (runs everywhere equally). Split axis: content -> templates
   repo; shared SDK -> core; CF-specific build -> `cloudflare-worker`. Never place by
   CI convenience.
4. **Feature-preservation** — Rust-to-TS moves must not lose features. Named risk:
   serde/Rust JSON-schema enforcement is stronger than zod. Do not move generation
   shape-enforcement to zod without proven parity (SBAI-5428/5429). If in doubt, it does
   not move.
5. **Naming** — Workers named to match their crate/service (e.g. `sb-<domain>-worker`),
   no opaque names.
6. **wasm32 boundary guard** — Nothing may be added to a crate in a wasm32 boundary
   that cannot compile to `wasm32-unknown-unknown`. Use per-target cfg-gating, never a
   dep that breaks the wasm build (SBAI-6881).
7. **Deploy preference** — Cloudflare native GitHub-to-Worker git integration. Custom
   CI deploy workflows are under separate review (SBAI-6935).
