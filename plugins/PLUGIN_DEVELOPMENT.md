# Plugin Development Guide

## Theme Rules

**NEVER hardcode hex colors.** The backend injects `plugin-theme.css` into every plugin iframe automatically. Use CSS variables for all colors.

### Surface Variables

| Variable | Purpose |
|----------|---------|
| `--surface-base-bg` | Page background |
| `--surface-base-text` | Primary text |
| `--surface-base-text-secondary` | Secondary/muted text |
| `--surface-base-border` | Borders on base surface |
| `--surface-base-hover` | Hover state background |
| `--surface-elevated-bg` | Card/panel background |
| `--surface-elevated-text` | Text on elevated surfaces |
| `--surface-elevated-border` | Card borders |
| `--surface-elevated-hover` | Card hover state |
| `--surface-primary-bg` | Primary brand color |
| `--surface-primary-text` | Text on primary surface |
| `--surface-success-border` | Green status |
| `--surface-warning-border` | Yellow/amber status |
| `--surface-error-border` | Red status |
| `--surface-info-text-secondary` | Blue info color |
| `--plugin-accent` | Your plugin's brand color |

### Your Plugin's Accent Color

Set `accent_color` in your `plugin.json`:

```json
{
  "accent_color": "#5865F2"
}
```

Then use `var(--plugin-accent)` everywhere you want your brand color:

```css
.my-button { background: var(--plugin-accent); color: #fff; }
.my-border { border-left: 3px solid var(--plugin-accent); }
```

If you don't set an accent, it defaults to the app's primary color.

---

## Plugin Context

The backend injects `window.PLUGIN_CONTEXT` before your HTML loads:

```js
// In panels:
window.PLUGIN_CONTEXT = {
  pluginId: "my-plugin",
  panelId: "my-panel",
  entityType: "characters",
  entityId: "abc123"
};

// In pages:
window.PLUGIN_CONTEXT = {
  pluginId: "my-plugin",
  page: "index"
};
```

---

## Backend API

Your plugin's custom routes are mounted at:

```
/api/ext/{plugin-id}/...
```

From a panel, call your backend:

```js
const ctx = window.PLUGIN_CONTEXT || {};
const API = `/api/ext/${ctx.pluginId}`;

const res = await fetch(`${API}/my-endpoint?entity_id=${ctx.entityId}`);
const data = await res.json();
```

---

## File Structure

```
my-plugin/
  plugin.json            # Manifest (required)
  backend/
    routes.py            # FastAPI router (prefix auto-set to /api/ext/{id})
    events.py            # Event handlers (entity.created, entity.updated, etc.)
  frontend/
    panels/
      sidebar-panel.html # Sidebar panel (location: entity-sidebar)
      tab-panel.html     # Tab panel (location: entity-tab)
    pages/
      index.html         # Dashboard page at /plugins/{id}
```

---

## Minimal Panel Template

```html
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, sans-serif;
    padding: 12px;
    background: transparent;
    color: var(--surface-base-text);
    font-size: 13px;
  }
  .card {
    background: var(--surface-elevated-bg);
    border: 1px solid var(--surface-elevated-border);
    border-radius: 8px;
    padding: 12px;
  }
  .btn {
    background: var(--plugin-accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 12px;
  }
  .btn:hover { opacity: 0.85; }
  .text-muted { color: var(--surface-base-text-secondary); }
</style>
</head>
<body>
  <div class="card">
    <h3>My Panel</h3>
    <p class="text-muted" id="info">Loading...</p>
    <button class="btn" onclick="doAction()">Action</button>
  </div>
  <script>
    const ctx = window.PLUGIN_CONTEXT || {};
    document.getElementById('info').textContent =
      `Entity: ${ctx.entityType}/${ctx.entityId}`;
    function doAction() { alert('Plugin action!'); }
  </script>
</body>
</html>
```

---

## Live Theme Sync

Plugin iframes automatically receive the user's customized theme colors. The injected `plugin-theme.css` provides sensible **defaults**, and a theme-sync script overrides them with the user's live settings.

**How it works:**
1. Plugin iframes are loaded via the Next.js proxy (`/plugin-proxy/...`) so they share the frontend's origin
2. The backend injects a `plugin-theme-sync` script into every plugin HTML
3. On load, the script reads the parent document's computed `--surface-*` CSS variables directly (same-origin access)
4. A `MutationObserver` on the parent `<html>` element re-syncs whenever the user changes theme
5. For cross-origin fallback (direct backend access), it listens for `postMessage` instead

**You don't need to do anything** — this is handled automatically. Just use `var(--surface-*)` in your CSS and the values will always reflect the user's theme.

If you need to react to theme changes in JS:
```js
// Works in same-origin mode (via proxy)
try {
  var isDark = window.parent.document.documentElement.classList.contains('dark');
} catch(e) {
  // Cross-origin fallback
}
```

---

## Settings Scopes

Plugin settings support two scopes declared in `settings_schema`:

| Scope | Who sets it | Use for |
|-------|------------|---------|
| `"instance"` (default) | Admin / org-wide | API keys, webhook URLs, server addresses, feature flags |
| `"user"` | Each individual user | Personal preferences, notification toggles, display options |

Add `"scope"` to each field in your `settings_schema`:

```json
{
  "settings_schema": {
    "api_key": {
      "type": "secret",
      "label": "API Key",
      "scope": "instance",
      "required": true
    },
    "notify_on_post": {
      "type": "boolean",
      "label": "Notify me on post",
      "scope": "user",
      "default": true
    }
  }
}
```

If `scope` is omitted, it defaults to `"instance"` (backwards compatible).

### How it works

- **Instance settings** are stored in the database, encrypted if `type: "secret"`.
- **User settings** are stored per-user in the same database table.
- The UI automatically splits settings into "Organization Settings" and "My Preferences" sections when both scopes are present.
- Secret fields show `"********"` in the UI and API responses — the plaintext is never sent to the frontend.
- Backend plugin code gets the real (decrypted) values via `plugin_settings_service`.

### Accessing settings from your backend

```python
from services.plugin_settings_service import get_all_settings

settings = get_all_settings("my-plugin")
api_key = settings.get("api_key")  # Decrypted automatically
```

---

## Plugin Data Storage

Plugins have two storage options. Choose based on your needs:

| | File-based (default) | Database (opt-in) |
|---|---|---|
| **Setup** | Zero — just read/write JSON | Import `PluginDataService` |
| **Queryable** | No | Yes — filter by entity, type, date |
| **Team isolation** | No | Yes — `team_id` scoping |
| **Audit trail** | No | Yes — `created_by`, `updated_by`, timestamps |
| **Cross-plugin access** | No | Yes — generic CRUD API |
| **Best for** | Simple personal data, caches, config | Time entries, notes, sync logs, shared records |

### Option 1: File-based storage (default)

Store data as JSON files in your plugin's `data/` folder. Simple, no setup required.

```
my-plugin/
  plugin.json
  data/                  # Plugin's private data folder
    entries.json         # Your plugin's data files
    config.json          # Any persistent config
  backend/
    routes.py
  frontend/
    ...
```

In your `routes.py`, resolve the data directory relative to the plugin root:

```python
from pathlib import Path
import json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def load_data(filename: str, default=None):
    path = DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default if default is not None else {}

def save_data(filename: str, data):
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
```

**Guidelines:**
- Store data as JSON files in your plugin's `data/` folder
- Never write outside your plugin's directory
- Add `data/` to `.gitignore` if plugin data is user-specific
- Keep filenames descriptive: `time_entries.json`, `webhook_config.json`, etc.
- For large datasets, consider splitting by date or entity: `entries_2026-02.json`

**Reference implementation:** `hello-world` plugin uses file-based notes storage in `data/notes.json`.

### Option 2: Database storage (opt-in)

For plugins that need queryability, team isolation, or shared records, use `PluginDataService`:

```python
from services.plugin_data_service import PluginDataService

data_svc = PluginDataService("my-plugin")

# Create a record
record = data_svc.create(
    record_type="time_entry",
    data={"start_time": "2026-02-22T10:00:00Z", "duration_seconds": 3600},
    entity_type="character",
    entity_id="ch_alice",
)

# List records (paginated, filterable)
result = data_svc.list(record_type="time_entry", entity_id="ch_alice", limit=50)
# Returns: {"records": [...], "total": N, "limit": 50, "offset": 0}

# Get / Update / Delete
record = data_svc.get("uuid-string")
record = data_svc.update("uuid-string", {"note": "updated"})
data_svc.delete("uuid-string")  # Soft delete
```

**Generic CRUD API** — available automatically for all plugins without writing route code:

```
GET    /api/ext/{plugin_id}/data/{record_type}              — list records
POST   /api/ext/{plugin_id}/data/{record_type}              — create record
GET    /api/ext/{plugin_id}/data/{record_type}/{record_id}  — get record
PUT    /api/ext/{plugin_id}/data/{record_type}/{record_id}  — update record
DELETE /api/ext/{plugin_id}/data/{record_type}/{record_id}  — soft-delete
```

**Declare your record types** in `plugin.json` with `data_schema` (optional but recommended):

```json
{
  "data_schema": {
    "time_entry": {
      "label": "Time Entry",
      "fields": {
        "start_time": "datetime",
        "end_time": "datetime",
        "duration_seconds": "integer",
        "note": "string",
        "billable": "boolean"
      }
    }
  }
}
```

**Reference implementations:**
- `time-tracker` plugin — full plugin with Python backend using `PluginDataService` directly
- `data-notes` plugin — **frontend-only** plugin calling the generic CRUD API from JavaScript (no Python backend required)

### Calling the generic CRUD API from frontend HTML (frontend-only plugins)

Frontend-only plugins (no `backend/` directory) can still use database storage by calling
the generic REST endpoints from JavaScript. Authentication cookies are sent automatically
since the iframe shares the same origin via the `/plugin-proxy/` rewrite.

```js
// In your panel or page HTML:
const ctx = window.PLUGIN_CONTEXT || {};
const API = `/api/ext/${ctx.pluginId}/data`;

// List records for the current entity
async function loadRecords(recordType) {
  const params = new URLSearchParams({ limit: '50', offset: '0' });
  if (ctx.entityType) params.set('entity_type', ctx.entityType);
  if (ctx.entityId)   params.set('entity_id',   ctx.entityId);

  const res = await fetch(`${API}/${recordType}?${params}`, { credentials: 'include' });
  const data = await res.json();
  return data.records || [];  // Each record: { record_id, data, entity_type, entity_id, created_at, ... }
}

// Create a record
async function createRecord(recordType, payload) {
  const res = await fetch(`${API}/${recordType}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      data: payload,               // Your plugin's record fields (free-form JSON)
      entity_type: ctx.entityType, // Optional: associate with current entity
      entity_id:   ctx.entityId,   // Optional: associate with current entity
    }),
  });
  return await res.json();
}

// Update a record (partial merge)
async function updateRecord(recordType, recordId, patch) {
  const res = await fetch(`${API}/${recordType}/${recordId}`, {
    method: 'PUT',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: patch }),
  });
  return await res.json();
}

// Delete a record (soft delete)
async function deleteRecord(recordType, recordId) {
  const res = await fetch(`${API}/${recordType}/${recordId}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  return await res.json();
}
```

Key points for frontend-only plugins:
- The `tenant_id` is derived automatically from the user's JWT cookie — you never pass it explicitly
- Records are always scoped to the current tenant — users cannot access other tenants' data
- `record_id` is a UUID auto-generated by the backend unless you pass your own via the POST body
- Soft-deleted records are excluded from list results automatically

### Migrating from file-based to database

If you structure your JSON data in this format, it migrates with one line:

```json
{
  "records": [
    {
      "id": "uuid-string",
      "record_type": "time_entry",
      "entity_type": "character",
      "entity_id": "ch_alice",
      "data": {
        "start_time": "2026-02-22T10:00:00Z",
        "duration_seconds": 3600,
        "note": "Worked on backstory"
      },
      "created_at": "2026-02-22T10:00:00Z"
    }
  ]
}
```

Then in your backend:

```python
data_svc = PluginDataService("my-plugin")
data_svc.import_from_json("data/entries.json")  # Reads file, inserts into DB
data_svc.export_to_json("data/entries_backup.json")  # DB -> JSON backup
```

---

## Plugin Data Backup & Restore

Plugin data is automatically backed up before uninstalls and updates. Backups are stored in `_Plugins/_backups/{plugin_id}_{timestamp}/`.

**What gets backed up:**
- `data/` folder (file-based storage)
- DB `plugin_data` records (exported as JSON)
- DB `plugin_settings` (exported as JSON)

**API endpoints:**
- `POST /api/plugins/{id}/backup` — manually trigger a backup
- `POST /api/plugins/{id}/restore` — restore from latest backup
- `GET /api/plugins/{id}/backups` — list available backups

When reinstalling a plugin that has previous backups, you can restore data via the API.

---

## Utility Classes (from injected theme)

| Class | Effect |
|-------|--------|
| `.bg-base` | Base background |
| `.bg-elevated` | Elevated/card background |
| `.bg-accent` | Plugin accent background |
| `.text-primary` | Primary text color |
| `.text-secondary` | Muted text color |
| `.text-accent` | Plugin accent as text |
| `.border-base` | Base border color |
| `.border-elevated` | Elevated border color |
| `.btn-accent` | Accent-colored button |
| `.btn-primary` | Primary-colored button |
| `.btn-ghost` | Ghost/outline button |
| `.badge-success` | Green status badge |
| `.badge-warning` | Yellow status badge |
| `.badge-error` | Red status badge |
| `.card` | Elevated card with border |
| `.shadow-sm/md/lg` | Box shadows |
