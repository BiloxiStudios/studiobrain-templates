#!/usr/bin/env python3
"""Build mirror-manifest.json -- the versioned weights-mirror manifest
consumed by the R2 mirror provisioning/publish pipeline (SBAI-7882) and
verified by scripts/verify_mirror_manifest.py (SBAI-7881, epic SBAI-7842).

Scans every ``templates/Providers/*.provider.yaml`` with ``wire: in-app`` and
flattens each ``weights`` row into one manifest entry: provider id, row id,
source repo, pinned revision, mirror path, license, and the row's
independently-checksummed constituent files. This is a SEPARATE artifact
from catalog-index.json (SBAI-7611) -- that index carries marketplace
badges (wire/runtime/provides), this one carries mirror provenance
(revision/sha256/size/license) that only the R2 publish pipeline and the
app/model-manager download paths need. Conflating them would force every
catalog consumer to parse multi-gigabyte-download checksums it never uses.

Usage:
    python3 scripts/build_mirror_manifest.py
    python3 scripts/build_mirror_manifest.py --generated-at 2026-08-23T00:00:00Z
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROVIDERS_DIR = ROOT / "templates" / "Providers"
DEFAULT_OUT = ROOT / "mirror-manifest.json"
MANIFEST_SCHEMA_VERSION = 1

_WEIGHT_ROW_FIELDS = ("id", "source", "revision", "mirror_path", "license", "license_artifact", "size", "files")


def iter_provider_files(root: pathlib.Path = ROOT):
    """Yield every *.provider.yaml under templates/Providers, in deterministic order."""
    providers_dir = root / "templates" / "Providers"
    if not providers_dir.exists():
        return
    for pattern in ("*.provider.yaml", "*.provider.yml"):
        for path in sorted(providers_dir.rglob(pattern)):
            yield path


def build_entries(root: pathlib.Path = ROOT) -> list[dict[str, Any]]:
    """Parse every wire:in-app provider and return its weights rows, sorted by row id.

    Rows missing the mirror contract fields (revision/mirror_path/license/
    license_artifact/size/files) are skipped, not errored -- that gate is
    scripts/verify_mirror_manifest.py's job (and scripts/validate.py's
    check_requires, SBAI-7881), so a provider mid-backfill does not crash the
    build. The manifest only ever contains complete, checksummed rows.
    """
    if yaml is None:
        raise RuntimeError("pyyaml is required to build the mirror manifest")
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for path in iter_provider_files(root):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise RuntimeError(f"{path}: YAML parse error: {exc}") from exc
        if not isinstance(data, dict) or data.get("wire") != "in-app":
            continue
        provider_id = str(data.get("id") or "")
        for row in data.get("weights") or []:
            if not isinstance(row, dict):
                continue
            if not all(row.get(field) for field in _WEIGHT_ROW_FIELDS):
                continue
            row_id = str(row["id"])
            if row_id in seen_ids:
                raise RuntimeError(f"{path}: duplicate weights row id {row_id!r} across the mirror manifest")
            seen_ids.add(row_id)
            files = [
                {"name": str(f["name"]), "sha256": str(f["sha256"]), "size": int(f["size"])}
                for f in row.get("files") or []
            ]
            entries.append({
                "id": row_id,
                "provider": provider_id,
                "provider_path": path.relative_to(root).as_posix(),
                "source": str(row["source"]),
                "revision": str(row["revision"]),
                "mirror_path": str(row["mirror_path"]),
                "license": str(row["license"]),
                "license_artifact": str(row["license_artifact"]),
                "size": int(row["size"]),
                "files": files,
            })
    entries.sort(key=lambda e: e["id"])
    return entries


def default_generated_at(root: pathlib.Path = ROOT) -> str:
    """HEAD commit timestamp (deterministic per commit), else wall clock."""
    try:
        out = subprocess.run(
            ["git", "show", "-s", "--format=%cI", "HEAD"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        stamp = datetime.fromisoformat(out)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        stamp = datetime.now(timezone.utc)
    return stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_manifest(generated_at: str, root: pathlib.Path = ROOT) -> dict[str, Any]:
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at,
        "objects": build_entries(root),
    }


def render(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build mirror-manifest.json (weights mirror provenance manifest).")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output path (default: mirror-manifest.json at the repo root).")
    parser.add_argument(
        "--generated-at",
        help="ISO-8601 UTC timestamp for generated_at. Default: HEAD commit timestamp, falling back to wall clock.",
    )
    args = parser.parse_args(argv)

    generated_at = args.generated_at or default_generated_at()
    manifest = build_manifest(generated_at)
    out = pathlib.Path(args.out)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(manifest))

    total_bytes = sum(e["size"] for e in manifest["objects"])
    print(f"wrote {out}: {len(manifest['objects'])} objects, {total_bytes / 1_000_000_000:.2f} GB total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
