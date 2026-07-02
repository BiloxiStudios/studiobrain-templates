//! LTX-2 Pipeline WASM Adapter
//!
//! Protocol adapter for the LTX-2 ltx-pipelines server API
//! (https://github.com/Lightricks/LTX-2/tree/main/packages/ltx-pipelines).
//!
//! This WASM plugin bridges the model-manager's `ProtocolAdapter` interface
//! to the LTX-2 synchronous pipeline API. Since ltx-pipelines runs
//! synchronously (no job queue), the adapter:
//!
//! - `adapt_request`:  Builds the Python CLI command and submission payload
//!                     for the ltx-pipelines server.
//! - `adapt_response`: Handles the poll loop — since LTX-2 is synchronous,
//!                     the adapter returns "done" immediately when the server
//!                     responds, or "pending" with a poll URL if the server
//!                     supports async job submission via a wrapper.
//! - `health_check`:   Probes the ltx-pipelines server health endpoint.
//!
//! Target: wasm32-wasip1, compiled with cargo --target wasm32-wasip1.

use extism_pdk::*;
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types — model-manager ProtocolAdapter interface
// ---------------------------------------------------------------------------

/// Generate request from the model-manager scheduler.
/// This is what the host passes into adapt_request.
#[derive(Deserialize, Debug)]
struct GenerateRequest {
    #[serde(default)]
    #[allow(dead_code)]
    model: String,
    #[serde(default)]
    prompt: String,
    #[serde(default)]
    negative_prompt: Option<String>,
    #[serde(default)]
    width: Option<u32>,
    #[serde(default)]
    height: Option<u32>,
    #[serde(default)]
    num_frames: Option<u32>,
    #[serde(default)]
    seed: Option<u64>,
    #[serde(default)]
    guidance_scale: Option<f32>,
    #[serde(default)]
    num_inference_steps: Option<u32>,
    /// Extra parameters passed through as JSON.
    #[serde(default)]
    extra: Option<serde_json::Value>,
}

/// Raw HTTP response from the managed service.
/// Passed into adapt_response and health_check.
#[derive(Deserialize, Debug)]
struct RawHttpResponse {
    status_code: u16,
    #[serde(default)]
    #[allow(dead_code)]
    headers: Vec<(String, String)>,
    #[serde(default)]
    body: String,
}

/// Adapted request — what the host should send to the service.
#[derive(Serialize, Debug)]
struct AdaptedRequest {
    url: String,
    method: String,
    headers: serde_json::Value,
    body: serde_json::Value,
    timeout_ms: u64,
}

/// Poll specification for pending responses.
#[derive(Serialize, Debug)]
struct PollSpec {
    url: String,
    method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    body: Option<serde_json::Value>,
    delay_ms: u64,
}

/// Adapted response — returned from adapt_response.
/// Three variants: "done", "pending", "error".
#[derive(Serialize, Debug)]
#[serde(tag = "status", rename_all = "snake_case")]
enum AdaptedResponse {
    Done { result: serde_json::Value },
    Pending { poll: PollSpec },
    Error { message: String },
}

/// Health check result.
#[derive(Serialize, Debug)]
struct HealthCheckResult {
    healthy: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    message: Option<String>,
}

// ---------------------------------------------------------------------------
// LTX-2 pipeline command builder
// ---------------------------------------------------------------------------

/// Build a submission payload for the LTX-2 ltx-pipelines server.
///
/// The ltx-pipelines server accepts generation requests via its API.
/// This function converts the model-manager's GenerateRequest into
/// the format the LTX-2 server expects.
fn build_ltx2_submission(req: &GenerateRequest) -> serde_json::Value {
    let mut payload = serde_json::Map::new();

    // Core generation parameters.
    if !req.prompt.is_empty() {
        payload.insert("prompt".to_string(), serde_json::json!(req.prompt));
    }
    if let Some(ref neg) = req.negative_prompt {
        payload.insert("negative_prompt".to_string(), serde_json::json!(neg));
    }
    if let Some(w) = req.width {
        // LTX-2 requires dimensions divisible by 32.
        payload.insert("width".to_string(), serde_json::json!(round_to_32(w)));
    }
    if let Some(h) = req.height {
        payload.insert("height".to_string(), serde_json::json!(round_to_32(h)));
    }
    if let Some(nf) = req.num_frames {
        // LTX-2 frame count formula: 8n+1.
        payload.insert("num_frames".to_string(), serde_json::json!(nf));
    }
    if let Some(seed) = req.seed {
        payload.insert("seed".to_string(), serde_json::json!(seed));
    }
    if let Some(gs) = req.guidance_scale {
        payload.insert("guidance_scale".to_string(), serde_json::json!(gs));
    }
    if let Some(steps) = req.num_inference_steps {
        payload.insert("num_inference_steps".to_string(), serde_json::json!(steps));
    }

    // Pass through extra parameters.
    if let Some(ref extra) = req.extra {
        if let serde_json::Value::Object(obj) = extra {
            for (k, v) in obj {
                payload.insert(k.clone(), v.clone());
            }
        }
    }

    serde_json::Value::Object(payload)
}

/// Round a dimension to the nearest multiple of 32 (LTX-2 requirement).
fn round_to_32(v: u32) -> u32 {
    (v + 15) / 32 * 32
}

// ---------------------------------------------------------------------------
// adapt_request
// ---------------------------------------------------------------------------

/// Convert a GenerateRequest into an HTTP request for the LTX-2 server.
///
/// The host provides the base URL via the `base_url` config variable.
/// This function builds the submission payload.
#[plugin_fn]
pub fn adapt_request(Json(req): Json<GenerateRequest>) -> FnResult<Json<AdaptedRequest>> {
    let payload = build_ltx2_submission(&req);

    // Build headers.
    let headers = serde_json::json!({
        "Content-Type": "application/json",
        "Accept": "application/json",
    });

    Ok(Json(AdaptedRequest {
        // The URL is set to the generation endpoint.
        // The host's base_url is configured in the managed service config.
        url: "/generate".to_string(),
        method: "POST".to_string(),
        headers,
        body: payload,
        // Video generation can take a while — set a generous timeout.
        timeout_ms: 300_000, // 5 minutes
    }))
}

// ---------------------------------------------------------------------------
// adapt_response
// ---------------------------------------------------------------------------

/// Handle the response from the LTX-2 server.
///
/// Since ltx-pipelines is synchronous, a successful response means the
/// generation is complete. The adapter returns "done" with the result.
///
/// If the response indicates an error (non-2xx status or error JSON),
/// it returns "error" with the message.
///
/// If the server supports async job submission (via a wrapper), it
/// returns "pending" with a poll URL.
#[plugin_fn]
pub fn adapt_response(Json(resp): Json<RawHttpResponse>) -> FnResult<Json<AdaptedResponse>> {
    // Check for HTTP-level errors.
    if resp.status_code >= 500 {
        return Ok(Json(AdaptedResponse::Error {
            message: format!("Server error: HTTP {}", resp.status_code),
        }));
    }

    if resp.status_code >= 400 {
        // Try to extract an error message from the body.
        let message = extract_error_message(&resp.body);
        return Ok(Json(AdaptedResponse::Error { message }));
    }

    // Parse the JSON body.
    let body_value: serde_json::Value = match serde_json::from_str(&resp.body) {
        Ok(v) => v,
        Err(e) => {
            // Non-JSON body — might be a direct media response or error page.
            return Ok(Json(AdaptedResponse::Error {
                message: format!("Invalid JSON response: {e}"),
            }));
        }
    };

    // Check for async job submission pattern (job_id + status field).
    // Some LTX-2 server wrappers submit to a queue and return a job ID.
    if let Some(job_id) = body_value.get("job_id").and_then(|v| v.as_str()) {
        let status = body_value.get("status").and_then(|v| v.as_str()).unwrap_or("pending");

        if status == "done" || status == "completed" || status == "success" {
            return Ok(Json(AdaptedResponse::Done {
                result: body_value,
            }));
        }

        // Job is still pending — return poll spec.
        return Ok(Json(AdaptedResponse::Pending {
            poll: PollSpec {
                url: format!("/jobs/{job_id}/status"),
                method: "GET".to_string(),
                body: None,
                delay_ms: 2_000, // Poll every 2 seconds.
            },
        }));
    }

    // Check for direct error in JSON body.
    if let Some(error) = body_value.get("error").and_then(|v| v.as_str()) {
        return Ok(Json(AdaptedResponse::Error {
            message: error.to_string(),
        }));
    }
    if let Some(error) = body_value.get("message").and_then(|v| v.as_str()) {
        // Some APIs use "message" for errors.
        // But "message" can also be a status message — check for error indicators.
        if body_value.get("status").and_then(|v| v.as_str()) == Some("error") {
            return Ok(Json(AdaptedResponse::Error {
                message: error.to_string(),
            }));
        }
    }

    // Check for output field — indicates successful generation complete.
    if body_value.get("output").is_some()
        || body_value.get("video_url").is_some()
        || body_value.get("result").is_some()
    {
        return Ok(Json(AdaptedResponse::Done {
            result: body_value,
        }));
    }

    // Default: treat any successful JSON response as done.
    Ok(Json(AdaptedResponse::Done {
        result: body_value,
    }))
}

/// Extract an error message from a response body.
fn extract_error_message(body: &str) -> String {
    // Try to parse as JSON and extract error/message field.
    if let Ok(value) = serde_json::from_str::<serde_json::Value>(body) {
        if let Some(error) = value.get("error").and_then(|v| v.as_str()) {
            return error.to_string();
        }
        if let Some(message) = value.get("message").and_then(|v| v.as_str()) {
            return message.to_string();
        }
        if let Some(detail) = value.get("detail").and_then(|v| v.as_str()) {
            return detail.to_string();
        }
    }
    // Fallback: truncate the body to a reasonable length.
    if body.len() > 200 {
        format!("{}...", &body[..200])
    } else {
        body.to_string()
    }
}

// ---------------------------------------------------------------------------
// health_check
// ---------------------------------------------------------------------------

/// Check if the LTX-2 server is healthy and reachable.
///
/// Returns healthy=true if the server responds with 200 OK on its
/// health endpoint, or if the response body indicates the server
/// is operational.
#[plugin_fn]
pub fn health_check(Json(resp): Json<RawHttpResponse>) -> FnResult<Json<HealthCheckResult>> {
    if resp.status_code == 200 {
        // Try to parse the body for additional health indicators.
        if let Ok(value) = serde_json::from_str::<serde_json::Value>(&resp.body) {
            // Some health endpoints return {"status": "ok"} or {"healthy": true}.
            if let Some(status) = value.get("status").and_then(|v| v.as_str()) {
                if status == "ok" || status == "healthy" || status == "running" {
                    return Ok(Json(HealthCheckResult {
                        healthy: true,
                        message: value.get("message").and_then(|v| v.as_str()).map(String::from),
                    }));
                }
                return Ok(Json(HealthCheckResult {
                    healthy: false,
                    message: Some(format!("Server reports status: {status}")),
                }));
            }
            if let Some(healthy) = value.get("healthy").and_then(|v| v.as_bool()) {
                return Ok(Json(HealthCheckResult {
                    healthy,
                    message: value.get("message").and_then(|v| v.as_str()).map(String::from),
                }));
            }
        }
        // 200 OK with no specific health field — assume healthy.
        return Ok(Json(HealthCheckResult {
            healthy: true,
            message: None,
        }));
    }

    // Non-200 response — extract error info.
    let message = if resp.status_code == 0 {
        Some("Connection failed".to_string())
    } else {
        Some(format!("Health check failed: HTTP {}", resp.status_code))
    };

    Ok(Json(HealthCheckResult {
        healthy: false,
        message,
    }))
}
