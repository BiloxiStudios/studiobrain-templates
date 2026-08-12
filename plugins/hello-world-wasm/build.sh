#!/usr/bin/env bash
# Build hello-world-wasm as a StudioBrain WASM component.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "plugin" ]; then
    echo "Generating bindings from WIT..."
    componentize-py --wit-path ./wit --world plugin bindings .
fi

echo "Building WASM component..."
componentize-py --wit-path ./wit --world plugin componentize plugin -o plugin.wasm
echo "Build complete: plugin.wasm"
