# Contributing to StudioBrain Templates

Thank you for your interest in contributing to `studiobrain-templates`! This repository is an **Apache 2.0** open-source data package — pure Markdown templates, YAML rules, JSON layouts, and plugin SDK samples. There is no backend or frontend application code here.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [What lives in this repo](#what-lives-in-this-repo)
- [Getting started](#getting-started)
- [Making a contribution](#making-a-contribution)
- [Commit and branch conventions](#commit-and-branch-conventions)
- [Pull request checklist](#pull-request-checklist)
- [Validation](#validation)
- [Reporting bugs and requesting features](#reporting-bugs-and-requesting-features)

---

## Code of Conduct

Be respectful. We follow the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

## What lives in this repo

| Path | What belongs here |
|---|---|
| `templates/Standard/` | Entity-type template `.md` files with YAML frontmatter |
| `templates/Core/` | Core templates (Assembly, Dialogue, Quest, Timeline) |
| `templates/Layouts/` | JSON layout definitions for the widget registry |
| `templates/Packs/` | Template pack manifests (`pack.json`) |
| `rules/` | AI generation rule `.md` files with YAML frontmatter |
| `plugins/<name>/` | Plugin manifest (`plugin.json`) + optional `frontend/` HTML panels |
| `plugins/<name>-wasm/` | WASM plugin SDK samples (`plugin.json`, `Cargo.toml`, `src/lib.rs`) |
| `schemas/` | JSON Schema definitions for template and plugin validation |

### What does NOT belong here

- ❌ Python/TypeScript/Node application logic
- ❌ Compiled binaries or `.wasm` artifacts
- ❌ Credentials, secrets, or API keys
- ❌ Commercial-only AI logic

If you are building a full plugin implementation (not just an SDK sample), that work belongs in the separate **studiobrain-plugins** repository.

---

## Getting started

1. **Fork** the repository and clone your fork.
2. Create a branch from `main` named after your JIRA ticket:
   ```
   git checkout -b SBAI-XXXX-short-description
   ```
3. Make your changes (see conventions below).
4. Run the local validation check before opening a PR:
   ```bash
   pip install pyyaml jsonschema
   python3 -c "
   import yaml, sys, pathlib
   errors = []
   for md in sorted(pathlib.Path('templates').rglob('*.md')):
       if md.name == 'README.md':
           continue
       text = md.read_text()
       if not text.startswith('---'):
           errors.append(f'{md}: missing frontmatter')
           continue
       parts = text.split('---', 2)
       if len(parts) < 3:
           errors.append(f'{md}: unclosed frontmatter')
           continue
       try:
           yaml.safe_load(parts[1])
       except yaml.YAMLError as e:
           errors.append(f'{md}: {e}')
   if errors:
       [print(e) for e in errors]; sys.exit(1)
   print('All templates valid.')
   "
   ```

---

## Making a contribution

### Adding a new entity type

1. Create `templates/Standard/MYTYPE_TEMPLATE.md` with valid YAML frontmatter.
2. Create `rules/MYTYPE_RULES.md` with valid YAML frontmatter.
3. Both files must have the same `entity_type` value in their frontmatter.

### Adding or updating a plugin

1. Every plugin directory must contain a `plugin.json` with the required keys: `id`, `name`, `version`, `description`, `type`, `author`.
2. WASM plugins also need a `Cargo.toml` and `src/lib.rs` following the pattern in `plugins/hello-world-wasm/`.
3. Do not add workspace-level `Cargo.toml` files — each WASM plugin is a standalone crate.

### Adding a template pack

1. Create a directory under `templates/Packs/<pack-name>/`.
2. Include a `pack.json` manifest with `id`, `name`, `version`, `description`, and `templates` fields.

### Updating layouts

JSON files in `templates/Layouts/` must remain valid JSON and conform to the widget registry schema in `schemas/`.

---

## Commit and branch conventions

- Branch names: `SBAI-XXXX-short-description` (JIRA ticket prefix required).
- Commit messages: start with the JIRA ticket, e.g. `SBAI-4636 fix license metadata`.
- Keep commits focused — one logical change per commit.

---

## Pull request checklist

Before requesting review, confirm:

- [ ] Branch is named `SBAI-XXXX-*` and targets `main`.
- [ ] Every new/modified template `.md` has valid YAML frontmatter (CI will verify).
- [ ] Every new/modified rules `.md` has valid YAML frontmatter (CI will verify).
- [ ] `plugin.json` manifests include all required keys.
- [ ] No compiled binaries, credentials, or secrets are included.
- [ ] `README.md` or relevant docs updated if structure changed.
- [ ] PR description references the JIRA ticket.

See `.github/PULL_REQUEST_TEMPLATE.md` for the full template used when opening a PR.

---

## Validation

CI runs automatically on every PR targeting `main`. The checks are defined in `.github/workflows/ci.yml` and cover:

1. **YAML frontmatter** — all `.md` files in `templates/` and `rules/` (except `README.md` and `RULES_INDEX.md`).
2. **JSON Schemas** — all files in `schemas/`.
3. **Plugin manifests** — every `plugins/*/plugin.json` must have the required keys.

Fix any CI failures before requesting a merge.

---

## Reporting bugs and requesting features

Open an issue on GitHub or create a JIRA ticket under the **SBAI** project at [biloxistudios.atlassian.net](https://biloxistudios.atlassian.net).

---

*Maintained by [Biloxi Studios Inc.](https://github.com/BiloxiStudios) — Apache 2.0.*
