# Plugin Manifest Fixtures

Test fixtures for validating the plugin.json v2 schema and backwards-compatibility with v1 manifests.

## Fixture Types

| Fixture | Purpose | Should Validate |
|---------|---------|-----------------|
| `valid_v2_full_surfaces.json` | Complete v2 manifest with all surface types (page, panel, command, settings, widget), explicit capabilities, permissions, and placement metadata | ✅ PASS |
| `valid_v2_minimal.json` | Minimal valid v2 manifest with single surface | ✅ PASS |
| `invalid_v2_missing_required.json` | V2 manifest missing required fields (label, artifact.path, invalid surface type) and invalid permission formats | ❌ FAIL |
| `valid_v1_legacy.json` | Legacy v1 manifest using capabilities-based contract with `manifest_version: 1` | ✅ PASS |
| `invalid_v1_missing_capabilities.json` | Legacy v1 manifest missing required `capabilities` field | ❌ FAIL |

## Running Fixture Tests

```bash
# Validate all fixtures against the schema
python3 scripts/validate.py --fixtures

# Validate a specific fixture
python3 -c "
import json
from scripts.validate import make_validator

validator = make_validator('plugin.json')
with open('schemas/fixtures/valid_v2_full_surfaces.json') as f:
    data = json.load(f)
errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
print(f'Errors: {len(errors)}')
for err in errors:
    print(f'  - {err.message} at /{\"/\".join(str(p) for p in err.path)}')
"
```

## V2 Schema Key Changes

The v2 manifest introduces:

1. **`manifest_version` field** - Explicit version discriminator (1 or 2). Defaults to 1 for backwards compatibility.

2. **`surfaces` array** - Replaces the nested `capabilities.frontend.pages/panels` with an explicit, typed array. Each surface declares:
   - `type`: `"page" | "panel" | "command" | "settings" | "widget"`
   - `artifact.path`: Relative path to the HTML/JS file
   - `placement.location`: Where the surface mounts
   - `capabilities[]`: Granular capability requirements per surface
   - `permissions[]`: Permission grants per surface
   - `context{}`: Entity type filters, selection requirements

3. **Per-surface granularity** - Each surface can declare its own dependencies, capabilities, and permissions instead of inheriting from plugin-level.

4. **Explicit routes/event_handlers** - V2 allows declaring routes and event handlers as explicit arrays alongside (or instead of) the legacy `capabilities.backend` object.

5. **Backwards compatibility** - V1 manifests with `manifest_version: 1` (or omitting the field) continue to validate against the legacy `capabilities`-based schema.

## Migration Path

Authors with existing v1 manifests can:

1. **Continue using v1** - Legacy manifests remain valid indefinitely with `manifest_version: 1` (implicit or explicit).

2. **Migrate to v2** - Convert `capabilities.frontend.pages/panels` into the `surfaces` array:
   - V1 `pages[]` → V2 `surfaces[]` with `type: "page"`
   - V1 `panels[]` → V2 `surfaces[]` with `type: "panel"`
   - Add new surface types: `command`, `settings`, `widget`

Example migration:

```json
// V1 (still valid)
"capabilities": {
  "frontend": {
    "pages": [{"id": "dash", "route": "/plugins/my-plugin", "label": "Dash"}],
    "panels": [{"id": "side", "label": "Sidebar", "location": "entity-sidebar"}]
  }
}

// V2 equivalent
"manifest_version": 2,
"surfaces": [
  {"type": "page", "id": "dash", "label": "Dash", "artifact": {"path": "frontend/pages/dash.html"}, "placement": {"location": "plugins-nav"}},
  {"type": "panel", "id": "side", "label": "Sidebar", "artifact": {"path": "frontend/panels/side.html"}, "placement": {"location": "entity-sidebar"}}
]
```

## Adding New Fixtures

When extending the schema, add corresponding fixtures:

1. Create `valid_v2_<feature>.json` demonstrating the new feature
2. Create `invalid_v2_<violation>.json` testing validation catches the error
3. Update this README's table
4. Run `python3 scripts/validate.py --fixtures` to confirm
