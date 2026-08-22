#!/usr/bin/env python3
"""Upload catalog-index.json to Cloudflare R2 (SBAI-7665).

This is the templates catalog badge index, not the signed plugin index.
The object is mutable: every successful publish overwrites
``catalog/catalog-index.json``.

Only invoked from the push-to-main / hourly-schedule job. Validate and
pull_request jobs must never receive these credentials.

Requires: pip install boto3
Requires env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
Optional env: R2_BUCKET (default: sb-content)
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys


DEFAULT_KEY = "catalog/catalog-index.json"


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(msg)


def make_client(account_id: str, access_key: str, secret_key: str):
    import boto3  # type: ignore

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def publish(local_path: pathlib.Path, key: str, bucket: str, account_id: str, access_key: str, secret_key: str) -> int:
    if not local_path.is_file():
        _err(f"{local_path} not found")
        return 1

    client = make_client(account_id, access_key, secret_key)
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=local_path.read_bytes(),
        ContentType="application/json",
        CacheControl="public, max-age=60",
    )
    _info(f"published (overwrite): s3://{bucket}/{key}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="catalog-index.json")
    parser.add_argument("--key", default=DEFAULT_KEY)
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

    return publish(
        pathlib.Path(args.file),
        args.key,
        args.bucket,
        account_id,
        access_key,
        secret_key,
    )


if __name__ == "__main__":
    sys.exit(main())
