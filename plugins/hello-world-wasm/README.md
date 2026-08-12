# Hello World WASM Plugin — SBAI-6815 Migration Proof of Concept

This is a **WASM component** version of the legacy `hello-world` plugin, created as a proof-of-concept for SBAI-6815.

## What Changed (FastAPI → WASM)

| Legacy (FastAPI) | WASM Component |
|-----------------|----------------|
| `@router.get("/notes")` | `handle_request()` with method/path routing |
| `pathlib` + JSON file I/O | `host_abi.kv_set/get/delete` |
| `event_bus.on("entity.*")` | `on_entity_save/create/delete` hooks |
| `pydantic` models | Manual JSON parsing |
| `logging.getLogger()` | `log.log(level, message)` |

## File Structure

```
hello-world-wasm/
  plugin.json       # Manifest with "runtime": "wasm"
  plugin.py         # WASM component implementation (replaces backend/)
  build.sh          # Build script using componentize-py
  README.md         # This file
  wit/              # WIT interface files (copied from core/wit/)
  plugin.wasm       # Built WASM component (after build)
```

## Build

```bash
chmod +x build.sh
./build.sh
```

Requires `pip install componentize-py`.

## Install

Copy `plugin.json` and `plugin.wasm` to your StudioBrain plugins directory. The host loads `.wasm` entry points via the `sb-plugin-wasmtime` runtime.

## Architecture

This plugin implements three WIT exports:

1. **Metadata** — `get_info()` returns plugin identity
2. **Hooks** — `on_entity_save/create/delete` log entity lifecycle events
3. **Routes** — `handle_request()` handles HTTP requests for notes CRUD

The host provides two imports:

1. **log** — Structured logging routed through the host
2. **host-abi** — Entity CRUD, KV store, event emission

## Migration Pattern

See `../MIGRATION_PLAN.md` for the full migration strategy covering all 28 plugins.

### Key Mapping

```
Legacy FastAPI          →  WASM Component
─────────────────────────────────────────────
@router.get("/x")       →  if method=="GET" and path=="/x" in handle_request()
event_bus.on("pattern") →  on_entity_save/create/delete/validate hooks
data/notes.json         →  host_abi.kv_set/kv_get with "notes:" prefix keys
logging.getLogger()     →  log.log(level, message)
pydantic BaseModel      →  Manual json.loads() in handle_request()
```

## Testing

The frontend HTML panels from the original `hello-world` plugin remain unchanged — they call the same REST API endpoints (`/api/ext/hello-world-wasm/notes`). Only the backend implementation changes from Python FastAPI to WASM component.
