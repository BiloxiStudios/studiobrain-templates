// StudioBrain LoRA Training Manager (WASM) WASM Plugin
//
// WASM port of the lora-trainer plugin. Exports:
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
        id: "lora-trainer-wasm".into(),
        name: "LoRA Training Manager (WASM)".into(),
        version: "0.2.0".into(),
        description: "LoRA Training Manager (WASM) -- WASM port".into(),
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
        "[lora-trainer-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "lora-trainer-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["LoRA Training Manager (WASM) ready.".into()],
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
            description: "Plugin health check with GPU status".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/datasets".into(),
            description: "List training datasets for an entity".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/datasets/prepare".into(),
            description: "Prepare a training dataset".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/datasets/captions".into(),
            description: "Generate captions for images".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/train".into(),
            description: "Queue a LoRA training job".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/jobs".into(),
            description: "List training jobs".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/jobs/detail".into(),
            description: "Get details of a training job".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/jobs/cancel".into(),
            description: "Cancel a training job".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/loras".into(),
            description: "List completed LoRA files".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/gpu-status".into(),
            description: "Get GPU utilization info".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let output_dir = get_setting("output_dir").unwrap_or_default();
            let gpu_id = get_setting("gpu_id").unwrap_or_else(|| "0".into());
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "lora-trainer-wasm",
                "runtime": "wasm",
                "output_dir": output_dir,
                "gpu_id": gpu_id,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/train") => {
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();
            var::set("host_call:lora_train", &body_str)?;

            let result = match var::get("host_result:lora_train") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "queued"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "queued"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/datasets") | ("POST", "/datasets/prepare") | ("POST", "/datasets/captions")
        | ("GET", "/jobs") | ("GET", "/jobs/detail") | ("POST", "/jobs/cancel")
        | ("DELETE", "/jobs") | ("GET", "/loras") | ("GET", "/gpu-status") => {
            let call_key = format!("host_call:lora:{}", req.path);
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();
            var::set(&call_key, &body_str)?;

            let result_key = format!("host_result:lora:{}", req.path);
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
