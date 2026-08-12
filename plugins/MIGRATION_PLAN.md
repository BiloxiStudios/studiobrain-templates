# Plugin Migration Plan: Python FastAPI → WASM Components

**Ticket:** SBAI-6815  
**Date:** 2026-08-12  
**Status:** Plan v1.0 — awaiting approval  

## Problem Statement

All 28 published template plugins target the decommissioned Python FastAPI backend (`from fastapi import APIRouter`). The current production `sb-server` (Rust/Axum) only loads `.wasm` plugin entry points via the `sb-plugin-wasmtime` crate using wasmtime's Component Model with a WIT interface (`studiobrain:plugin@1.0.0`).

**Net effect:** As currently published, these 28 plugins cannot run against the current production backend.

## Target Architecture

Plugins are now WASM components compiled from:
- **Rust** (native, recommended for performance)
- **Python** (via `componentize-py`, Bytecode Alliance's CPython-to-Wasm-Component compiler)
- **JavaScript/TypeScript** (via `componentize-js`)
- **Go, C/C++** (via WIT-compatible toolchains)

The WIT interface (`/core/wit/studiobrain-plugin.wit`) defines:
- **Host imports:** `log`, `host-abi` (entity CRUD, KV store, event emission)
- **Plugin exports:** `metadata` (required), `hooks` (optional), `routes` (optional)

## Plugin Audit Results

Total: **28 plugins**, **~19,254 lines of Python backend code**, **52 `.py` files**

### Bucket A — Straightforward Migration (~18 plugins, ~10k lines)

Pure CRUD/hooks/transform against host-entities/host-settings, no exotic dependencies. These plugins use only:
- File-based JSON storage (`pathlib`, `json`)
- Basic FastAPI routes with `pydantic` models
- Entity event handlers (`event_bus.on(...)`)
- No external API calls, no C extensions, no async streams

| Plugin | Lines (routes+events) | Type | Notes |
|--------|----------------------|------|-------|
| hello-world | 145 | full | Reference implementation, notes CRUD |
| entity-validator | 415 | full | Validation rules, no exotic deps |
| kanban-board | 455 | full | Board state as JSON, entity hooks |
| time-tracker | 471 | full | Time entries, file-based storage |
| data-notes | 0 | frontend-only | No Python backend — already WASM-ready |
| prompt-engine | 430 | full | Prompt templates, settings |
| comfyui-workflows | 736 | full | Workflow JSON storage |
| discord-poster | 529 | full | Webhook calls (standard HTTP) |
| webhook-automations | 639 | full | HTTP webhook handlers |
| pdf-exporter | 1494 | full | Template rendering, no external deps |
| assembly-composer | 542 | full | Assembly state management |
| obsidian-vault | 574 | full | Markdown sync, file I/O |
| unity-exporter | 1041 | full | Export pipeline |
| unreal-exporter | 700 | full | Export pipeline |
| uefn-exporter | 826 | full | Export pipeline |
| blender-bridge | 909 | full | Bridge communication |
| youtube-manager | 415 | full | Video metadata management |
| import-export-pipeline | 1183 | full | Data import/export |

### Bucket B — Uncertain (~7 plugins, ~5k lines)

External OAuth flows or async/streaming needs the WIT interface may not cover yet. These plugins use:
- OAuth token refresh flows
- Streaming response patterns
- Long-running async operations

| Plugin | Lines | Blockers |
|--------|-------|----------|
| jira-sync | 737 | OAuth flow, periodic sync scheduling |
| notion-sync | 743 | OAuth flow, API rate limiting |
| google-sheets-sync | 756 | OAuth flow, Google API deps |
| social-publisher | 922 | Multiple OAuth providers |
| voice-forge | 412 | Audio processing, streaming |
| music-gen | 690 | Audio generation, long-running |
| showrunner-exporter | 977 | Complex pipeline, streaming |

**Resolution:** Requires WIT interface review and potential extension for OAuth token management and streaming host capabilities.

### Bucket C — Hard/Blocked (~3 plugins, ~3k lines)

Plugins that fundamentally cannot work in a WASM sandbox without new host capabilities.

| Plugin | Lines | Blocker | Workaround |
|--------|-------|---------|------------|
| version-history | 471 | `subprocess` calls to `git` | New host-git capability OR wasm-native git library |
| comparison | 480 | `subprocess` calls to `git` | Same as version-history |
| lora-trainer | 805 | Real-time GPU job streaming | New host-ai streaming interface |

**Resolution:** These require new host capabilities to be added to the WIT interface before migration is possible.

### Frontend-Only Plugins (No Migration Needed)

| Plugin | Type | Status |
|--------|------|--------|
| data-notes | frontend-only | Already WASM-ready — calls generic CRUD API from JS |
| entity-validator | full (has backend) | Backend needs migration |

## Migration Strategy

### Phase 1: Proof of Concept (this ticket)

- [x] Audit all 28 plugins and categorize
- [ ] Build hello-world as WASM plugin via componentize-py
- [ ] Verify build pipeline works end-to-end
- [ ] Document the migration pattern

### Phase 2: Batch A Migration (separate tickets)

Migrate the 18 straightforward plugins using the proven pattern from Phase 1. Each plugin gets its own ticket for parallel work.

### Phase 3: WIT Interface Extension (separate tickets)

Add host capabilities needed for Bucket B plugins:
- OAuth token storage and refresh
- Streaming response support
- Scheduled task/cron interface

### Phase 4: Bucket C Resolution (separate tickets)

Design and implement host capabilities for:
- Git operations (version-history, comparison)
- GPU job streaming (lora-trainer)

## Migration Pattern (Python → WASM)

### Before (Legacy FastAPI)

```python
# backend/routes.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/notes")
async def get_notes(entity_type: str, entity_id: str):
    data = _read_data()
    return {"notes": data.get(f"{entity_type}:{entity_id}", [])}
```

### After (WASM Component)

```python
# plugin.py
from plugin import exports
from plugin.imports import host_abi, log
from plugin.imports.types import PluginInfo, HookEvent, HookResult, HttpRequest, HttpResponse

class Metadata(exports.Metadata):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            id="hello-world",
            name="Hello World",
            version="1.0.0",
            description="Reference plugin with entity notes",
        )

class Hooks(exports.Hooks):
    def on_entity_save(self, event: HookEvent) -> HookResult:
        log.log(log.Level.INFO, f"Entity save: {event.entity_type}")
        return HookResult(modified_data=None, messages=[])

class Routes(exports.Routes):
    def list_routes(self):
        return [RouteDescriptor(method="GET", path="/notes", description="List notes")]

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET" and request.path == "/notes":
            # Use host-abi for entity access, kv-set/kv-get for storage
            ...
```

### Key Differences

| Aspect | Legacy FastAPI | WASM Component |
|--------|---------------|----------------|
| Routes | `@router.get("/path")` decorators | `handle_request()` with manual routing |
| Storage | `pathlib` + `json` file I/O | `host_abi.kv_set/get/delete` |
| Entities | Direct DB access via services | `host_abi.get_entity/list_entity_ids` |
| Events | `event_bus.on("pattern")` | `on_entity_save/create/delete/validate` hooks |
| Logging | `logging.getLogger()` | `host_log.log(level, message)` |
| Settings | `get_all_settings()` service | `host_settings.get_setting()` (future WIT extension) |
| HTTP calls | `httpx` / `requests` | `host_http.fetch()` (future WIT extension) |
| Models | `pydantic` BaseModel | Manual JSON parsing in `handle_request` |

## Build Instructions (Python WASM Plugin)

```bash
# Prerequisites
pip install componentize-py

# Generate bindings
componentize-py --wit-path ./wit --world plugin bindings .

# Build WASM component
componentize-py --wit-path ./wit --world plugin componentize plugin.py -o plugin.wasm

# Install
cp plugin.json plugin.wasm /path/to/studiobrain/plugins/hello-world/
```

## Risks and Caveats

1. **componentize-py unproven**: No plugin has actually been compiled this way yet in this codebase. The template exists but hasn't been exercised end-to-end.

2. **Binary size**: WASM components from Python will be larger (2-10MB) than native Rust plugins (~100KB) due to embedded CPython runtime.

3. **Cold start**: Python WASM plugins will have slower cold-start times than Rust due to interpreter initialization.

4. **No C extensions**: Any Python C extensions (numpy, PIL, etc.) require wasm32-wasi builds. Audit confirmed zero numpy/pandas/PIL/torch/cv2 usage across all 28 plugins.

5. **WIT interface gaps**: The current WIT interface doesn't cover OAuth token management, streaming responses, or external HTTP fetch — these will need to be added for Bucket B plugins.

## Recommendations

1. **Prove the pipeline first**: Migrate 1-2 Bucket A plugins end-to-end before committing to the full migration. This will surface any componentize-py issues early.

2. **Parallelize after proof**: Once the pattern is proven, each Bucket A plugin can be migrated independently by separate workers.

3. **Preserve frontend HTML**: The frontend HTML panels/pages don't need changes — they call the same REST API paths. Only the backend Python code needs rewriting.

4. **Consider Rust for complex plugins**: For plugins with complex logic (>500 lines), Rust may be a better target than Python due to smaller binary size and faster startup.
