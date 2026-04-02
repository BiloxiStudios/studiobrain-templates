// StudioBrain Unreal Engine Exporter (WASM) WASM Plugin
//
// WASM port of the unreal-exporter plugin. Exports:
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
        id: "unreal-exporter-wasm".into(),
        name: "Unreal Engine Exporter (WASM)".into(),
        version: "1.0.0".into(),
        description: "Unreal Engine Exporter (WASM) -- WASM port".into(),
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
        "[unreal-exporter-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[unreal-exporter-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "unreal-exporter-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Unreal Engine Exporter (WASM) ready.".into()],
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
            path: "/entity-types".into(),
            description: "List entity types for export".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/schema".into(),
            description: "Get export schema for a type".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/preview".into(),
            description: "Preview DataAsset for an entity".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/ustruct".into(),
            description: "Generate USTRUCT header for a type".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/datatable".into(),
            description: "Generate DataTable CSV for a type".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export".into(),
            description: "Export an entity as UE assets".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/batch-export".into(),
            description: "Batch export entities".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let project_path = get_setting("ue_project_path").unwrap_or_default();
            let api_url = get_setting("ue_rest_api_url").unwrap_or_default();
            let module = get_setting("module_name")
                .unwrap_or_else(|| "CityOfBrains".into());
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "unreal-exporter-wasm",
                "runtime": "wasm",
                "project_path": project_path,
                "remote_control_url": api_url,
                "module_name": module,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/export") | ("POST", "/batch-export") => {
            let api_url = get_setting("ue_rest_api_url").unwrap_or_default();
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            // If Remote Control API is configured, push via HTTP
            if !api_url.is_empty() {
                let call = serde_json::json!({
                    "url": format!("{}/remote/object/call", api_url),
                    "method": "POST",
                    "body": body_str,
                });
                var::set("host_call:http_fetch", &call.to_string())?;
            }

            let call_key = format!("host_call:unreal:{}", req.path);
            var::set(&call_key, &body_str)?;

            let result_key = format!("host_result:unreal:{}", req.path);
            let result = match var::get(&result_key) {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "exporting"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "exporting"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/entity-types") | ("GET", "/schema") | ("GET", "/preview")
        | ("GET", "/ustruct") | ("GET", "/datatable") => {
            let call_key = format!("host_call:unreal:{}", req.path);
            var::set(&call_key, "")?;
            let result_key = format!("host_result:unreal:{}", req.path);
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
