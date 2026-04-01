// StudioBrain Hello World WASM Plugin
//
// Reference implementation showing how a Rust/WASM plugin exports the
// functions defined in the StudioBrain plugin WIT interface.  Uses the
// Extism PDK, which gives us `#[plugin_fn]` for exports and `var::get` /
// `var::set` for host-managed state.
//
// Exported functions (match WIT `studiobrain:plugin@0.1.0`):
//   metadata   — get_info
//   hooks      — on_entity_save, on_entity_create, on_entity_delete, on_entity_validate
//   routes     — list_routes, handle_request

use extism_pdk::*;
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types — mirrors of the WIT records, serialised as JSON across the boundary
// ---------------------------------------------------------------------------

/// Metadata every plugin must provide (`types.plugin-info`).
#[derive(Serialize)]
struct PluginInfo {
    id: String,
    name: String,
    version: String,
    description: String,
    author: String,
}

/// An entity lifecycle event (`types.hook-event`).
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

/// Result returned from save/create/delete hooks (`types.hook-result`).
#[derive(Serialize)]
struct HookResult {
    /// Modified entity data (JSON). `None` means keep the original.
    data: Option<String>,
    /// User-facing messages.
    messages: Vec<String>,
    /// Whether to abort the operation.
    abort: bool,
    /// Reason shown to the user when `abort` is true.
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

/// Validation result (`types.validation-result`).
#[derive(Serialize)]
struct ValidationResult {
    valid: bool,
    errors: Vec<ValidationError>,
}

/// A single validation finding (`types.validation-error`).
#[derive(Serialize)]
struct ValidationError {
    field: String,
    message: String,
    severity: String,
}

/// Setup result for on_project_init (`types.setup-result`).
#[derive(Serialize)]
struct SetupResult {
    success: bool,
    messages: Vec<String>,
}

/// Route descriptor (`types.route-descriptor`).
#[derive(Serialize)]
struct RouteDescriptor {
    method: String,
    path: String,
    description: String,
}

/// Inbound HTTP request (`types.http-request`).
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

/// Outbound HTTP response (`types.http-response`).
#[derive(Serialize)]
struct HttpResponse {
    status: u16,
    headers: Vec<KvPair>,
    body: Option<Vec<u8>>,
}

/// Key-value pair for headers and query params (`types.kv-pair`).
#[derive(Serialize, Deserialize)]
struct KvPair {
    key: String,
    value: String,
}

/// Entity query result returned by the host (`types.entity-query-result`).
#[derive(Deserialize)]
struct EntityQueryResult {
    #[allow(dead_code)]
    records: Vec<serde_json::Value>,
    total: u32,
    #[allow(dead_code)]
    offset: u32,
    #[allow(dead_code)]
    limit: u32,
}

/// Query filter sent to the host (`types.entity-query-filter`).
#[derive(Serialize)]
struct EntityQueryFilter {
    entity_type: Option<String>,
    filter_json: Option<String>,
    limit: Option<u32>,
    offset: Option<u32>,
    order_by: Option<String>,
    order_desc: Option<bool>,
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

/// Try to read the "greeting" setting from the host.  Falls back to the
/// default if the host call fails or the key is not set.
fn greeting_message() -> String {
    // Extism vars are the simplest way to pass host-managed config into a
    // plugin.  The StudioBrain host pre-populates vars from the plugin's
    // settings before each call.
    match var::get("setting:greeting") {
        Ok(Some(bytes)) => String::from_utf8(bytes).unwrap_or_else(|_| default_greeting()),
        _ => default_greeting(),
    }
}

fn default_greeting() -> String {
    "Hello from the WASM plugin system!".into()
}

// ---------------------------------------------------------------------------
// metadata — required export
// ---------------------------------------------------------------------------

/// Return the plugin's identity.
/// WIT: `metadata::get-info() -> plugin-info`
#[plugin_fn]
pub fn get_info(_: ()) -> FnResult<Json<PluginInfo>> {
    Ok(Json(PluginInfo {
        id: "hello-world-wasm".into(),
        name: "Hello World (WASM)".into(),
        version: "1.0.0".into(),
        description: "Reference WASM plugin demonstrating hooks, routes, host \
                       functions, settings, and frontend panels"
            .into(),
        author: "BiloxiStudios".into(),
    }))
}

// ---------------------------------------------------------------------------
// hooks — optional exports
// ---------------------------------------------------------------------------

/// Called before an entity is saved (create or update).
/// WIT: `hooks::on-entity-save(event: hook-event) -> hook-result`
#[plugin_fn]
pub fn on_entity_save(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "Hello! Entity {}/{} was saved",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

/// Called before an entity is created (first save only).
/// WIT: `hooks::on-entity-create(event: hook-event) -> hook-result`
#[plugin_fn]
pub fn on_entity_create(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "Hello! New entity {}/{} created",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

/// Called before an entity is deleted.
/// WIT: `hooks::on-entity-delete(event: hook-event) -> hook-result`
#[plugin_fn]
pub fn on_entity_delete(Json(event): Json<HookEvent>) -> FnResult<Json<HookResult>> {
    log!(
        LogLevel::Info,
        "Hello! Entity {}/{} is being deleted",
        event.entity_type,
        event.entity_id
    );
    Ok(Json(HookResult::passthrough()))
}

/// Validate that the entity has a non-empty "name" field.
/// WIT: `hooks::on-entity-validate(event: hook-event) -> validation-result`
#[plugin_fn]
pub fn on_entity_validate(Json(event): Json<HookEvent>) -> FnResult<Json<ValidationResult>> {
    let parsed: serde_json::Value =
        serde_json::from_str(&event.data).unwrap_or(serde_json::Value::Null);

    // Check for a "name" field in the entity's frontmatter.
    let has_name = parsed
        .get("name")
        .and_then(|v| v.as_str())
        .map(|s| !s.trim().is_empty())
        .unwrap_or(false);

    if has_name {
        Ok(Json(ValidationResult {
            valid: true,
            errors: Vec::new(),
        }))
    } else {
        Ok(Json(ValidationResult {
            valid: false,
            errors: vec![ValidationError {
                field: "name".into(),
                message: "Entity must have a non-empty 'name' field".into(),
                severity: "error".into(),
            }],
        }))
    }
}

/// Called once when the plugin is first loaded in a project.
/// WIT: `hooks::on-project-init() -> setup-result`
#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "hello-world-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Hello World (WASM) plugin ready.".into()],
    }))
}

// ---------------------------------------------------------------------------
// routes — optional exports
// ---------------------------------------------------------------------------

/// Declare the routes this plugin handles.
/// WIT: `routes::list-routes() -> list<route-descriptor>`
#[plugin_fn]
pub fn list_routes(_: ()) -> FnResult<Json<Vec<RouteDescriptor>>> {
    Ok(Json(vec![
        RouteDescriptor {
            method: "GET".into(),
            path: "/hello".into(),
            description: "Greeting endpoint — returns a configurable hello message".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/stats".into(),
            description: "Returns the total entity count from the host".into(),
        },
        RouteDescriptor {
            method: "GET".into(),
            path: "/status".into(),
            description: "Plugin health check".into(),
        },
    ]))
}

/// Handle an inbound HTTP request.
/// WIT: `routes::handle-request(request: http-request) -> http-response`
#[plugin_fn]
pub fn handle_request(Json(req): Json<HttpRequest>) -> FnResult<Json<HttpResponse>> {
    match (req.method.as_str(), req.path.as_str()) {
        // --- GET /hello -------------------------------------------------
        ("GET", "/hello") => {
            let greeting = greeting_message();
            let body = serde_json::json!({
                "message": greeting,
                "plugin": "hello-world-wasm",
                "version": "1.0.0"
            });
            Ok(Json(json_response(200, &body)))
        }

        // --- GET /stats -------------------------------------------------
        ("GET", "/stats") => {
            // Ask the host how many entities exist.  The host exposes entity
            // queries through an Extism host function.  We send the filter as
            // a JSON var and read the result back.
            let filter = EntityQueryFilter {
                entity_type: None,
                filter_json: None,
                limit: Some(0), // we only need the count, not the records
                offset: None,
                order_by: None,
                order_desc: None,
            };
            let filter_json = serde_json::to_string(&filter).unwrap_or_default();

            // Write the query filter into a well-known var for the host to read.
            var::set("host_call:query_entities", &filter_json)?;

            // Read the host's response from the result var.
            let entity_count = match var::get("host_result:query_entities") {
                Ok(Some(bytes)) => {
                    let result_str = String::from_utf8(bytes).unwrap_or_default();
                    serde_json::from_str::<EntityQueryResult>(&result_str)
                        .map(|r| r.total)
                        .unwrap_or(0)
                }
                _ => 0,
            };

            let body = serde_json::json!({
                "entity_count": entity_count,
                "plugin": "hello-world-wasm",
            });
            Ok(Json(json_response(200, &body)))
        }

        // --- GET /status ------------------------------------------------
        ("GET", "/status") => {
            let body = serde_json::json!({
                "status": "ok",
                "plugin": "hello-world-wasm",
                "runtime": "wasm",
            });
            Ok(Json(json_response(200, &body)))
        }

        // --- 404 --------------------------------------------------------
        _ => {
            let body = serde_json::json!({
                "error": "not_found",
                "message": format!("No route for {} {}", req.method, req.path),
            });
            Ok(Json(json_response(404, &body)))
        }
    }
}
