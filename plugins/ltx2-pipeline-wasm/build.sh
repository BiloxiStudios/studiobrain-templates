#!/usr/bin/env bash
# Build the ltx2-pipeline-wasm plugin to a WASM binary.
#
# Prerequisites:
#   rustup target add wasm32-wasip1
#
# Usage:
#   bash build.sh          # release build (optimised, stripped)
#   bash build.sh debug    # debug build (fast, unoptimised)

set -euo pipefail
cd "$(dirname "$0")"

PROFILE="${1:-release}"

if ! command -v cargo &>/dev/null; then
    echo "ERROR: cargo not found. Install Rust: https://rustup.rs/" >&2
    exit 1
fi

if ! rustup target list --installed 2>/dev/null | grep -q wasm32-wasip1; then
    echo "Adding wasm32-wasip1 target..."
    rustup target add wasm32-wasip1
fi

if [ "$PROFILE" = "debug" ]; then
    echo "Building ltx2-pipeline-wasm (debug)..."
    cargo build --target wasm32-wasip1
    WASM="target/wasm32-wasip1/debug/ltx2_pipeline_wasm.wasm"
else
    echo "Building ltx2-pipeline-wasm (release)..."
    cargo build --target wasm32-wasip1 --release
    WASM="target/wasm32-wasip1/release/ltx2_pipeline_wasm.wasm"
fi

if [ ! -f "$WASM" ]; then
    echo "ERROR: Expected WASM output not found at $WASM" >&2
    exit 1
fi

cp "$WASM" ./plugin.wasm
SIZE=$(wc -c < ./plugin.wasm)
echo "Built: plugin.wasm ($SIZE bytes)"

# Calculate SHA256 for registry.
if command -v sha256sum &>/dev/null; then
    HASH=$(sha256sum ./plugin.wasm | awk '{print $1}')
elif command -v shasum &>/dev/null; then
    HASH=$(shasum -a 256 ./plugin.wasm | awk '{print $1}')
else
    echo "WARNING: No sha256 tool found — cannot calculate hash"
    HASH=""
fi

if [ -n "$HASH" ]; then
    echo "SHA256: $HASH"
    echo "$HASH" > ./plugin.wasm.sha256
fi
