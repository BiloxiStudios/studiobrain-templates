# Hello World Plugin

A minimal reference implementation demonstrating all core plugin system capabilities. Use this as a starting point when building your own StudioBrain plugin.

## What This Plugin Demonstrates

| Capability | File | Description |
|-----------|------|-------------|
| Plugin manifest | `plugin.json` | Declares id, name, version, capabilities, permissions, settings schema, data schema |
| Backend API routes | `backend/routes.py` | FastAPI router auto-mounted at `/api/ext/hello-world/` |
| Event handlers | `backend/events.py` | Listens to `entity.*` events on the backend event bus |
| Full-page dashboard | `frontend/pages/index.html` | Sandboxed iframe page linked from the sidebar nav |
| Sidebar panel | `frontend/panels/entity-notes.html` | Injected into the entity editor sidebar |
| Entity tab panel | `frontend/panels/entity-stats.html` | Injected as an extra tab in the entity editor |
| File-based storage | `data/notes.json` | Simple JSON storage for per-entity plugin data |
| Settings schema | `plugin.json` `settings_schema` | Configurable options shown in Settings > Plugins |

## Directory Structure

```
hello-world/
  plugin.json                         # Manifest (required for all plugins)
  README.md                           # This file
  backend/
    routes.py                         # FastAPI router
    events.py                         # Entity event handlers
  frontend/
    pages/
      index.html                      # Full-page plugin dashboard
    panels/
      entity-notes.html               # Sidebar panel (entity-sidebar location)
      entity-stats.html               # Entity tab panel (entity-tab location)
  data/
    notes.json                        # Persistent file-based storage
```

## Backend Routes

All backend routes are auto-mounted at `/api/ext/hello-world/` by the plugin loader:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/ext/hello-world/` | Greeting message |
| `GET` | `/api/ext/hello-world/status` | Plugin health check |
| `GET` | `/api/ext/hello-world/notes` | List notes for an entity |
| `POST` | `/api/ext/hello-world/notes` | Add a note to an entity |
| `DELETE` | `/api/ext/hello-world/notes/{id}` | Delete a note by ID |

The `router` variable in `routes.py` is discovered automatically — no registration needed.

## Event Handlers

`backend/events.py` registers a `register_handlers(event_bus)` function. The plugin loader calls this on startup. The hello-world example logs all `entity.*` events:

```python
@event_bus.on("entity.*")
async def on_entity_event(event):
    logger.info("[hello-world] Entity event: %s", event.event_type)
```

Common event patterns: `entity.created`, `entity.updated`, `entity.deleted`, `entity.*` (wildcard).

## Frontend: Accessing Plugin Context

The backend injects `window.PLUGIN_CONTEXT` into every sandboxed iframe before the HTML loads.

In panels:
```js
const ctx = window.PLUGIN_CONTEXT || {};
// ctx.pluginId    -> "hello-world"
// ctx.panelId     -> "entity-notes" | "entity-stats"
// ctx.entityType  -> "Character" | "Location" | ...
// ctx.entityId    -> "some-entity-slug"
```

In pages:
```js
const ctx = window.PLUGIN_CONTEXT || {};
// ctx.pluginId    -> "hello-world"
// ctx.page        -> "index"
```

Call your backend API:
```js
const API = `/api/ext/${ctx.pluginId}`;
const res = await fetch(`${API}/notes?entity_type=${ctx.entityType}&entity_id=${ctx.entityId}`);
const data = await res.json();
```

## Frontend: Theme Variables

**Never hardcode colors.** Use CSS variables injected by the backend:

```css
body {
  background: var(--surface-base-bg);
  color: var(--surface-base-text);
}
.card {
  background: var(--surface-elevated-bg);
  border: 1px solid var(--surface-elevated-border);
}
.accent-button {
  background: var(--plugin-accent);   /* your accent_color from plugin.json */
}
```

## Settings Schema

Settings defined in `plugin.json` under `settings_schema` appear automatically in **Settings > Plugins**. From the backend, access settings via the `settings` parameter in your route functions (injected by the plugin loader).

```json
"settings_schema": {
  "greeting": {
    "type": "string",
    "label": "Greeting Message",
    "required": false,
    "default": "Hello from the plugin system!",
    "scope": "instance"
  }
}
```

Supported types: `string`, `boolean`, `integer`, `enum`, `text`.

## Using This as a Template

1. Copy the `hello-world/` directory to a new plugin directory under `_Plugins/`.
2. Update `plugin.json`: change `id`, `name`, `description`, `author`, `accent_color`.
3. Edit `backend/routes.py`: replace the notes routes with your own logic.
4. Edit `backend/events.py`: register only the events you need (or remove the file).
5. Edit the HTML files in `frontend/`: replace the demo UI with your own.
6. Enable the plugin: `POST /api/plugins/{your-plugin-id}/enable`.

For the full developer reference including advanced storage options, event bus patterns, data schema, security rules, and deployment compatibility, see `_Plugins/PLUGIN_DEVELOPMENT.md`.
