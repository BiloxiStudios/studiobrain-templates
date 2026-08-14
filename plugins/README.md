# _Plugins Directory

> ## ⚠️ DEPRECATED — DO NOT BUILD NEW PLUGINS AGAINST THIS DIRECTORY
>
> **The 28 plugins in this directory target a plugin host that no longer exists.**
>
> Their backends are Python/FastAPI modules (`backend/routes.py`, `backend/events.py`),
> written for the legacy Python backend that has been retired. The current StudioBrain
> plugin runtime (`sb-plugin-wasmtime`) loads **WASM Components only** — it cannot load
> a Python module, so nothing in this directory is loadable today.
>
> These plugins were conceptual proof-of-concept designs demonstrating that the plugin
> *system* could work. They were never production-validated, and no ingestion path ever
> published them to a user-facing plugin catalog.
>
> **Owner decision (2026-08-12, recorded in SBAI-6818):** these are *not* being migrated.
> The host-interaction model changed completely, so every migration would be a full
> rewrite with nothing gained by starting from the old source. New, well-designed
> plugins are being built from scratch on the real SDK instead.
>
> ### Build against this instead
>
> | What | Where |
> |---|---|
> | Guest SDK + WIT world | `studiobrain-core` → `packages/plugin-sdk/wit/` (`plugin.wit`, `world.wit`) |
> | Starter templates | `studiobrain-core` → `packages/plugin-sdk/templates/` (`rust`, `python`, `typescript`, `frontend-panel`) |
> | Working reference (Rust) | `studiobrain-core` → `_Plugins/entity-notes`, `_Plugins/entity-snapshots` |
>
> Rust plugins use `wit-bindgen`; Python plugins use `componentize-py`. Both emit the
> WASM **Component** binary format. Plugins built with the **Extism** PDK are also not
> loadable — Extism produces core wasm modules, which is a different, incompatible ABI.
>
> Kept in place for historical reference and for the non-plugin content in this repo
> (`templates/`, `rules/`, `skills/`), which is unaffected and still current.
>
> Tracking: SBAI-6815 · Replacement work: SBAI-6818 · Architecture: SBAI-6854

## What Plugins Are

Plugins extend StudioBrain with:
- **Custom UI panels** embedded in entity views (sidebar or tab)
- **Full-page dashboards** accessible from the sidebar nav
- **Backend API routes** mounted at `/api/ext/{plugin-id}/...`
- **Entity event handlers** that react to entity lifecycle events

*(Historical — describes the retired Python plugin host, not the current runtime.)*
Plugins ran in sandboxed iframes (frontend) and were imported as isolated Python modules
(backend). They could not access other tenants' data and could not write outside their own
directory. In the current runtime the backend half is a sandboxed WASM Component instead;
see the deprecation notice above.

## How to Enable a Plugin

### Via the UI

Go to **Settings > Plugins** in the StudioBrain app. Find the plugin and click **Enable**.

### Via the API

```bash
curl -s -X POST http://localhost:8201/api/plugins/{plugin-id}/enable \
  -H "Authorization: Bearer $TOKEN"
```

After enabling, the plugin's UI panels and pages appear automatically. Backend routes are registered on next restart.

## Plugin Types

| Type | Description |
|------|-------------|
| `"full"` (default) | Has both frontend HTML and backend Python. Registers API routes and event handlers. |
| `"frontend-only"` | HTML/CSS/JS only. Uses the app's REST API and generic data CRUD. No Python backend. |

## Required Files

Every plugin must have:

```
plugin-name/
  plugin.json      # Manifest (required for all plugins)
```

Full plugins also need at least one of:
```
  backend/
    routes.py      # FastAPI router
    events.py      # Entity event handlers
```

Frontend plugins need at least:
```
  frontend/
    panels/        # Panel HTML files
    pages/         # Page HTML files
```

## plugin.json Quick Reference

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "What this plugin does.",
  "author": "Your Name",
  "type": "full",
  "capabilities": {
    "backend": {
      "routes": ["backend/routes.py"],
      "event_handlers": ["backend/events.py"]
    },
    "frontend": {
      "pages": [
        {
          "id": "dashboard",
          "route": "/plugins/my-plugin",
          "label": "My Plugin",
          "icon": "plug",
          "nav_section": "plugins"
        }
      ],
      "panels": [
        {
          "id": "sidebar",
          "label": "My Panel",
          "location": "entity-sidebar",
          "icon": "plug"
        }
      ]
    }
  },
  "permissions": ["entity:read"],
  "settings_schema": {
    "api_key": {
      "type": "secret",
      "label": "API Key",
      "scope": "instance",
      "required": true
    }
  },
  "accent_color": "#5865F2"
}
```

**The `"type"` field** defaults to `"full"`. Set `"type": "frontend-only"` for plugins with no Python backend — the loader will skip importing `backend/` for these plugins.

### Key field summary

| Field | Notes |
|-------|-------|
| `id` | Must match the directory name. Lowercase kebab-case. |
| `type` | `"full"` (default) or `"frontend-only"`. |
| `capabilities.backend` | Only for `"full"` plugins. Routes prefix is set automatically to `/api/ext/{id}`. |
| `capabilities.frontend.panels[].location` | `"entity-sidebar"` or `"entity-tab"`. |
| `settings_schema[].scope` | `"instance"` (org-wide, default) or `"user"` (per-user). |
| `settings_schema[].type` | `"string"`, `"boolean"`, `"number"`, or `"secret"`. |
| `accent_color` | CSS value or `var(--surface-primary-bg)`. Never hardcode hex colors inside your HTML. |

## Directory Contents

| Directory/File | Purpose |
|---------------|---------|
| `hello-world/` | Minimal reference plugin with file-based storage |
| `time-tracker/` | Full plugin with DB-backed storage |
| `kanban-board/` | Full plugin with entity-tab panel |
| `discord-poster/` | Integration plugin with event handlers |
| `_shared/` | Shared assets available to all plugins |
| `_plugins.json` | Registry of enabled/disabled state (self-hosted and desktop modes) |
| `_plugin_settings.json` | Plugin settings (self-hosted mode) |
| `_backups/` | Auto-generated backups from install/uninstall operations |
| `PLUGIN_CATALOG.md` | Marketplace catalog listing |
| `PLUGIN_DEVELOPMENT.md` | Extended developer reference (settings, data storage, backup/restore) |

## Full Developer Documentation

For the complete developer guide including:
- Full manifest spec with all fields
- Frontend development (theme variables, PLUGIN_CONTEXT, sandbox rules)
- Backend development (routes, event handlers, settings access)
- Data storage options (file-based and DB)
- REST API reference
- Deployment compatibility table
- Security rules

See: **`docs/plugins/README.md`** (developer guide) and **`docs/plugins/API.md`** (REST API reference)

## Contribution Guidelines

1. **Name your directory** to match your `id` in `plugin.json`. Use lowercase kebab-case.
2. **Follow the theme system.** Never hardcode hex colors in plugin HTML. Use `var(--surface-*)` and `var(--plugin-accent)` from the injected CSS.
3. **Declare your permissions** in `plugin.json`. Only request what you need.
4. **Test both plugin types:** Verify your plugin works in both light and dark mode.
5. **Add to the catalog:** Submit a PR updating `PLUGIN_CATALOG.md` with your plugin's listing.
6. **Security checklist before submitting:**
   - No hardcoded credentials or API keys in source
   - No writes outside your plugin directory
   - No cross-tenant data access
   - Secrets declared with `"type": "secret"` in `settings_schema`

Plugins are reviewed by Biloxi Studios before being added to the marketplace.
