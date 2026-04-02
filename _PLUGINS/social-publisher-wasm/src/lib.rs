// StudioBrain Social Publisher (WASM) WASM Plugin
//
// WASM port of the social-publisher plugin. Exports:
//   metadata   -- get_info
//   hooks      -- on_entity_create, on_entity_save, on_project_init
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
        id: "social-publisher-wasm".into(),
        name: "Social Publisher (WASM)".into(),
        version: "0.2.0".into(),
        description: "Social Publisher (WASM) -- WASM port".into(),
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
        "[social-publisher-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[social-publisher-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "social-publisher-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Social Publisher (WASM) ready.".into()],
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
            description: "Plugin health check with platform status".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/publish".into(),
            description: "Publish entity to social platforms".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/templates".into(),
            description: "List post templates".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/templates/preview".into(),
            description: "Preview a post template".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/history".into(),
            description: "View publish history".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/scheduled".into(),
            description: "List scheduled posts".into(),
        },
        RouteDescriptor {
            method: "DELETE".into(),
            path: "/scheduled".into(),
            description: "Cancel a scheduled post".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/stats".into(),
            description: "Publishing statistics".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let has_twitter = get_setting("twitter_api_key").is_some();
            let has_bluesky = get_setting("bluesky_handle").is_some();
            let has_instagram = get_setting("instagram_access_token").is_some();
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "social-publisher-wasm",
                "runtime": "wasm",
                "platforms": {
                    "twitter": has_twitter,
                    "bluesky": has_bluesky,
                    "instagram": has_instagram,
                },
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/publish") => {
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            // Publishing calls go through host-http::fetch for each platform
            var::set("host_call:social_publish", &body_str)?;

            let result = match var::get("host_result:social_publish") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "publishing"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "publishing"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/templates") | ("GET", "/templates/preview") | ("GET", "/history")
        | ("GET", "/scheduled") | ("DELETE", "/scheduled") | ("GET", "/stats") => {
            let call_key = format!("host_call:social:{}", req.path);
            var::set(&call_key, "")?;
            let result_key = format!("host_result:social:{}", req.path);
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
