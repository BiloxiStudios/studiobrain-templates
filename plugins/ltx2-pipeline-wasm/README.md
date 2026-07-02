# LTX-2 Pipeline WASM Adapter

WASM protocol adapter for the [LTX-2 ltx-pipelines server](https://github.com/Lightricks/LTX-2/tree/main/packages/ltx-pipelines).

## What It Does

This adapter bridges StudioBrain's model-manager managed service system to the LTX-2 video generation pipeline. It implements the `ProtocolAdapter` interface expected by the model-manager's Extism WASM plugin host:

| Function | Purpose |
|----------|---------|
| `adapt_request` | Converts a `GenerateRequest` into an HTTP submission payload for the LTX-2 server |
| `adapt_response` | Handles the server response — returns `done`, `pending` (with poll URL), or `error` |
| `health_check` | Probes the LTX-2 server health endpoint |

## LTX-2 Compatibility

The LTX-2 ltx-pipelines library is **synchronous** (no async job queue). This adapter handles that by:

1. Submitting the generation request to the server's `/generate` endpoint
2. When the server responds (synchronously), parsing the response:
   - If it contains `job_id`, returns `pending` with a poll URL (for wrapped async servers)
   - If it contains `output`/`video_url`/`result`, returns `done`
   - If it contains `error`/`message` with error status, returns `error`
   - Otherwise, treats any successful JSON response as `done`

## Building

```bash
# Prerequisites
rustup target add wasm32-wasip1

# Release build (optimised, stripped)
bash build.sh

# Debug build
bash build.sh debug
```

Output: `plugin.wasm` (and `plugin.wasm.sha256` with the SHA-256 hash).

## Registry

This adapter is registered in `registry/adapters.json` in the studiobrain-model-manager repo:

```json
{
  "id": "ltx2-pipeline",
  "display_name": "LTX-2 Video Pipeline",
  "service_type": "video",
  "version": "0.1.0",
  "author": "BiloxiStudios",
  "wasm_url": "https://github.com/BiloxiStudios/studiobrain-model-manager/releases/download/adapters-v0.1.0/ltx2-pipeline.wasm",
  "sha256": "<calculated at build time>",
  "compatible_services": ["ltx-video", "ltx2"]
}
```

## Usage in model-manager Config

```toml
[managed_services.ltx2]
display_name = "LTX-2 Video Generator"
service_type = "video"
runtime = "process"
command = "python -m ltx_pipelines.ti2vid_two_stages --checkpoint-path /models/ltx2.safetensors"
working_dir = "/opt/ltx-pipelines"
host_port = 8188
adapter = "wasm:ltx2-pipeline"
vram_estimate_gb = 20.0
idle_timeout = "15m"
```

## License

Apache-2.0
