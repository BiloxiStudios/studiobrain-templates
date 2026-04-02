#!/usr/bin/env bash
# Build the kanban-board-wasm plugin to a WASM binary.
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
    echo "Building kanban-board-wasm (debug)..."
    cargo build --target wasm32-wasip1
    WASM="target/wasm32-wasip1/debug/kanban_board_wasm.wasm"
else
    echo "Building kanban-board-wasm (release)..."
    cargo build --target wasm32-wasip1 --release
    WASM="target/wasm32-wasip1/release/kanban_board_wasm.wasm"
fi

if [ ! -f "$WASM" ]; then
    echo "ERROR: Expected WASM output not found at $WASM" >&2
    exit 1
fi

cp "$WASM" ./plugin.wasm
SIZE=$(wc -c < ./plugin.wasm)
echo "Built: plugin.wasm ($SIZE bytes)"
