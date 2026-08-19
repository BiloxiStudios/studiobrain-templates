#!/usr/bin/env python3
"""Publish a staged plugin build (``dist/``) to Cloudflare R2 (SBAI-7183).

Only ever invoked from the push-to-main publish job — see
``scripts/check_workflow_secret_isolation.py`` for the automated check that
this job (and therefore this script's credentials) is unreachable from any
pull_request-triggered workflow run.

Bucket / key layout follows the owner-approved ruling in
PLUGIN-ARCHITECTURE-DESIGN.md Q3 (sb-cf, 2026-08-16): one shared bucket,
kind-prefixed keys — ``plugins/<id>/<version>/...`` for this pipeline.

Immutability: a version, once published, must never change. Before
uploading any object this script HEADs it; if it already exists with a
DIFFERENT sha256 than what's about to be uploaded, the publish FAILS HARD
(the fix is to bump the plugin version, not overwrite a shipped one). If the
object exists with an IDENTICAL sha256, the upload is skipped (idempotent —
re-running the workflow on the same commit is safe).

The signed index (``_plugins.index.json``) is the one object in this
pipeline that IS mutable — it always reflects the latest known-good state,
so it's just overwritten every publish.

Requires: pip install boto3
Requires env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
Optional env: R2_BUCKET (default: sb-content)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(msg)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def make_client(account_id: str, access_key: str, secret_key: str):
    import boto3  # type: ignore

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def existing_sha256(client, bucket: str, key: str) -> str | None:
    from botocore.exceptions import ClientError  # type: ignore

    try:
        head = client.head_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("404", "NoSuchKey", "NotFound"):
            return None
        raise
    return head.get("Metadata", {}).get("sha256")


def publish_versioned_object(client, bucket: str, key: str, local_path: pathlib.Path) -> str:
    """Publish an immutable, versioned artifact. Returns 'uploaded' | 'skipped-identical'."""
    new_sha = sha256_file(local_path)
    prior_sha = existing_sha256(client, bucket, key)

    if prior_sha is not None:
        if prior_sha == new_sha:
            return "skipped-identical"
        raise RuntimeError(
            f"IMMUTABILITY VIOLATION: {key} already exists in {bucket} with "
            f"sha256={prior_sha}, but this build would publish sha256={new_sha}. "
            f"A published plugin version must never change — bump the version instead."
        )

    client.upload_file(
        str(local_path),
        bucket,
        key,
        ExtraArgs={
            "Metadata": {"sha256": new_sha},
            "CacheControl": "public, max-age=31536000, immutable",
        },
    )
    return "uploaded"


def publish(dist_dir: pathlib.Path, bucket: str, account_id: str, access_key: str, secret_key: str) -> int:
    plugins_dir = dist_dir / "plugins"
    index_path = dist_dir / "_plugins.index.json"

    if not index_path.exists():
        _err(f"{index_path} not found — run scripts/build_plugin_artifacts.py first")
        return 1
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if "signature" not in index:
        _err(f"{index_path} is not signed — run scripts/sign_index.py first")
        return 1

    client = make_client(account_id, access_key, secret_key)

    uploaded = 0
    skipped = 0
    for plugin in index.get("plugins", []):
        plugin_id, version = plugin["id"], plugin["version"]
        local_dir = plugins_dir / plugin_id / version
        if not local_dir.exists():
            _err(f"{local_dir} missing from staged build for {plugin_id}@{version}")
            return 1
        for local_path in sorted(local_dir.rglob("*")):
            if not local_path.is_file():
                continue
            rel = local_path.relative_to(plugins_dir)
            key = f"plugins/{rel.as_posix()}"
            result = publish_versioned_object(client, bucket, key, local_path)
            _info(f"  {result}: {key}")
            if result == "uploaded":
                uploaded += 1
            else:
                skipped += 1

    # The index itself is mutable — always overwrite with the freshest signed copy.
    index_key = "plugins/_plugins.index.json"
    client.put_object(
        Bucket=bucket,
        Key=index_key,
        Body=index_path.read_bytes(),
        ContentType="application/json",
        CacheControl="public, max-age=60",
    )
    _info(f"  published (overwrite): {index_key}")

    _info(f"Done: {uploaded} artifact(s) uploaded, {skipped} already present and identical.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--bucket", default=os.environ.get("R2_BUCKET", "sb-content"))
    args = parser.parse_args(argv)

    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    missing = [
        name
        for name, val in (
            ("R2_ACCOUNT_ID", account_id),
            ("R2_ACCESS_KEY_ID", access_key),
            ("R2_SECRET_ACCESS_KEY", secret_key),
        )
        if not val
    ]
    if missing:
        _err(f"missing required env var(s): {', '.join(missing)}")
        return 1

    return publish(pathlib.Path(args.dist), args.bucket, account_id, access_key, secret_key)


if __name__ == "__main__":
    sys.exit(main())
