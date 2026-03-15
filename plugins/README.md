# _Plugins Directory

This directory contains all StudioBrain plugins. Each plugin is a subdirectory with a `plugin.json` manifest.

## What Plugins Are

Plugins extend StudioBrain with:
- **Custom UI panels** embedded in entity views (sidebar or tab)
- **Full-page dashboards** accessible from the sidebar nav
- **Backend API routes** mounted at `/api/ext/{plugin-id}/...`
- **Entity event handlers** that react to entity lifecycle events

Plugins run in sandboxed iframes (frontend) and are imported as isolated Python modules (backend). They cannot access other tenants' data and cannot write outside their own directory.

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
