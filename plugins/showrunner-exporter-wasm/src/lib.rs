// StudioBrain Showrunner Exporter (WASM) WASM Plugin
//
// WASM port of the showrunner-exporter plugin. Exports:
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
        id: "showrunner-exporter-wasm".into(),
        name: "Showrunner Exporter (WASM)".into(),
        version: "1.0.0".into(),
        description: "Showrunner Exporter (WASM) -- WASM port".into(),
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
        "[showrunner-exporter-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[showrunner-exporter-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "showrunner-exporter-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Showrunner Exporter (WASM) ready.".into()],
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
            path: "/export/character".into(),
            description: "Export a character to Showrunner format".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/episode".into(),
            description: "Export an episode to Showrunner format".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/preview".into(),
            description: "Preview entity export data".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/batch-export".into(),
            description: "Batch export entities to Showrunner".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/projects".into(),
            description: "List Showrunner projects".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/export-log".into(),
            description: "View export history".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/characters".into(),
            description: "List available characters for export".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/stats".into(),
            description: "Export statistics".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let api_url = get_setting("showrunner_api_url")
                .unwrap_or_else(|| "https://api.showrunner.xyz".into());
            let has_key = get_setting("showrunner_api_key").is_some();
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "showrunner-exporter-wasm",
                "runtime": "wasm",
                "api_url": api_url,
                "api_key_configured": has_key,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/export/character") | ("POST", "/export/episode")
        | ("POST", "/batch-export") => {
            // Export requires fetching entity data then POSTing to Showrunner API.
            // Use host-http::fetch for the external API call.
            let api_url = get_setting("showrunner_api_url")
                .unwrap_or_else(|| "https://api.showrunner.xyz".into());
            let api_key = get_setting("showrunner_api_key")
                .unwrap_or_default();
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            // Delegate external API call to host
            let call = serde_json::json!({
                "url": format!("{}/v1/import", api_url),
                "method": "POST",
                "headers": {"Authorization": format!("Bearer {}", api_key)},
                "body": body_str,
            });
            var::set("host_call:http_fetch", &call.to_string())?;

            let result = match var::get("host_result:http_fetch") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "export_queued"}).to_string(),
            };

            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "export_queued"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/preview") | ("GET", "/projects") | ("GET", "/export-log")
        | ("GET", "/export-status") | ("GET", "/characters") | ("GET", "/stats") => {
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "showrunner-exporter-wasm",
                "message": "Query delegated to host",
            });
            Ok(Json(json_response(200, &body)))
        }
        _ => Ok(Json(not_found_response(&req.method, &req.path))),
    }
}
