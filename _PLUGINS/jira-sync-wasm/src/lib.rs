// StudioBrain Jira Sync (WASM) WASM Plugin
//
// WASM port of the jira-sync plugin. Exports:
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
        id: "jira-sync-wasm".into(),
        name: "Jira Sync (WASM)".into(),
        version: "0.1.0".into(),
        description: "Jira Sync (WASM) -- WASM port".into(),
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
        "[jira-sync-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[jira-sync-wasm] Entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_entity_delete(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "[jira-sync-wasm] Entity {}/{} deleted",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "jira-sync-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Jira Sync (WASM) ready.".into()],
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
            description: "Plugin health check with Jira connection status".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/sync".into(),
            description: "Sync a single entity to Jira".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/link".into(),
            description: "Get the Jira issue linked to an entity".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/link".into(),
            description: "Link an entity to a Jira issue".into(),
        },
        RouteDescriptor {
            method: "DELETE".into(),
            path: "/link".into(),
            description: "Unlink an entity from a Jira issue".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/sync-all".into(),
            description: "Sync all entities of a type to Jira".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/mappings".into(),
            description: "Get entity-to-issue type mappings".into(),
        },
        RouteDescriptor {
            method: "PUT".into(),
            path: "/mappings".into(),
            description: "Update entity-to-issue type mappings".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/webhook".into(),
            description: "Jira webhook receiver for bidirectional sync".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let has_token = get_setting("jira_api_token").is_some();
            let instance = get_setting("jira_instance_url").unwrap_or_default();
            let project = get_setting("default_project_key").unwrap_or_default();
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "jira-sync-wasm",
                "runtime": "wasm",
                "api_token_configured": has_token,
                "jira_instance": instance,
                "project_key": project,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/sync") | ("POST", "/sync-all") | ("POST", "/link")
        | ("DELETE", "/link") | ("POST", "/webhook") => {
            let instance = get_setting("jira_instance_url").unwrap_or_default();
            let email = get_setting("jira_email").unwrap_or_default();
            let token = get_setting("jira_api_token").unwrap_or_default();
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();

            let call = serde_json::json!({
                "url": format!("{}/rest/api/3/issue", instance),
                "method": req.method,
                "headers": {
                    "Authorization": format!("Basic {}", email),
                },
                "body": body_str,
            });
            var::set("host_call:http_fetch", &call.to_string())?;

            let result = match var::get("host_result:http_fetch") {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "syncing"}).to_string(),
            };
            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "syncing"}));
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/link") | ("GET", "/mappings") | ("PUT", "/mappings") => {
            let call_key = format!("host_call:jira:{}", req.path);
            var::set(&call_key, "")?;
            let result_key = format!("host_result:jira:{}", req.path);
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
