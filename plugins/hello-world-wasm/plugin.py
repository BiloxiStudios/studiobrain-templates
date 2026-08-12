"""Hello World WASM Plugin — SBAI-6815 Migration Proof of Concept

This module implements the studiobrain:plugin/plugin@1.0.0 WIT world
using componentize-py. It demonstrates the migration pattern from the
legacy FastAPI hello-world plugin to the WASM component model.

Legacy (FastAPI):
  - backend/routes.py: @router.get("/notes"), @router.post("/notes"), etc.
  - backend/events.py: event_bus.on("entity.*") handlers

WASM Component:
  - Metadata: get_info() → PluginInfo
  - Hooks: on_entity_save/create/delete → HookResult
  - Routes: list_routes() + handle_request() → HttpRequest/HttpResponse

Build: ./build.sh
Output: plugin.wasm
"""

import json
from plugin import exports
from plugin.imports import log, host_abi
from plugin.imports.types import (
    PluginInfo,
    HookEvent,
    HookResult,
    RouteDescriptor,
    HttpRequest,
    HttpResponse,
    Tuple2,
)


def _log(level: str, message: str) -> None:
    log.log(level, message)


def _kv_key(entity_type: str, entity_id: str) -> str:
    return f"notes:{entity_type}:{entity_id}"


def _read_notes(entity_type: str, entity_id: str) -> list:
    key = _kv_key(entity_type, entity_id)
    value = host_abi.kv_get(key)
    if value is None:
        return []
    return json.loads(value)


def _write_notes(entity_type: str, entity_id: str, notes: list) -> None:
    key = _kv_key(entity_type, entity_id)
    host_abi.kv_set(key, json.dumps(notes))


def _http_response(status: int, body: dict, content_type: str = "application/json") -> HttpResponse:
    return HttpResponse(
        status=status,
        headers=[Tuple2("content-type", content_type)],
        body=json.dumps(body),
    )


def _error_response(status: int, detail: str) -> HttpResponse:
    return _http_response(status, {"error": detail})


class Metadata(exports.Metadata):
    """Plugin identity — required for all plugins."""

    def get_info(self) -> PluginInfo:
        return PluginInfo(
            id="hello-world-wasm",
            name="Hello World (WASM)",
            version="2.0.0",
            description="Reference plugin migrated to WASM. Demonstrates entity notes CRUD via KV store.",
        )


class Hooks(exports.Hooks):
    """Entity lifecycle hooks. Maps to legacy events.py register_handlers()."""

    def on_entity_save(self, event: HookEvent) -> HookResult:
        entity_type = event.entity_type or "unknown"
        _log("info", f"[hello-world-wasm] Entity save: {entity_type}")
        return HookResult(modified_data=None, messages=[])

    def on_entity_create(self, event: HookEvent) -> HookResult:
        entity_type = event.entity_type or "unknown"
        _log("info", f"[hello-world-wasm] Entity created: {entity_type}")
        return HookResult(modified_data=None, messages=[])

    def on_entity_delete(self, event: HookEvent) -> HookResult:
        entity_type = event.entity_type or "unknown"
        _log("info", f"[hello-world-wasm] Entity deleted: {entity_type}")
        return HookResult(modified_data=None, messages=[])


class Routes(exports.Routes):
    """HTTP route handling — mounted under /api/ext/hello-world-wasm/.

    Maps to legacy FastAPI @router decorators. Plugin must manually route
    based on request.method and request.path.
    """

    def list_routes(self) -> list:
        return [
            RouteDescriptor(method="GET", path="/status", description="Plugin health check"),
            RouteDescriptor(method="GET", path="/notes", description="List notes for an entity"),
            RouteDescriptor(method="POST", path="/notes", description="Add a note to an entity"),
            RouteDescriptor(method="DELETE", path="/notes", description="Delete a note by ID"),
        ]

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        path = request.path.split("?")[0]
        query_string = ""
        if "?" in request.path:
            query_string = request.path.split("?", 1)[1]

        if request.method == "GET" and path == "/status":
            return _http_response(200, {"status": "ok", "plugin": "hello-world-wasm", "runtime": "wasm"})

        if request.method == "GET" and path == "/notes":
            params = _parse_query(query_string)
            entity_type = params.get("entity_type")
            entity_id = params.get("entity_id")
            if not entity_type or not entity_id:
                return _error_response(400, "entity_type and entity_id are required")
            return _http_response(200, {"notes": _read_notes(entity_type, entity_id)})

        if request.method == "POST" and path == "/notes":
            if request.body is None:
                return _error_response(400, "Request body is required")
            try:
                body = json.loads(request.body)
            except (json.JSONDecodeError, ValueError):
                return _error_response(400, "Invalid JSON body")
            entity_type = body.get("entity_type")
            entity_id = body.get("entity_id")
            text = body.get("text", "")
            if not entity_type or not entity_id:
                return _error_response(400, "entity_type and entity_id are required")
            if not text.strip():
                return _error_response(400, "Note text cannot be empty")
            notes = _read_notes(entity_type, entity_id)
            note_id = f"note-{len(notes) + 1}"
            note = {"id": note_id, "text": text.strip()}
            notes.insert(0, note)
            _write_notes(entity_type, entity_id, notes)
            return _http_response(201, note)

        if request.method == "DELETE" and path == "/notes":
            params = _parse_query(query_string)
            entity_type = params.get("entity_type")
            entity_id = params.get("entity_id")
            note_id = params.get("note_id")
            if not entity_type or not entity_id or not note_id:
                return _error_response(400, "entity_type, entity_id, and note_id are required")
            notes = _read_notes(entity_type, entity_id)
            original_len = len(notes)
            notes = [n for n in notes if n.get("id") != note_id]
            if len(notes) == original_len:
                return _error_response(404, "Note not found")
            _write_notes(entity_type, entity_id, notes)
            return _http_response(200, {"deleted": note_id})

        return _error_response(404, f"Route not found: {request.method} {request.path}")


def _parse_query(query_string: str) -> dict:
    params = {}
    if not query_string:
        return params
    for pair in query_string.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value
    return params
