// StudioBrain Blender Bridge (WASM) WASM Plugin
//
// WASM port of the blender-bridge plugin. Exports:
//   metadata   -- get_info
//   hooks      -- on_entity_save, on_entity_create, on_project_init
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
        id: "blender-bridge-wasm".into(),
        name: "Blender Bridge (WASM)".into(),
        version: "0.2.0".into(),
        description: "Blender Bridge (WASM) -- WASM port".into(),
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
        "[blender-bridge-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[blender-bridge-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "blender-bridge-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Blender Bridge (WASM) ready.".into()],
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
            path: "/connection-status".into(),
            description: "Check Blender RPC connection".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/export-format".into(),
            description: "Get entity export format for Blender".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export".into(),
            description: "Export entity data to Blender".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/batch-export".into(),
            description: "Batch export entities to Blender".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/render-request".into(),
            description: "Queue a Blender render request".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/renders".into(),
            description: "List render history".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/export-log".into(),
            description: "View export log".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let port = get_setting("blender_port").unwrap_or_else(|| "8400".into());
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "blender-bridge-wasm",
                "runtime": "wasm",
                "blender_port": port,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/connection-status") => {
            let port = get_setting("blender_port").unwrap_or_else(|| "8400".into());
            let call = serde_json::json!({
                "url": format!("http://localhost:{}/api/status", port),
                "method": "GET",
            });
            var::set("host_call:http_fetch", &call.to_string())?;

            let connected = match var::get("host_result:http_fetch") {
                Ok(Some(bytes)) => {
                    let s = String::from_utf8(bytes).unwrap_or_default();
                    s.contains("ok")
                }
                _ => false,
            };

            let body = serde_json::json!({
                "connected": connected,
                "port": port,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/export") | ("POST", "/batch-export") | ("POST", "/render-request") => {
            let port = get_setting("blender_port").unwrap_or_else(|| "8400".into());
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            let call = serde_json::json!({
                "url": format!("http://localhost:{}/api/command", port),
                "method": "POST",
                "body": body_str,
            });
            var::set("host_call:http_fetch", &call.to_string())?;

            let result = match var::get("host_result:http_fetch") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "queued"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "queued"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/export-format") | ("GET", "/renders") | ("GET", "/export-log")
        | ("GET", "/exports") | ("GET", "/available-entities") => {
            let call_key = format!("host_call:blender:{}", req.path);
            var::set(&call_key, "")?;
            let result_key = format!("host_result:blender:{}", req.path);
            let result = match var::get(&result_key) {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => "{}".to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({}));
            Ok(Json(json_response(200, &body)))
        }
        _ => Ok(Json(not_found_response(&req.method, &req.path))),
    }
}
