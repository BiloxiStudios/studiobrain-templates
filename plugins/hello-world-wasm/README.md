# Hello World WASM Plugin — SBAI-6815 Migration Proof of Concept

WASM component version of the legacy `hello-world` plugin.

## What Changed (FastAPI → WASM)

| Legacy (FastAPI) | WASM Component |
|-----------------|----------------|
| `@router.get("/notes")` | `handle_request()` with method/path routing |
| `pathlib` + JSON file I/O | `host_abi.kv_set/get/delete` |
| `event_bus.on("entity.*")` | `on_entity_save/create/delete` hooks |
| `pydantic` models | Manual JSON parsing |
| `logging.getLogger()` | `log.log(level, message)` |

## Build

```bash
chmod +x build.sh && ./build.sh
```

Requires `pip install componentize-py`.

## Install

Copy `plugin.json` + `plugin.wasm` to StudioBrain plugins directory.

See `../MIGRATION_PLAN.md` for the full migration strategy.
