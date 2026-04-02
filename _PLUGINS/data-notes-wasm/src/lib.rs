// StudioBrain Data Notes WASM Plugin
//
// Frontend-only plugin: notes are managed via the generic Plugin Data Service.
// The WASM backend exports get_info and a minimal on_project_init hook.
// All real work happens in the frontend panels (HTML/JS).

use extism_pdk::*;
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

#[derive(Serialize)]
struct PluginInfo {
    id: String,
    name: String,
    version: String,
    description: String,
    author: String,
}

#[derive(Serialize)]
struct SetupResult {
    success: bool,
    messages: Vec<String>,
}

// ---------------------------------------------------------------------------
// metadata
// ---------------------------------------------------------------------------

#[plugin_fn]
pub fn get_info(_: ()) -> FnResult<Json<PluginInfo>> {
    Ok(Json(PluginInfo {
        id: "data-notes-wasm".into(),
        name: "Entity Notes (WASM)".into(),
        version: "1.0.0".into(),
        description: "Attach timestamped notes to any entity. Uses the generic \
                       Plugin Data Service for database-backed storage."
            .into(),
        author: "BiloxiStudios".into(),
    }))
}

// ---------------------------------------------------------------------------
// hooks
// ---------------------------------------------------------------------------

#[plugin_fn]
pub fn on_project_init(_: ()) -> FnResult<Json<SetupResult>> {
    log!(LogLevel::Info, "data-notes-wasm plugin initialized");
    Ok(Json(SetupResult {
        success: true,
        messages: vec!["Entity Notes (WASM) plugin ready.".into()],
    }))
}
