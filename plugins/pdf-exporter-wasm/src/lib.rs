// StudioBrain PDF Bible Exporter (WASM) WASM Plugin
//
// WASM port of the pdf-exporter plugin. Exports:
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
        id: "pdf-exporter-wasm".into(),
        name: "PDF Bible Exporter (WASM)".into(),
        version: "1.0.0".into(),
        description: "PDF Bible Exporter (WASM) -- WASM port".into(),
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
        "[pdf-exporter-wasm] Entity {}/{} saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "pdf-exporter-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["PDF Bible Exporter (WASM) ready.".into()],
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
            path: "/templates".into(),
            description: "List available export templates".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/entities".into(),
            description: "List entities of a given type".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/preview".into(),
            description: "HTML preview of a single entity export".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/export".into(),
            description: "Downloadable print-ready HTML for an entity".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/batch".into(),
            description: "Batch export multiple entities to HTML".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/world-bible".into(),
            description: "Generate a full world bible document".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let studio_name = get_setting("studio_name")
                .unwrap_or_else(|| "City of Brains Studio".into());
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "pdf-exporter-wasm",
                "runtime": "wasm",
                "studio_name": studio_name,
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/templates") => {
            let body = serde_json::json!({
                "templates": [
                    {"id": "character-sheet", "name": "Character Sheet", "entity_types": ["character"]},
                    {"id": "location-guide", "name": "Location Guide", "entity_types": ["location"]},
                    {"id": "world-bible", "name": "World Bible", "entity_types": ["*"]},
                    {"id": "faction-dossier", "name": "Faction Dossier", "entity_types": ["faction"]},
                    {"id": "item-catalog", "name": "Item Catalog", "entity_types": ["item"]},
                ]
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/entities") | ("GET", "/preview") | ("GET", "/export")
        | ("POST", "/batch") | ("POST", "/world-bible") => {
            // Entity rendering requires host entity data + markdown parsing.
            // Delegate to host and return the rendered result.
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();
            let call_key = format!("host_call:pdf_export:{}", req.path);
            var::set(&call_key, &body_str)?;

            let result_key = format!("host_result:pdf_export:{}", req.path);
            let result = match var::get(&result_key) {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "delegated"}).to_string(),
            };

            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "delegated"}));
            Ok(Json(json_response(200, &body)))
        }
        _ => Ok(Json(not_found_response(&req.method, &req.path))),
    }
}
