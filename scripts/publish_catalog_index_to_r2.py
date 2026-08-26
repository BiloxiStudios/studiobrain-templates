#!/usr/bin/env python3
"""Upload catalog-index.json to Cloudflare R2 (SBAI-7611 / SBAI-7665).

This is the templates catalog badge index, not the signed plugin index.
The object is mutable: every successful publish overwrites
``catalog/catalog-index.json``.

After PUT, the job witnesses the write: HeadObject must return an ETag,
S3 GetObject must match the local bytes, and (when R2_PUBLIC_BASE_URL is
set) a CDN GET must return the same body.

Only invoked from the push-to-main / hourly-schedule job. Validate and
pull_request jobs must never receive these credentials.

Requires: pip install boto3
Requires env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
Optional env: R2_BUCKET (default: sb-content)
Optional env: R2_PUBLIC_BASE_URL (CDN GET witness, e.g. https://pub-….r2.dev)
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
import urllib.error
import urllib.request


DEFAULT_KEY = "catalog/catalog-index.json"
CDN_USER_AGENT = "studiobrain-catalog-publish/1.0"


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(msg)


def make_client(account_id: str, access_key: str, secret_key: str):
    import boto3  # type: ignore

    # boto3 1.36+ defaults to CRC32 request checksums. R2 answers AccessDenied.
    os.environ.setdefault("AWS_REQUEST_CHECKSUM_CALCULATION", "when_required")
    os.environ.setdefault("AWS_RESPONSE_CHECKSUM_VALIDATION", "when_required")

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def _strip_etag(value: object) -> str:
    return str(value or "").strip().strip('"')


def witness_s3(client, bucket: str, key: str, body: bytes) -> str:
    head = client.head_object(Bucket=bucket, Key=key)
    etag = _strip_etag(head.get("ETag"))
    if not etag:
        raise RuntimeError(f"publish witness: missing ETag after PUT s3://{bucket}/{key}")
    got = client.get_object(Bucket=bucket, Key=key)["Body"].read()
    if got != body:
        raise RuntimeError(
            f"publish witness: S3 read-back mismatch for s3://{bucket}/{key} "
            f"(put {len(body)} bytes, got {len(got)})"
        )
    _info(f"witness s3 etag={etag} bytes={len(got)}")
    return etag


def witness_cdn(public_base_url: str, key: str, body: bytes) -> str:
    url = f"{public_base_url.rstrip('/')}/{key.lstrip('/')}"
    req = urllib.request.Request(url, headers={"User-Agent": CDN_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            cdn_etag = _strip_etag(resp.headers.get("ETag"))
            cdn_body = resp.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"publish witness: CDN GET {url} HTTP {exc.code}") from exc
    if cdn_body != body:
        raise RuntimeError(
            f"publish witness: CDN GET body mismatch for {url} "
            f"(put {len(body)} bytes, got {len(cdn_body)})"
        )
    _info(f"witness cdn etag={cdn_etag or '(none)'} url={url}")
    return cdn_etag


def publish(
    local_path: pathlib.Path,
    key: str,
    bucket: str,
    account_id: str,
    access_key: str,
    secret_key: str,
    public_base_url: str | None = None,
    content_type: str = "application/json",
) -> int:
    if not local_path.is_file():
        _err(f"{local_path} not found")
        return 1

    body = local_path.read_bytes()
    client = make_client(account_id, access_key, secret_key)
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
        CacheControl="public, max-age=60",
    )
    _info(f"published (overwrite): s3://{bucket}/{key}")
    try:
        witness_s3(client, bucket, key, body)
        if public_base_url:
            witness_cdn(public_base_url, key, body)
    except RuntimeError as exc:
        _err(str(exc))
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="catalog-index.json")
    parser.add_argument("--key", default=DEFAULT_KEY)
    parser.add_argument("--content-type", default="application/json",
                        help="MIME type for the uploaded object (default: application/json)")
    parser.add_argument("--bucket", default=os.environ.get("R2_BUCKET", "sb-content"))
    parser.add_argument(
        "--public-base-url",
        default=os.environ.get("R2_PUBLIC_BASE_URL", ""),
        help="CDN origin for GET witness (or R2_PUBLIC_BASE_URL)",
    )
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
        public_base_url=args.public_base_url or None,
        content_type=args.content_type,
    )


if __name__ == "__main__":
    sys.exit(main())
