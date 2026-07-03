## JIRA Ticket

<!-- Link the JIRA ticket this PR addresses, e.g. SBAI-XXXX -->
JIRA: https://biloxistudios.atlassian.net/browse/SBAI-XXXX

## Summary

<!-- A brief description of what this PR changes and why. -->

## Type of change

<!-- Check all that apply -->
- [ ] New entity template
- [ ] New or updated rule
- [ ] New or updated plugin (Python backend)
- [ ] New or updated plugin (WASM sample)
- [ ] Template layout / JSON schema update
- [ ] Template pack
- [ ] Documentation / governance
- [ ] CI / tooling

## Pre-merge checklist

<!-- All items must be checked before requesting merge approval. -->

### Templates & Rules
- [ ] Every new/modified `.md` in `templates/` has valid YAML frontmatter (CI validates this).
- [ ] Every new/modified `.md` in `rules/` has valid YAML frontmatter (CI validates this).
- [ ] New entity types include both a `templates/Standard/MYTYPE_TEMPLATE.md` and a `rules/MYTYPE_RULES.md`.

### Plugins
- [ ] Every `plugin.json` contains the required keys: `id`, `name`, `version`, `description`, `type`, `author`.
- [ ] WASM plugin samples follow the `hello-world-wasm` pattern (standalone `Cargo.toml`, no workspace file).
- [ ] `_plugins.json` registry updated if a plugin was added or removed.

### Schemas & Layouts
- [ ] JSON files are valid JSON and pass the CI schema validation step.

### General
- [ ] No compiled binaries, `.wasm` artifacts, or secrets are included.
- [ ] No application code (Python, TypeScript, Node) added to this repo.
- [ ] Branch name follows `SBAI-XXXX-short-description` convention.
- [ ] `README.md` or relevant docs updated if the repository structure changed.

## Testing

<!-- Describe any manual validation you performed (e.g. ran the frontmatter validation script locally). -->

## Related PRs / issues

<!-- List any related PRs or issues. -->
