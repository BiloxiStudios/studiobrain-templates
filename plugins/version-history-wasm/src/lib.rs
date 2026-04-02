// StudioBrain Version History (WASM) WASM Plugin
//
// WASM port of the version-history plugin. Exports:
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
        id: "version-history-wasm".into(),
        name: "Version History (WASM)".into(),
        version: "1.0.0".into(),
        description: "Version History (WASM) -- WASM port".into(),
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
        "[version-history-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[version-history-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_delete(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[version-history-wasm] Entity {}/{} deleted",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "version-history-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Version History (WASM) ready.".into()],
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
            path: "/history".into(),
            description: "Get commit history for an entity".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/diff".into(),
            description: "View diff at a specific commit".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/rollback".into(),
            description: "Rollback entity to a previous commit".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/stats".into(),
            description: "Repository-wide version statistics".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/file-at".into(),
            description: "View entity file at a specific commit".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let auto_commit = get_setting("auto_commit")
                .map(|v| v == "true")
                .unwrap_or(true);
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "version-history-wasm",
                "runtime": "wasm",
                "auto_commit": auto_commit,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/history") | ("GET", "/diff") | ("GET", "/stats")
        | ("GET", "/file-at") => {
            // Git operations are delegated to the host (git is not available in WASM)
            let call_key = format!("host_call:version:{}", req.path);
            let query: String = req.query_params.iter()
                .map(|kv| format!("{}={}", kv.key, kv.value))
                .collect::<Vec<_>>()
                .join("&");
            var::set(&call_key, &query)?;

            let result_key = format!("host_result:version:{}", req.path);
            let result = match var::get(&result_key) {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => "{}".to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({}));
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/rollback") => {
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();
            var::set("host_call:version:rollback", &body_str)?;

            let result = match var::get("host_result:version:rollback") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "rolling_back"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "rolling_back"}));
            Ok(Json(json_response(200, &body)))
        }
        _ => Ok(Json(not_found_response(&req.method, &req.path))),
    }
}
