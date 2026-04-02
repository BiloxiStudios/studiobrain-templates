// StudioBrain Import/Export Pipeline (WASM) WASM Plugin
//
// WASM port of the import-export-pipeline plugin. Exports:
//   metadata   -- get_info
//   hooks      -- on_project_init
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
        id: "import-export-pipeline-wasm".into(),
        name: "Import/Export Pipeline (WASM)".into(),
        version: "1.0.0".into(),
        description: "Import/Export Pipeline (WASM) -- WASM port".into(),
        author: "BiloxiStudios".into(),
    }))
}

// ---------------------------------------------------------------------------
// hooks
// ---------------------------------------------------------------------------

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "import-export-pipeline-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Import/Export Pipeline (WASM) ready.".into()],
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
            path: "/import/preview".into(),
            description: "Preview an import before applying".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/import/single".into(),
            description: "Import a single file".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/import/batch".into(),
            description: "Batch import multiple files".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/import/zip".into(),
            description: "Import from a ZIP archive".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/markdown".into(),
            description: "Export entities as Markdown".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/json".into(),
            description: "Export entities as JSON".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/csv".into(),
            description: "Export entities as CSV".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/html".into(),
            description: "Export entities as HTML".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/pdf".into(),
            description: "Export entities as PDF".into(),
        },
        RouteDescriptor {
            method: "POST".into(),
            path: "/export/docx".into(),
            description: "Export entities as DOCX".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/profiles".into(),
            description: "List available import/export profiles".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/formats".into(),
            description: "List supported import/export formats".into(),
        },
    ]))
}

#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/status") => {
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "import-export-pipeline-wasm",
                "runtime": "wasm",
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/formats") => {
            let body = serde_json::json!({
                "import": ["markdown", "json", "csv", "opml", "verse", "zip"],
                "export": ["markdown", "json", "csv", "html", "pdf", "docx"],
            });
            Ok(Json(json_response(200, &body)))
        }
        ("GET", "/profiles") => {
            let body = serde_json::json!({
                "profiles": ["character", "location", "quest", "dialogue", "assembly"]
            });
            Ok(Json(json_response(200, &body)))
        }
        ("POST", "/import/preview") | ("POST", "/import/single")
        | ("POST", "/import/batch") | ("POST", "/import/zip")
        | ("POST", "/export/markdown") | ("POST", "/export/json")
        | ("POST", "/export/csv") | ("POST", "/export/html")
        | ("POST", "/export/pdf") | ("POST", "/export/docx") => {
            // I/O-heavy operations delegated to host
            let body_str = req.body
                .as_ref()
                .map(|b| String::from_utf8_lossy(b).to_string())
                .unwrap_or_default();
            let call_key = format!("host_call:import_export:{}", req.path);
            var::set(&call_key, &body_str)?;

            let result_key = format!("host_result:import_export:{}", req.path);
            let result = match var::get(&result_key) {
                Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_default(),
                _ => serde_json::json!({"status": "processing"}).to_string(),
            };

            let body: serde_json::Value =
                serde_json::from_str(&result).unwrap_or(serde_json::json!({"status": "processing"}));
            Ok(Json(json_response(200, &body)))
        }
        _ => Ok(Json(not_found_response(&req.method, &req.path))),
    }
}
