#!/usr/bin/env bash
# Build hello-world-wasm as a StudioBrain WASM component.
#
# Prerequisites:
#   pip install componentize-py
#
# Usage:
#   ./build.sh
#
# Output:
#   plugin.wasm — ready to install alongside plugin.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Copy WIT files from the plugin SDK if not present.
WIT_DIR="$SCRIPT_DIR/wit"
if [ ! -d "$WIT_DIR" ]; then
    echo "Copying WIT files from plugin SDK..."
    CORE_WIT_DIR="/srv/studiobrain-dev/core/wit"
    if [ -d "$CORE_WIT_DIR" ]; then
        mkdir -p "$WIT_DIR"
        cp "$CORE_WIT_DIR"/*.wit "$WIT_DIR/"
        echo "Copied WIT files from $CORE_WIT_DIR"
    else
        echo "ERROR: Cannot find core WIT files at $CORE_WIT_DIR"
        echo "Download from: /core/wit/studiobrain-plugin.wit"
        exit 1
    fi
fi

# Generate Python bindings from the WIT files (if not already generated).
if [ ! -d "plugin" ]; then
    echo "Generating bindings from WIT..."
    componentize-py --wit-path ./wit --world plugin bindings .
fi

echo "Building WASM component..."
componentize-py --wit-path ./wit --world plugin componentize plugin -o plugin.wasm

echo ""
echo "Build complete: plugin.wasm ($(du -h plugin.wasm 2>/dev/null | cut -f1 || echo 'size unavailable'))"
echo ""
echo "Install by copying plugin.json + plugin.wasm to your StudioBrain plugins directory."
