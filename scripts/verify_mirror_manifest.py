#!/usr/bin/env python3
"""Deterministic sync/verify workflow for the on-device weights mirror
manifest (SBAI-7881, epic SBAI-7842).

This is the producer-side contract: studiobrain-templates owns the catalog
(the on-device weights rows) and this script proves the catalog is fit to
mirror, BEFORE the R2 bucket exists (SBAI-7882) and independent of it. It
never touches a live bucket -- structural checks run entirely against the
YAML on disk (or an in-memory manifest), and the staging-set check consumes
a plain JSON file of object keys, not a live API. That is what keeps this
script's own test suite free of any production bucket mutation.

Checks (fail-closed -- any violation is an ERROR, exit 1):

  1. Every wire:in-app weights row's mirror fields are internally consistent:
     - revision is a full 40-hex commit SHA (refuses 'main', 'latest', short
       SHAs, or anything else that is not an immutable pin).
     - license is in the redistributable allow-list (refuses apple-amlr and
       anything else not explicitly cleared -- SBAI-7726's FastVLM-exclusion
       doctrine, enforced here rather than left to comment discipline).
     - license_artifact points at a file that exists on disk.
     - every files[] entry has a 64-hex sha256 and a positive size, and the
       row's own 'size' equals the sum of its files' sizes (catches drift
       between a hand-edited total and the real per-file numbers).
     - no two rows publish the same (mirror_path + filename) object key with
       DIFFERENT content (same key, same bytes is fine and expected: sibling
       dtype rows on the same source+revision legitimately share a mirror
       prefix).

  2. --staging PATH: every manifest object's key (mirror_path + file name)
     must appear in the staging set named by PATH (a JSON file shaped
     {"objects": ["<key>", ...]}) -- catches a catalog row that was added
     (or a file that was renamed) without a corresponding mirror sync. This
     is how "refuses a catalog row absent from the mirror staging set" is
     satisfied without this repo ever calling R2: the staging set is
     produced by whatever process actually syncs the bucket (SBAI-7882) and
     handed to this script as a file, real or fixture.

  3. --verify-remote: re-fetches each file's sha256/size from the HF API and
     confirms the pinned values still match, and that 'revision' still
     resolves. Network-dependent and NOT part of the CI gate (scripts/
     validate.py never passes this flag) -- it is a maintenance command a
     human/agent runs when re-pinning or auditing drift.

Usage:
    python3 scripts/verify_mirror_manifest.py                      # structural check, no network, no bucket
    python3 scripts/verify_mirror_manifest.py --staging staged.json # + staging-set completeness
    python3 scripts/verify_mirror_manifest.py --verify-remote       # + live HF re-verification (network)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent

_ALLOWED_LICENSES = {"apache-2.0", "mit"}
_REVISION_RE = __import__("re").compile(r"^[0-9a-f]{40}$")
_SHA256_RE = __import__("re").compile(r"^[0-9a-f]{64}$")


def _load_build_mirror_manifest():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_mirror_manifest", pathlib.Path(__file__).resolve().parent / "build_mirror_manifest.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def check_structural(entries: list[dict[str, Any]], root: pathlib.Path = ROOT) -> list[str]:
    """Structural checks: no network, no bucket -- pure data validation."""
    errors: list[str] = []
    objects: dict[str, tuple[str, int, str]] = {}  # key -> (sha256, size, first row id)

    for entry in entries:
        row_id = entry.get("id", "<unknown>")
        revision = str(entry.get("revision") or "")
        if not _REVISION_RE.match(revision):
            errors.append(
                f"{row_id}: revision {revision!r} is not an immutable pin -- expected a full "
                "40-hex commit SHA, never a branch/tag such as 'main' or 'latest'"
            )

        license_id = str(entry.get("license") or "")
        if license_id not in _ALLOWED_LICENSES:
            errors.append(
                f"{row_id}: license {license_id!r} is not in the redistributable allow-list "
                f"({sorted(_ALLOWED_LICENSES)}) -- refused fail-closed"
            )

        license_artifact = str(entry.get("license_artifact") or "")
        if not license_artifact:
            errors.append(f"{row_id}: missing license_artifact")
        elif not (root / license_artifact).is_file():
            errors.append(f"{row_id}: license_artifact {license_artifact!r} does not exist on disk")

        mirror_path = str(entry.get("mirror_path") or "")
        if not mirror_path:
            errors.append(f"{row_id}: missing mirror_path")

        files = entry.get("files") or []
        if not files:
            errors.append(f"{row_id}: no files declared -- nothing to mirror or checksum")

        files_total = 0
        for f in files:
            name = str(f.get("name") or "")
            sha256 = str(f.get("sha256") or "")
            size = f.get("size")
            if not name:
                errors.append(f"{row_id}: a files[] entry has an empty name")
            if not _SHA256_RE.match(sha256):
                errors.append(f"{row_id}: files[{name!r}].sha256 {sha256!r} is not 64 lowercase hex characters")
            if not isinstance(size, int) or size < 1:
                errors.append(f"{row_id}: files[{name!r}].size {size!r} must be a positive integer")
                size = 0
            files_total += size

            if mirror_path and name:
                key = f"{mirror_path}{name}"
                prior = objects.get(key)
                if prior is not None and prior[:2] != (sha256, size):
                    errors.append(
                        f"{row_id}: object key {key!r} collides with row {prior[2]!r} at a "
                        f"DIFFERENT sha256/size -- two rows must never publish the same mirror "
                        "path + filename with different content"
                    )
                objects[key] = (sha256, size, row_id)

        declared_size = entry.get("size")
        if files and isinstance(declared_size, int) and declared_size != files_total:
            errors.append(
                f"{row_id}: size {declared_size} does not equal the sum of files[].size "
                f"({files_total}) -- one of the two was hand-edited out of sync"
            )

    return errors


def check_staging(entries: list[dict[str, Any]], staging_path: pathlib.Path) -> list[str]:
    """Refuse any manifest object absent from the staging set at staging_path.

    staging_path holds {"objects": ["<mirror_path><file name>", ...]} -- the
    set of keys some external process (real or fixture) says are actually
    staged for/present in the mirror. This function never calls a bucket
    API; it only compares two in-memory sets.
    """
    try:
        staged = json.loads(staging_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{staging_path}: cannot read staging set: {exc}"]
    staged_objects = set(staged.get("objects") or [])

    errors: list[str] = []
    for entry in entries:
        row_id = entry.get("id", "<unknown>")
        mirror_path = str(entry.get("mirror_path") or "")
        for f in entry.get("files") or []:
            key = f"{mirror_path}{f.get('name', '')}"
            if key not in staged_objects:
                errors.append(
                    f"{row_id}: object {key!r} is in the catalog manifest but absent from the "
                    f"mirror staging set ({staging_path}) -- sync it before this row can ship"
                )
    return errors


def check_remote(entries: list[dict[str, Any]], timeout: float = 15.0) -> list[str]:
    """Re-fetch each file's sha256/size from HF and confirm no drift. Network-dependent."""
    errors: list[str] = []
    for entry in entries:
        row_id = entry.get("id", "<unknown>")
        source = str(entry.get("source") or "")
        if not source.startswith("huggingface://"):
            continue
        repo = source[len("huggingface://"):]
        revision = str(entry.get("revision") or "")
        for f in entry.get("files") or []:
            name = str(f.get("name") or "")
            url = f"https://huggingface.co/{repo}/resolve/{revision}/{name}"
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                    headers = resp.headers
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{row_id}: HEAD {url} failed: {exc}")
                continue
            etag = (headers.get("x-linked-etag") or headers.get("etag") or "").strip('"')
            remote_size = headers.get("x-linked-size") or headers.get("content-length")
            if etag and etag != f.get("sha256"):
                errors.append(
                    f"{row_id}: {name} sha256 drifted -- manifest has {f.get('sha256')}, "
                    f"HF now reports {etag} at pinned revision {revision}"
                )
            if remote_size and int(remote_size) != f.get("size"):
                errors.append(
                    f"{row_id}: {name} size drifted -- manifest has {f.get('size')}, "
                    f"HF now reports {remote_size} at pinned revision {revision}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--manifest",
        help="Verify a specific mirror-manifest.json instead of rebuilding from templates/Providers/*.provider.yaml.",
    )
    parser.add_argument(
        "--staging",
        help="Path to a JSON staging-set file ({\"objects\": [...]}); refuses any manifest object absent from it.",
    )
    parser.add_argument(
        "--verify-remote",
        action="store_true",
        help="Also re-fetch sha256/size from the HF API and confirm no drift (network; not run in CI).",
    )
    args = parser.parse_args(argv)

    if args.manifest:
        manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
        entries = manifest.get("objects") or []
    else:
        entries = _load_build_mirror_manifest().build_entries(ROOT)

    errors = check_structural(entries)
    if args.staging:
        errors.extend(check_staging(entries, pathlib.Path(args.staging)))
    if args.verify_remote:
        errors.extend(check_remote(entries))

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"\n{len(errors)} mirror-manifest violation(s).", file=sys.stderr)
        return 1

    print(f"mirror manifest OK: {len(entries)} object row(s) verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
