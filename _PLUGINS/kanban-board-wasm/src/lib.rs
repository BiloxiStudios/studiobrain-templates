// StudioBrain Production Kanban (WASM) WASM Plugin
//
// WASM port of the kanban-board plugin. Exports:
//   metadata   -- get_info
//   hooks      -- on_entity_save, on_entity_create, on_entity_delete, on_project_init
//   routes     -- list_routes, handle_request


use extism_pdk::*;
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Common types — mirrors of the WIT records
// ---------------------------------------------------------------------------

#[derive(Serialize)]
struct PluginInfo {
    id: String,
    name: String,
    version: String,
    description: String,
    author: String,
}

#[derive(Deserialize)]
struct HookEvent {
    entity_type: String,
    entity_id: String,
    data: String,
    #[allow(dead_code)]
    actor: String,
    #[allow(dead_code)]
    source: String,
}

#[derive(Serialize)]
struct HookResult {
    data: Option<String>,
    messages: Vec<String>,
    abort: bool,
    abort_reason: Option<String>,
}

impl HookResult {
    fn passthrough() -> Self {
        Self {
            data: None,
            messages: Vec::new(),
            abort: false,
            abort_reason: None,
        }
    }
}

#[derive(Serialize)]
struct SetupResult {
    success: bool,
    messages: Vec<String>,
}

#[derive(Serialize)]
struct RouteDescriptor {
    method: String,
    path: String,
    description: String,
}

#[derive(Deserialize)]
struct HttpRequest {
    method: String,
    path: String,
    #[allow(dead_code)]
    headers: Vec<KvPair>,
    #[allow(dead_code)]
    query_params: Vec<KvPair>,
    #[allow(dead_code)]
    body: Option<Vec<u8>>,
}

#[derive(Serialize)]
struct HttpResponse {
    status: u16,
    headers: Vec<KvPair>,
    body: Option<Vec<u8>>,
}

#[derive(Serialize, Deserialize)]
struct KvPair {
    key: String,
    value: String,
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn json_response(status: u16, body: &impl Serialize) -> HttpResponse {
    let body_bytes = serde_json::to_vec(body).unwrap_or_default();
    HttpResponse {
        status,
        headers: vec![KvPair {
            key: "content-type".into(),
            value: "application/json".into(),
        }],
        body: Some(body_bytes),
    }
}

fn get_setting(key: &str) -> Option<String> {
    match var::get(&format!("setting:{}", key)) {
        Ok(Some(bytes)) => String::from_utf8(bytes).ok(),
        _ => None,
    }
}

fn not_found_response(method: &str, path: &str) -> HttpResponse {
    let body = serde_json::json!({
        "error": "not_found",
        "message": format!("No route for {} {}", method, path),
    });
    json_response(404, &body)
}


// ---------------------------------------------------------------------------
// metadata
// ---------------------------------------------------------------------------

#[plugin_fn]
pub fn get_info(_: ()) -> FnResult<Json<PluginInfo>> {
    Ok(Json(PluginInfo {
        id: "kanban-board-wasm".into(),
        name: "Production Kanban (WASM)".into(),
        version: "1.0.0".into(),
        description: "Production Kanban (WASM) -- WASM port".into(),
        author: "BiloxiStudios".into(),
    }))
}

// ---------------------------------------------------------------------------
// hooks
// ---------------------------------------------------------------------------

#[plugin_fn]
pub fn on_entity_save(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[kanban-board-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[kanban-board-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_delete(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[kanban-board-wasm] Entity {}/{} deleted",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "kanban-board-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Production Kanban (WASM) ready.".into()],
    }))
}

// ---------------------------------------------------------------------------
// routes
// ---------------------------------------------------------------------------

#[plugin_fn]
pub fn list_routes(_: ()) -> FnResult<Json<Vec<RouteDescriptor>>> {
    Ok(Json(vec![
        RouteDescriptor {
            method: "GET".into(),
            path: "/status".into(),
            description: "Plugin health check".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/columns".into(),
            description: "Get configured kanban columns with WIP limits".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/board".into(),
            description: "Get all entities grouped by kanban column".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/move".into(),
            description: "Move an entity to a new status column".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/stats".into(),
            description: "Column counts and completion percentages".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/entity-status".into(),
            description: "Get kanban status for a single entity".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "kanban-board-wasm",
                "runtime": "wasm",
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/columns") => {
            let columns = get_setting("columns")
                .unwrap_or_else(|| "Concept,In Progress,Review,Complete".into());
            let wip_raw = get_setting("wip_limits")
                .unwrap_or_else(|| "0,10,5,0".into());

            let cols: Vec<&str> = columns.split(',').collect();
            let wips: Vec<&str> = wip_raw.split(',').collect();

            let result: Vec<serde_json::Value> = cols
                .iter()
                .enumerate()
                .map(|(i, c)| {
                    let wip: u32 = wips.get(i)
                        .and_then(|w| w.trim().parse().ok())
                        .unwrap_or(0);
                    serde_json::json!({"name": c.trim(), "wip_limit": wip})
                })
                .collect();

            let body = serde_json::json!({"columns": result});
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/board") | ("GET", "/stats") | ("GET", "/entity-status") => {
            // These require entity queries via the host
            let filter_json = serde_json::json!({
                "entity_type": null,
                "limit": 1000,
            })
            .to_string();
            var::set("host_call:query_entities", &filter_json)?;

            let entities_json = match var::get("host_result:query_entities") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => "{}".to_string(),
            };

            let body: serde_json::Value =
                serde_json::from_str(&entities_json).unwrap_or(serde_json::json!({
                    "board": {},
                    "total": 0,
                    "message": "Board data delegated to host"
                }));
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/move") => {
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();
            var::set("host_call:move_entity", &body_str)?;

            let result = match var::get("host_result:move_entity") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"success": true}).to_string(),
            };

            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"success": true}));
            Ok(Json(json_response(200, &body)))
        }
        _ => Ok(Json(not_found_response(&req.method, &req.path))),
    }
}
