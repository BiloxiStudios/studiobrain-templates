// StudioBrain ComfyUI Workflow Manager (WASM) WASM Plugin
//
// WASM port of the comfyui-workflows plugin. Exports:
//   metadata   -- get_info
//   hooks      -- on_entity_save, on_project_init
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
        id: "comfyui-workflows-wasm".into(),
        name: "ComfyUI Workflow Manager (WASM)".into(),
        version: "0.2.0".into(),
        description: "ComfyUI Workflow Manager (WASM) -- WASM port".into(),
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
        "[comfyui-workflows-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "comfyui-workflows-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["ComfyUI Workflow Manager (WASM) ready.".into()],
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
            description: "Plugin health check with ComfyUI connection".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/workflows".into(),
            description: "List available workflows".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/workflows/detail".into(),
            description: "Get a specific workflow".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/import".into(),
            description: "Import a workflow JSON".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/execute".into(),
            description: "Queue a workflow execution".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/queue".into(),
            description: "Get ComfyUI queue status".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/history".into(),
            description: "Execution history".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/outputs".into(),
            description: "Get generated outputs for an entity".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let comfy_url = get_setting("comfyui_url")
                .unwrap_or_else(|| "http://localhost:8188".into());

            // Check ComfyUI connectivity via host-http::fetch
            let call = serde_json::json!({
                "url": format!("{}/system_stats", comfy_url),
                "method": "GET",
            });
            var::set("host_call:http_fetch", &call.to_string())?;

            let connected = match var::get("host_result:http_fetch") {
                Ok(Some(bytes)) => {
                    let s = String::from_utf8(bytes).unwrap_or_default();
                    !s.is_empty() && !s.contains("error")
                }
                _ => false,
            };

            let body = serde_json::json!({
                "status": "ok",
                "plugin": "comfyui-workflows-wasm",
                "runtime": "wasm",
                "comfyui_url": comfy_url,
                "comfyui_connected": connected,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/execute") => {
            let comfy_url = get_setting("comfyui_url")
                .unwrap_or_else(|| "http://localhost:8188".into());
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            let call = serde_json::json!({
                "url": format!("{}/prompt", comfy_url),
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
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
        ("GET", "/workflows") | ("GET", "/workflows/detail") | ("POST", "/import")
        | ("GET", "/queue") | ("GET", "/history") | ("GET", "/outputs") => {
            let comfy_url = get_setting("comfyui_url")
                .unwrap_or_else(|| "http://localhost:8188".into());
            let call_key = format!("host_call:comfyui:{}", req.path);
            var::set(&call_key, &comfy_url)?;

            let result_key = format!("host_result:comfyui:{}", req.path);
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
