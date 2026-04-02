# Hello World Plugin (WASM)

A minimal reference implementation demonstrating the WASM plugin stack for StudioBrain. This is the Rust/WASM counterpart of the Python `hello-world` plugin and exercises the same capabilities through the Extism PDK.

## What This Plugin Demonstrates

| Capability | File | Description |
|-----------|------|-------------|
| Plugin manifest | `plugin.json` | Declares id, name, version, `"runtime": "wasm"`, capabilities, permissions, settings |
| WASM backend | `src/lib.rs` | Rust source compiled to `wasm32-wasip1` via Extism PDK |
| Entity hooks | `src/lib.rs` | `on_entity_save`, `on_entity_create`, `on_entity_delete`, `on_entity_validate` |
| HTTP routes | `src/lib.rs` | `list_routes`, `handle_request` — GET /hello, GET /stats, GET /status |
| Host functions | `src/lib.rs` | Reads settings and queries entities via Extism vars |
| Full-page dashboard | `frontend/pages/index.html` | Sandboxed iframe page linked from the sidebar nav |
| Sidebar panel | `frontend/panels/entity-notes.html` | Injected into the entity editor sidebar |
| Entity tab panel | `frontend/panels/entity-stats.html` | Injected as an extra tab in the entity editor |
| Settings schema | `plugin.json` | Configurable greeting message and event logging toggle |
| Build script | `build.sh` | One-command build and copy of `plugin.wasm` |

## Directory Structure

```
hello-world-wasm/
  plugin.json                         # Manifest (runtime: wasm)
  Cargo.toml                          # Rust project config
  build.sh                            # Build script
  README.md                           # This file
  src/
    lib.rs                            # All WASM exports (metadata, hooks, routes)
  frontend/
    pages/
      index.html                      # Full-page plugin dashboard
    panels/
      entity-notes.html               # Sidebar panel (entity-sidebar location)
      entity-stats.html               # Entity tab panel (entity-tab location)
  plugin.wasm                         # Built artefact (after running build.sh)
```

## Prerequisites

- **Rust** toolchain (1.70+): https://rustup.rs/
- **wasm32-wasip1** target:
  ```bash
  rustup target add wasm32-wasip1
  ```

## Building

```bash
# Release build (optimised + stripped, ~100-200 KB)
bash build.sh

# Debug build (fast iteration)
bash build.sh debug
```

The build script produces `plugin.wasm` in the plugin root directory.

## Installing

Copy the entire `hello-world-wasm/` directory (including `plugin.wasm`) into your StudioBrain project's `_Plugins/` directory:

```bash
cp -r hello-world-wasm /path/to/your/project/_Plugins/
```

Enable the plugin via the API or the Settings > Plugins UI.

## Backend Routes

All routes are auto-mounted at `/api/ext/hello-world-wasm/` by the plugin host:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/ext/hello-world-wasm/hello` | Greeting message (configurable via settings) |
| `GET` | `/api/ext/hello-world-wasm/stats` | Entity count from host query |
| `GET` | `/api/ext/hello-world-wasm/status` | Plugin health check |

## Entity Hooks

| Hook | Behaviour |
|------|----------|
| `on_entity_save` | Logs "Entity {type}/{id} was saved", passes data through unmodified |
| `on_entity_create` | Logs "New entity {type}/{id} created", passes data through unmodified |
| `on_entity_delete` | Logs "Entity {type}/{id} is being deleted", passes data through unmodified |
| `on_entity_validate` | Checks that the entity has a non-empty `name` field |
| `on_project_init` | Logs initialisation, returns success |

## Host Function Usage

The plugin communicates with the StudioBrain host through Extism vars:

- **Settings:** Reads `setting:greeting` var (host pre-populates from `settings_schema`)
- **Entity queries:** Writes filter to `host_call:query_entities`, reads result from `host_result:query_entities`

This pattern maps to the WIT host interfaces (`host-settings`, `host-entities`) defined in `studiobrain:plugin@0.1.0`.

## WIT Interface Alignment

The exported functions match the WIT interface in `core/packages/plugin-sdk/wit/plugin.wit`:

| WIT Export | Rust Function |
|-----------|--------------|
| `metadata::get-info` | `get_info` |
| `hooks::on-entity-save` | `on_entity_save` |
| `hooks::on-entity-create` | `on_entity_create` |
| `hooks::on-entity-delete` | `on_entity_delete` |
| `hooks::on-entity-validate` | `on_entity_validate` |
| `hooks::on-project-init` | `on_project_init` |
| `routes::list-routes` | `list_routes` |
| `routes::handle-request` | `handle_request` |

## Differences from the Python Version

| Aspect | Python (`hello-world`) | WASM (`hello-world-wasm`) |
|--------|----------------------|--------------------------|
| Runtime | Python (in-process) | WASM (sandboxed Extism) |
| Routes | FastAPI `APIRouter` | `handle_request` dispatch |
| Events | `event_bus.on("entity.*")` | Individual hook exports |
| Storage | Direct file I/O (`data/notes.json`) | Host-mediated via Extism vars |
| Security | Shares process memory | Memory-isolated WASM sandbox |
| Size | ~5 KB source | ~100-200 KB compiled `.wasm` |

## Using This as a Template

1. Copy `hello-world-wasm/` to a new directory under `_Plugins/`.
2. Update `plugin.json`: change `id`, `name`, `description`, `author`.
3. Update `Cargo.toml`: change `name`, `version`, `description`.
4. Edit `src/lib.rs`: replace the demo logic with your own hook and route handlers.
5. Edit the HTML files in `frontend/`: replace the demo UI.
6. Build: `bash build.sh`
7. Enable: `POST /api/plugins/{your-plugin-id}/enable`

For the full developer reference see `_Plugins/PLUGIN_DEVELOPMENT.md`.
