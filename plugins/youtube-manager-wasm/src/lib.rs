// StudioBrain YouTube Manager (WASM) WASM Plugin
//
// WASM port of the youtube-manager plugin. Exports:
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
        id: "youtube-manager-wasm".into(),
        name: "YouTube Manager (WASM)".into(),
        version: "0.2.0".into(),
        description: "YouTube Manager (WASM) -- WASM port".into(),
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
        "[youtube-manager-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "youtube-manager-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["YouTube Manager (WASM) ready.".into()],
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
            method: "POST".into(),
            path: "/upload".into(),
            description: "Upload a video to YouTube".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/videos".into(),
            description: "List all managed videos".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/videos/entity".into(),
            description: "List videos for an entity".into(),
        },
        RouteDescriptor {
            method: "PUT".into(),
            path: "/videos".into(),
            description: "Update video metadata".into(),
        },
        RouteDescriptor {
            method: "DELETE".into(),
            path: "/videos".into(),
            description: "Delete a video".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/generate-metadata".into(),
            description: "Generate metadata from entity data".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/asset-videos".into(),
            description: "List asset videos for an entity".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/categories".into(),
            description: "List YouTube video categories".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let has_key = get_setting("youtube_api_key").is_some();
            let channel = get_setting("channel_id").unwrap_or_default();
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "youtube-manager-wasm",
                "runtime": "wasm",
                "api_key_configured": has_key,
                "channel_id": channel,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/categories") => {
            let body = serde_json::json!({
                "categories": [
                    {"id": "20", "name": "Gaming"},
                    {"id": "24", "name": "Entertainment"},
                    {"id": "1", "name": "Film & Animation"},
                    {"id": "22", "name": "People & Blogs"},
                ]
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/upload") | ("PUT", "/videos") | ("DELETE", "/videos")
        | ("POST", "/generate-metadata") => {
            let api_key = get_setting("youtube_api_key").unwrap_or_default();
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            let call = serde_json::json!({
                "url": "https://www.googleapis.com/youtube/v3/videos",
                "method": req.method,
                "headers": {"Authorization": format!("Bearer {}", api_key)},
                "body": body_str,
            });
            var::set("host_call:http_fetch", &call.to_string())?;

            let result = match var::get("host_result:http_fetch") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "processing"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "processing"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/videos") | ("GET", "/videos/entity") | ("GET", "/asset-videos") => {
            let call_key = format!("host_call:youtube:{}", req.path);
            var::set(&call_key, "")?;
            let result_key = format!("host_result:youtube:{}", req.path);
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
