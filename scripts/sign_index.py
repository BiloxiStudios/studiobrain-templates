#!/usr/bin/env python3
"""Sign a built ``_plugins.index.json`` with the CI index-signing key (SBAI-7183).

This is a DISTINCT signing domain from the per-plugin trust-tier signature
described in core's ``plugin_signature.rs`` (SBAI-4630, first_party /
trusted_vendor / partner). That signature proves a *plugin* was vetted by
Biloxi and is signed with a private key that lives only in Azure Key Vault,
used only by the commercial ``sb-plugin-sign`` tool — it must never be
reachable from this public, Apache-2.0 repo's CI.

This script signs the *index* — the list of what CI actually built and
published to R2 — so a consumer (core/cloud/desktop) fetching the index from
R2 can detect tampering in transit or at rest, independent of whether any
individual plugin inside it happens to carry a first_party signature. The
private key for THIS signature (``PLUGIN_INDEX_SIGNING_KEY``) is scoped only
to this one purpose and is only ever read in the push-to-main publish job —
see ``scripts/check_workflow_secret_isolation.py``.

Payload format (mirrors core's domain-separated signing payload style):

    studiobrain-plugin-index-signature-v1\\n
    signed_at=<rfc3339>\\n
    index=<canonical JSON of the index with the top-level 'signature' key removed>

Usage:
    python3 scripts/sign_index.py --index dist/_plugins.index.json \\
        --key-id <key-id> --signing-key-b64 "$PLUGIN_INDEX_SIGNING_KEY"

``--signing-key-b64`` is a base64-encoded 32-byte Ed25519 seed. Never pass it
on the command line in a logged context; CI passes it via an env var that is
only exported inside the gated publish job.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import sys

SIGNING_DOMAIN = "studiobrain-plugin-index-signature-v1"


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def signing_payload(canonical_index: str, signed_at: str) -> bytes:
    return f"{SIGNING_DOMAIN}\nsigned_at={signed_at}\nindex={canonical_index}".encode("utf-8")


def sign(index_path: pathlib.Path, key_id: str, signing_key_b64: str, signed_at_override: str | None = None) -> int:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError:
        _err("the 'cryptography' package is required to sign (pip install cryptography)")
        return 1

    index = json.loads(index_path.read_text(encoding="utf-8"))
    index.pop("signature", None)
    canonical = canonical_json(index)

    # Reproducibility (manager review, SBAI-7183): signed_at is pinned to the
    # index's own deterministic `generated_at` (derived from the commit's
    # author timestamp via --built-at) rather than wall-clock signing time, so
    # two sign invocations over the same build output are byte-identical.
    # Override with --signed-at only for explicit local testing.
    signed_at = signed_at_override or index.get("generated_at")
    if not signed_at:
        _err("index has no 'generated_at' to pin signed_at to (run build_plugin_artifacts.py first, or pass --signed-at)")
        return 1
    payload = signing_payload(canonical, signed_at)

    seed = base64.b64decode(signing_key_b64)
    if len(seed) != 32:
        _err(f"signing key must decode to 32 raw bytes, got {len(seed)}")
        return 1
    private_key = Ed25519PrivateKey.from_private_bytes(seed)
    signature = private_key.sign(payload)

    index["signature"] = {
        "alg": "ed25519",
        "key_id": key_id,
        "sig": base64.b64encode(signature).decode("ascii"),
        "signed_digest": sha256_hex(payload),
        "signed_at": signed_at,
    }
    index_path.write_text(canonical_json(index) + "\n", encoding="utf-8")
    print(f"Signed {index_path} with key_id={key_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument(
        "--signing-key-b64",
        required=True,
        help="Base64-encoded 32-byte Ed25519 seed. Pass via env var, never a literal in CI logs.",
    )
    parser.add_argument(
        "--signed-at",
        default=None,
        help="Override the signature timestamp (RFC3339). Default: the index's own deterministic "
        "generated_at, so re-signing the same build output is byte-identical (SBAI-7183).",
    )
    args = parser.parse_args(argv)
    return sign(pathlib.Path(args.index), args.key_id, args.signing_key_b64, args.signed_at)


if __name__ == "__main__":
    sys.exit(main())
