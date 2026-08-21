#!/usr/bin/env python3
"""Sync a signed ``_plugins.index.json`` into the cloud catalog (SBAI-7210).

This is the trusted-publish half of the plugin pipeline started in SBAI-7183
(build/sign/publish-to-R2). Where that pipeline makes plugin artifacts
*downloadable*, this script makes them *discoverable*: it reads the signed
index and idempotently upserts each entry into cloud's catalog via
``PUT /api/catalog/plugins/:id`` (SBAI-7209), so app/desktop/mobile clients
browsing the marketplace see what CI actually built and published.

Trust model — same shape as ``scripts/sign_index.py`` /
``scripts/publish_to_r2.py``, and enforced by the same
``scripts/check_workflow_secret_isolation.py`` CI gate:

  * This script is only ever invoked from the push-to-main publish job, and
    only ever receives a short-lived (15 minute, measured live 2026-08-21
    against accounts.studiobrain.ai) access token minted just-in-time for
    that one run. It is never reachable from a ``pull_request``-triggered
    run, so the credential that mints it — the login password for a
    dedicated, low-privilege "catalog publisher" bot account (an
    otherwise-empty tenant it owns; no billing, no other repo/team access;
    self-registration already gives it ``role: owner``, which is all
    ``is_catalog_admin()`` requires) — is never exposed to PR-controlled
    code. The publish job's own "log in" step (not this script) does
    ``POST /api/auth/login`` fresh every run and hands this script only the
    resulting access token via ``CLOUD_CATALOG_ACCESS_TOKEN``.
    Deliberately NOT the standard interactive refresh-token flow: accounts'
    ``/api/auth/refresh`` enforces reuse-detection rotation (a stale
    refresh token revokes ALL of that user's tokens), which is the right
    model for a browser session but would make an unattended headless CI
    credential self-destruct on its second run if the workflow ever reused
    an old refresh token. A fresh login has no such reuse state to collide
    with, so every run is independent.
  * FAIL CLOSED on integrity: the whole run aborts, publishing NOTHING, if
    the index's Ed25519 signature is missing or does not verify against the
    checked-in trusted-key registry (delegates to
    ``verify_index_signature.verify()`` — the exact same check the publish
    job already runs standalone). A per-entry ``manifest_sha256`` (the
    ``checksum`` field of the publish contract) is also required; an entry
    that lacks one is refused individually rather than silently published
    with an empty/unverifiable checksum.
  * Idempotent: the cloud endpoint is an upsert
    (``ON CONFLICT (id) DO UPDATE``), and this script always sends the same
    deterministic request body for the same index content, so re-running it
    against an unchanged index (a manual rerun, or a push whose commit
    didn't change any plugin) is a safe no-op from the catalog's point of
    view — same response, same end state, every time.
  * Bounded failure reporting: one bad/rejected entry (e.g. a 409 id/kind
    collision) does not abort the whole run — every entry is attempted, and
    the script exits non-zero at the end if *any* entry failed, with a
    per-entry summary of what happened. Authentication failure (401/403) is
    the one exception: it signals a broken credential rather than bad data
    in one entry, so the run aborts immediately rather than repeating the
    same failure once per plugin.

Usage:
    python3 scripts/sync_catalog_plugins.py \\
        --index _plugins.index.json \\
        --cloud-api-base https://api.studiobrain.ai \\
        --token "$CLOUD_CATALOG_ACCESS_TOKEN"

    # Preview the request bodies without making any network call:
    python3 scripts/sync_catalog_plugins.py --index _plugins.index.json --dry-run
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Cloudflare's Bot Fight Mode WAF (error 1010) blocks Python's default
# "Python-urllib/x.y" User-Agent outright — measured live against
# accounts.studiobrain.ai/api.studiobrain.ai 2026-08-21 (first trusted-run
# attempt 403'd on exactly this). A descriptive, identifiable UA is required
# for every request this script makes.
USER_AGENT = "studiobrain-templates-ci/1.0 (+https://github.com/BiloxiStudios/studiobrain-templates)"


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(msg)


def _load_sibling(name: str):
    """Import a sibling script module by path (mirrors scripts/tests/*.py's
    loader) so this file has no package-relative import dependency."""
    spec = importlib.util.spec_from_file_location(name, pathlib.Path(__file__).resolve().parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verify_index_signature = _load_sibling("verify_index_signature")


class AuthError(RuntimeError):
    """Raised when the catalog API rejects the credential itself (401/403),
    as opposed to rejecting one entry's data. Aborts the whole run."""


def build_publish_request(entry: dict[str, Any]) -> dict[str, Any]:
    """Map one ``_plugins.index.json`` entry onto the cloud
    ``PublishPluginRequest`` contract (SBAI-7209,
    ``crates/sb-cloud/src/routes/catalog.rs``). Field names below match that
    struct exactly: ``name``, ``version``, ``description``, ``author``,
    ``checksum``, ``source_url``, ``active``, ``manifest``.
    """
    artifacts = entry.get("artifacts") or []
    source_url = ""
    for artifact in artifacts:
        if artifact.get("url"):
            source_url = artifact["url"]
            break

    # The manifest field is an opaque JSON object as far as the cloud
    # contract is concerned — pass through everything about this build that
    # isn't already a top-level publish field, so downstream consumers can
    # still see capabilities/artifacts/placement without a schema change.
    manifest = {
        k: v
        for k, v in entry.items()
        if k not in ("id", "name", "version", "description", "author")
    }

    return {
        "name": entry.get("name") or entry["id"],
        "version": entry.get("version") or "",
        "description": entry.get("description") or "",
        "author": entry.get("author") or "",
        "checksum": entry["manifest_sha256"],
        "source_url": source_url,
        "active": True,
        "manifest": manifest,
    }


def load_verified_index(index_path: pathlib.Path, keys_path: pathlib.Path) -> dict[str, Any]:
    """Load ``index_path`` and verify its signature. Raises on any failure —
    there is no partial-trust mode. A caller must never publish entries from
    an index this function did not return successfully."""
    rc = verify_index_signature.verify(index_path, keys_path)
    if rc != 0:
        raise RuntimeError(
            f"{index_path} failed signature verification against {keys_path} — "
            f"refusing to sync ANY entries (fail-closed)."
        )
    return json.loads(index_path.read_text(encoding="utf-8"))


def publish_entry(
    cloud_api_base: str,
    token: str,
    entry_id: str,
    body: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    url = f"{cloud_api_base.rstrip('/')}/api/catalog/plugins/{entry_id}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        if exc.code in (401, 403):
            raise AuthError(f"{entry_id}: HTTP {exc.code} — credential rejected: {payload}") from exc
        raise RuntimeError(f"{entry_id}: HTTP {exc.code}: {payload}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{entry_id}: network error: {exc.reason}") from exc


def sync(
    index_path: pathlib.Path,
    keys_path: pathlib.Path,
    cloud_api_base: str,
    token: str | None,
    dry_run: bool,
    timeout: float = 30.0,
) -> int:
    try:
        index = load_verified_index(index_path, keys_path)
    except RuntimeError as exc:
        _err(str(exc))
        return 1
    plugins = index.get("plugins", [])
    _info(f"Verified signed index: {len(plugins)} plugin(s) to sync.")

    if not plugins:
        _info("Nothing to publish (empty index) — trivially successful sync.")
        return 0

    if not dry_run and not token:
        _err("--token (or CLOUD_CATALOG_ACCESS_TOKEN) is required unless --dry-run is passed")
        return 1

    published, failed, skipped = 0, 0, 0
    failures: list[str] = []
    for entry in plugins:
        entry_id = entry.get("id")
        if not entry_id:
            failed += 1
            failures.append("<missing id>: entry has no 'id' field")
            continue
        if not entry.get("manifest_sha256"):
            # Fail-closed per entry: refuse to publish anything we cannot
            # attach a verifiable checksum to, even though the index as a
            # whole verified — an entry missing its own hash is not
            # tamper-evident on its own.
            failed += 1
            failures.append(f"{entry_id}: no manifest_sha256 — refusing to publish (fail-closed)")
            continue

        body = build_publish_request(entry)

        if dry_run:
            _info(f"  [dry-run] would PUT {entry_id}: {json.dumps(body, sort_keys=True)}")
            skipped += 1
            continue

        try:
            result = publish_entry(cloud_api_base, token, entry_id, body, timeout)
        except AuthError as exc:
            # A rejected credential invalidates every remaining entry too —
            # stop immediately instead of repeating the same 401/403 N times.
            _err(str(exc))
            _err("Aborting remaining entries: credential was rejected.")
            return 1
        except RuntimeError as exc:
            failed += 1
            failures.append(str(exc))
            _err(str(exc))
            continue

        published += 1
        _info(f"  published {entry_id}@{body['version']}: {result.get('status', result)}")

    _info(f"Done: {published} published, {failed} failed, {skipped} dry-run.")
    if failures:
        _err("Failures:")
        for f in failures:
            _err(f"  - {f}")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", default=str(ROOT / "_plugins.index.json"))
    parser.add_argument("--keys", default=str(ROOT / "schemas" / "keys" / "plugin-index-trusted-keys.json"))
    parser.add_argument(
        "--cloud-api-base",
        default=os.environ.get("CLOUD_API_BASE_URL", "https://api.studiobrain.ai"),
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("CLOUD_CATALOG_ACCESS_TOKEN"),
        help="Bearer access token for an admin-role catalog publisher account. "
        "Never pass on the command line in a logged CI context — the publish "
        "job exports it as an env var scoped to this one step. Not required "
        "with --dry-run.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    try:
        return sync(
            pathlib.Path(args.index),
            pathlib.Path(args.keys),
            args.cloud_api_base,
            args.token,
            args.dry_run,
            args.timeout,
        )
    except RuntimeError as exc:
        _err(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
