#!/usr/bin/env python3
"""Verify a signed ``_plugins.index.json`` against the trusted index-signing
public key registry (SBAI-7183). Public-key operation only — safe to run in
any CI job, including untrusted pull_request builds, since it never touches
a private key.

Two modes:

  --index <path> --keys <path>
      Verify a real signed index against the public-key registry checked
      into this repo (``schemas/plugin-index-trusted-keys.json``).

  --selftest
      Round-trip proof that sign -> verify actually works, using a freshly
      generated throwaway keypair (never the production key). This is the
      negative/positive evidence the pipeline is exercised on every PR
      without ever needing the real signing secret.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIGNING_DOMAIN = "studiobrain-plugin-index-signature-v1"


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def signing_payload(canonical_index: str, signed_at: str) -> bytes:
    return f"{SIGNING_DOMAIN}\nsigned_at={signed_at}\nindex={canonical_index}".encode("utf-8")


def verify(index_path: pathlib.Path, keys_path: pathlib.Path) -> int:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
    except ImportError:
        _err("the 'cryptography' package is required to verify (pip install cryptography)")
        return 1

    index = json.loads(index_path.read_text(encoding="utf-8"))
    sig_block = index.get("signature")
    if not sig_block:
        _err(f"{index_path}: no 'signature' block present")
        return 1

    registry = json.loads(keys_path.read_text(encoding="utf-8"))
    key_entry = next(
        (k for k in registry.get("keys", []) if k["key_id"] == sig_block.get("key_id")),
        None,
    )
    if key_entry is None:
        _err(f"signing key '{sig_block.get('key_id')}' is not in {keys_path}")
        return 1

    index_without_sig = {k: v for k, v in index.items() if k != "signature"}
    canonical = canonical_json(index_without_sig)
    payload = signing_payload(canonical, sig_block["signed_at"])

    if sha256_hex(payload) != sig_block.get("signed_digest"):
        _err("signed_digest does not match the recomputed payload digest")
        return 1

    pub_bytes = base64.b64decode(key_entry["public_key"])
    public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
    try:
        public_key.verify(base64.b64decode(sig_block["sig"]), payload)
    except InvalidSignature:
        _err("Ed25519 signature verification failed")
        return 1

    print(f"OK: {index_path} verified against key_id={sig_block['key_id']}")
    return 0


def selftest() -> int:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )
    except ImportError:
        _err("the 'cryptography' package is required for --selftest")
        return 1

    private_key = Ed25519PrivateKey.generate()
    seed_b64 = base64.b64encode(
        private_key.private_bytes_raw()
    ).decode("ascii")
    public_key = private_key.public_key()
    pub_b64 = base64.b64encode(public_key.public_bytes_raw()).decode("ascii")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        index_path = tmp_path / "_plugins.index.json"
        keys_path = tmp_path / "keys.json"

        index_path.write_text(
            canonical_json(
                {"index_schema_version": 1, "generated_at": "1970-01-01T00:00:00Z", "plugins": []}
            )
            + "\n",
            encoding="utf-8",
        )
        keys_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "keys": [
                        {
                            "key_id": "selftest-key",
                            "algorithm": "ed25519",
                            "public_key": pub_b64,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        # Sign using the sibling script's exact logic (import, not subprocess,
        # so this stays a pure-python round trip with no PATH dependency).
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import sign_index  # noqa: E402

        rc = sign_index.sign(index_path, "selftest-key", seed_b64)
        if rc != 0:
            _err("selftest: sign_index.sign() failed")
            return 1

        rc = verify(index_path, keys_path)
        if rc != 0:
            _err("selftest: round-trip verification FAILED — signing pipeline is broken")
            return 1

        # Negative control: tampering must break verification.
        tampered = json.loads(index_path.read_text(encoding="utf-8"))
        tampered["plugins"] = [{"id": "injected-by-attacker"}]
        index_path.write_text(canonical_json(tampered) + "\n", encoding="utf-8")
        rc = verify(index_path, keys_path)
        if rc == 0:
            _err(
                "selftest: tampered index PASSED verification — signature is not "
                "tamper-evident, this is a critical bug"
            )
            return 1

    print("OK: selftest passed (sign -> verify roundtrip, tamper detection)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index")
    parser.add_argument("--keys", default=str(ROOT / "schemas" / "keys" / "plugin-index-trusted-keys.json"))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.index:
        parser.error("--index is required unless --selftest is passed")
    return verify(pathlib.Path(args.index), pathlib.Path(args.keys))


if __name__ == "__main__":
    sys.exit(main())
