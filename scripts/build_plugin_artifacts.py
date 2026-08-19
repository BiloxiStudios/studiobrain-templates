#!/usr/bin/env python3
"""StudioBrain templates — plugin v2 build + smoke-test (SBAI-7183).

Stages publish-ready artifacts for every ``manifest_version: 2`` plugin under
``plugins/`` and emits a checksum-bearing index describing what was built.

This script deliberately does NOT touch any secret, credential, or network
resource — it only reads ``plugins/`` and writes to a local output directory.
That is what makes it safe to run in a pull_request-triggered CI job (forked
PRs included): the build/smoke stage of the pipeline is meant to run on
untrusted code, so it must be trustworthy to run with zero elevated access.
Publishing the staged output to R2 is a SEPARATE script
(``publish_to_r2.py``) that only ever runs in the push-to-main job — see
``scripts/check_workflow_secret_isolation.py`` for the automated check that
enforces this split.

Only v1 (legacy ``capabilities``) manifests are skipped: those plugins are
unsupported by the new pipeline (SBAI-6815) and stay archived as-is.
Protocol-adapter (WASM) plugins are also skipped here — they have no
``surfaces`` array and their component build is tracked separately
(PLUGIN-ARCHITECTURE-DESIGN.md work item 3, not this ticket).

Usage:
    python3 scripts/build_plugin_artifacts.py --out dist
    python3 scripts/build_plugin_artifacts.py --out dist --plugins-dir plugins

Exit code is non-zero if any plugin fails validation or smoke-test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import validate as _validate  # noqa: E402  (scripts/validate.py — reused for schema validation)

INDEX_SCHEMA_VERSION = 1


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(msg)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def canonical_json(obj: Any) -> str:
    """Sorted-key, compact JSON — same shape used by core's manifest signing
    (SBAI-2254 canonicalize_manifest) so a signed index is reproducible."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def discover_v2_plugins(plugins_dir: pathlib.Path) -> list[pathlib.Path]:
    found = []
    for manifest_path in sorted(plugins_dir.glob("*/plugin.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _err(f"{manifest_path}: JSON parse error: {exc}")
            continue
        if data.get("manifest_version") == 2:
            found.append(manifest_path)
    return found


def smoke_test_artifact(path: pathlib.Path) -> list[str]:
    """Minimal, dependency-free smoke test for a surface artifact file.

    Not a browser/runtime test — this repo is pure data with no build
    toolchain (see CLAUDE.md). The smoke test proves the artifact is
    present, non-empty, valid UTF-8, and (for .js) syntactically valid.
    """
    errors: list[str] = []
    if not path.exists():
        return [f"{path}: artifact file does not exist"]
    if path.stat().st_size == 0:
        errors.append(f"{path}: artifact file is empty")
        return errors
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: not valid UTF-8: {exc}")
        return errors

    suffix = path.suffix.lower()
    if suffix == ".html" and "<" not in text:
        errors.append(f"{path}: .html artifact contains no markup")
    elif suffix == ".js":
        node = shutil.which("node")
        if node:
            proc = subprocess.run(
                [node, "--check", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                errors.append(f"{path}: node --check failed: {proc.stderr.strip()}")
        else:
            _info(f"NOTE: node not available — skipping syntax check for {path}")
    return errors


def build_plugin(manifest_path: pathlib.Path, out_dir: pathlib.Path) -> tuple[dict[str, Any] | None, list[str]]:
    plugin_dir = manifest_path.parent
    plugin_id = plugin_dir.name
    errors: list[str] = []

    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    # 1. Schema validation (reuses scripts/validate.py's $ref-aware registry).
    schema_errors = _validate._validate_instance(data, "plugin.json", str(manifest_path))
    errors.extend(schema_errors)
    if data.get("id") != plugin_id:
        errors.append(
            f"{manifest_path}: manifest id '{data.get('id')}' does not match "
            f"directory name '{plugin_id}'"
        )

    surfaces = data.get("surfaces", [])
    if not isinstance(surfaces, list):
        errors.append(f"{manifest_path}: 'surfaces' is not an array")
        return None, errors

    # 2. Resolve + smoke-test every declared surface artifact.
    artifact_records = []
    for surface in surfaces:
        artifact = surface.get("artifact", {})
        rel_path = artifact.get("path")
        if not rel_path:
            errors.append(
                f"{manifest_path}: surface '{surface.get('id')}' has no artifact.path"
            )
            continue
        artifact_path = plugin_dir / rel_path
        errors.extend(smoke_test_artifact(artifact_path))
        if artifact_path.exists() and artifact_path.stat().st_size > 0:
            artifact_records.append(
                {
                    "surface_id": surface.get("id"),
                    "surface_type": surface.get("type"),
                    "path": rel_path,
                    "sha256": sha256_file(artifact_path),
                    "size_bytes": artifact_path.stat().st_size,
                }
            )

    if errors:
        return None, errors

    # 3. Stage into dist/plugins/<id>/<version>/ mirroring the R2 key layout
    #    (plugins/<id>/<version>/...) from PLUGIN-ARCHITECTURE-DESIGN.md Q3.
    version = data["version"]
    stage_dir = out_dir / "plugins" / plugin_id / version
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)

    manifest_bytes = manifest_path.read_bytes()
    (stage_dir / "plugin.json").write_bytes(manifest_bytes)

    for record in artifact_records:
        src = plugin_dir / record["path"]
        dst = stage_dir / record["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    manifest_sha256 = sha256_bytes(manifest_bytes)
    (stage_dir / "_checksums.json").write_text(
        json.dumps(
            {
                "manifest_sha256": manifest_sha256,
                "artifacts": artifact_records,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    entry = {
        "id": plugin_id,
        "name": data.get("name"),
        "version": version,
        "description": data.get("description"),
        "author": data.get("author"),
        "category": data.get("category"),
        "manifest_version": data.get("manifest_version"),
        "trust_tier": data.get("trust_tier"),
        "manifest_sha256": manifest_sha256,
        "artifacts": artifact_records,
        "r2_prefix": f"plugins/{plugin_id}/{version}/",
    }
    return entry, []


def build(plugins_dir: pathlib.Path, out_dir: pathlib.Path, built_at: str, source_commit: str) -> int:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    manifests = discover_v2_plugins(plugins_dir)
    _info(f"Found {len(manifests)} manifest_version=2 plugin(s) under {plugins_dir}")

    entries = []
    had_errors = False
    for manifest_path in manifests:
        entry, errors = build_plugin(manifest_path, out_dir)
        if errors:
            had_errors = True
            for e in errors:
                _err(e)
            continue
        entries.append(entry)
        _info(f"  built {entry['id']}@{entry['version']} ({len(entry['artifacts'])} artifact(s))")

    index = {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "generated_at": built_at,
        "source_commit": source_commit,
        "plugins": sorted(entries, key=lambda e: e["id"]),
    }
    index_path = out_dir / "_plugins.index.json"
    index_path.write_text(canonical_json(index) + "\n", encoding="utf-8")
    _info(f"Wrote {index_path} ({len(entries)} plugin(s))")

    if had_errors:
        _err("Build/smoke failed for one or more plugins — see errors above.")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugins-dir", default=str(ROOT / "plugins"))
    parser.add_argument("--out", default=str(ROOT / "dist"))
    parser.add_argument(
        "--built-at",
        default=None,
        help="RFC3339 timestamp to embed (default: current UTC time). "
        "CI should pass a stable value derived from the commit for reproducibility.",
    )
    parser.add_argument(
        "--source-commit",
        default="unknown",
        help="Git commit SHA this build was produced from (CI passes $GITHUB_SHA).",
    )
    args = parser.parse_args(argv)

    built_at = args.built_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return build(pathlib.Path(args.plugins_dir), pathlib.Path(args.out), built_at, args.source_commit)


if __name__ == "__main__":
    sys.exit(main())
