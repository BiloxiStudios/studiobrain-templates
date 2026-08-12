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

The WIT interface (`core/wit/studiobrain-plugin.wit`) defines:
- **Host imports:** `log`, `host-abi` (entity CRUD, KV store, event emission)
- **Plugin exports:** `metadata` (required), `hooks` (optional), `routes` (optional)

## Plugin Audit Results

Total: **28 plugins**, **~19,254 lines of Python backend code**, **52 `.py` files**

### Bucket A — Straightforward Migration (~18 plugins, ~10k lines)

Pure CRUD/hooks/transform against host-entities/host-settings, no exotic dependencies.

| Plugin | Lines | Type | Notes |
|--------|-------|------|-------|
| hello-world | 145 | full | Reference implementation, notes CRUD |
| entity-validator | 415 | full | Validation rules |
| kanban-board | 455 | full | Board state as JSON |
| time-tracker | 471 | full | Time entries, file storage |
| data-notes | 0 | frontend-only | No Python — WASM-ready |
| prompt-engine | 430 | full | Prompt templates |
| comfyui-workflows | 736 | full | Workflow JSON |
| discord-poster | 529 | full | Webhook HTTP calls |
| webhook-automations | 639 | full | HTTP handlers |
| pdf-exporter | 1494 | full | Template rendering |
| assembly-composer | 542 | full | Assembly state |
| obsidian-vault | 574 | full | Markdown sync |
| unity-exporter | 1041 | full | Export pipeline |
| unreal-exporter | 700 | full | Export pipeline |
| uefn-exporter | 826 | full | Export pipeline |
| blender-bridge | 909 | full | Bridge communication |
| youtube-manager | 415 | full | Video metadata |
| import-export-pipeline | 1183 | full | Data import/export |

### Bucket B — Uncertain (~7 plugins, ~5k lines)

External OAuth flows or async/streaming needs.

| Plugin | Lines | Blockers |
|--------|-------|----------|
| jira-sync | 737 | OAuth, periodic sync |
| notion-sync | 743 | OAuth, rate limiting |
| google-sheets-sync | 756 | OAuth, Google API deps |
| social-publisher | 922 | Multiple OAuth providers |
| voice-forge | 412 | Audio streaming |
| music-gen | 690 | Audio generation |
| showrunner-exporter | 977 | Complex pipeline, streaming |

### Bucket C — Hard/Blocked (~3 plugins, ~3k lines)

| Plugin | Lines | Blocker |
|--------|-------|---------|
| version-history | 471 | `subprocess` calls to `git` |
| comparison | 480 | `subprocess` calls to `git` |
| lora-trainer | 805 | Real-time GPU job streaming |

## Migration Strategy

### Phase 1: Proof of Concept (this ticket)
- Build hello-world as WASM plugin via componentize-py
- Verify build pipeline works end-to-end
- Document the migration pattern

### Phase 2: Batch A Migration (separate tickets)
Migrate 18 straightforward plugins using proven pattern.

### Phase 3: WIT Interface Extension (separate tickets)
Add host capabilities for OAuth, streaming, scheduled tasks.

### Phase 4: Bucket C Resolution (separate tickets)
Design host capabilities for git operations and GPU streaming.

## Build Instructions (Python WASM Plugin)

```bash
pip install componentize-py
componentize-py --wit-path ./wit --world plugin bindings .
componentize-py --wit-path ./wit --world plugin componentize plugin.py -o plugin.wasm
```

## Risks

1. **componentize-py unproven**: No plugin compiled this way yet in this codebase
2. **Binary size**: Python WASM ~2-10MB vs Rust ~100KB
3. **Cold start**: Slower than Rust due to interpreter init
4. **No C extensions**: numpy/pandas/etc. require wasm32-wasi builds (audit confirmed zero usage)
5. **WIT gaps**: No OAuth, streaming, or external HTTP fetch in current interface
