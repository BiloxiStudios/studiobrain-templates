"""Unit tests for scripts/sign_index.py (SBAI-7183).

Covers the reproducibility contract from the manager review: signing the
same built index twice with the same key must be byte-identical (signed_at
pinned to the index's deterministic generated_at, never wall-clock), and the
result must verify (and fail to verify after tampering) against
scripts/verify_index_signature.py.
"""
from __future__ import annotations

import base64
import importlib.util
import json
import pathlib
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

TEST_PUBLIC_KEY_B64 = base64.b64encode(
    Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    .public_key()
    .public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
).decode("ascii")

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sign_index = _load("sign_index")
verify_index_signature = _load("verify_index_signature")

# A fixed Ed25519 seed (test-only; generated once, never used anywhere else).
TEST_SEED_B64 = base64.b64encode(bytes(range(32))).decode("ascii")
TEST_KEY_ID = "test-index-key"


def write_index(dir_: pathlib.Path, generated_at: str) -> pathlib.Path:
    p = dir_ / "_plugins.index.json"
    p.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "index_schema_version": 2,
                "source_commit": "0" * 40,
                "plugins": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return p


class SignIndexTests(unittest.TestCase):
    def test_signed_at_pins_to_generated_at(self):
        with tempfile.TemporaryDirectory() as td:
            p = write_index(pathlib.Path(td), "2026-08-19T11:04:40Z")
            self.assertEqual(sign_index.sign(p, TEST_KEY_ID, TEST_SEED_B64), 0)
            sig = json.loads(p.read_text(encoding="utf-8"))["signature"]
            self.assertEqual(sig["signed_at"], "2026-08-19T11:04:40Z")

    def test_same_build_signed_twice_is_byte_identical(self):
        # Manager finding #1: two builds/signs of the same commit must not
        # drift. signed_at comes from generated_at (deterministic --built-at),
        # so the entire signed file is byte-identical.
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            p1 = write_index(pathlib.Path(td1), "2026-08-19T11:04:40Z")
            p2 = write_index(pathlib.Path(td2), "2026-08-19T11:04:40Z")
            self.assertEqual(sign_index.sign(p1, TEST_KEY_ID, TEST_SEED_B64), 0)
            self.assertEqual(sign_index.sign(p2, TEST_KEY_ID, TEST_SEED_B64), 0)
            self.assertEqual(
                p1.read_bytes(),
                p2.read_bytes(),
                "re-signing the same build output must be byte-identical (SBAI-7183 reproducibility)",
            )

    def test_resigning_an_already_signed_index_is_stable(self):
        # The publish job re-signs dist output that may already carry a
        # signature from a previous cycle; the old signature must be replaced
        # deterministically, not stack or drift.
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            p = write_index(d, "2026-08-19T11:04:40Z")
            self.assertEqual(sign_index.sign(p, TEST_KEY_ID, TEST_SEED_B64), 0)
            first = p.read_bytes()
            self.assertEqual(sign_index.sign(p, TEST_KEY_ID, TEST_SEED_B64), 0)
            self.assertEqual(first, p.read_bytes())

    def test_signed_at_override(self):
        with tempfile.TemporaryDirectory() as td:
            p = write_index(pathlib.Path(td), "2026-08-19T11:04:40Z")
            self.assertEqual(sign_index.sign(p, TEST_KEY_ID, TEST_SEED_B64, signed_at_override="2020-01-01T00:00:00Z"), 0)
            sig = json.loads(p.read_text(encoding="utf-8"))["signature"]
            self.assertEqual(sig["signed_at"], "2020-01-01T00:00:00Z")

    def test_missing_generated_at_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "_plugins.index.json"
            p.write_text(json.dumps({"index_schema_version": 2, "plugins": []}) + "\n", encoding="utf-8")
            self.assertEqual(sign_index.sign(p, TEST_KEY_ID, TEST_SEED_B64), 1)

    def test_verify_roundtrip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            p = write_index(d, "2026-08-19T11:04:40Z")
            self.assertEqual(sign_index.sign(p, TEST_KEY_ID, TEST_SEED_B64), 0)
            keys = d / "keys.json"
            keys.write_text(json.dumps({"keys": [{"key_id": TEST_KEY_ID, "public_key": TEST_PUBLIC_KEY_B64}]}), encoding="utf-8")
            self.assertEqual(
                verify_index_signature.main(["--index", str(p), "--keys", str(keys)]), 0,
            )
            # Tamper: append a plugin entry -> digest mismatch -> non-zero exit.
            doc = json.loads(p.read_text(encoding="utf-8"))
            doc["plugins"].append({"id": "evil", "version": "9.9.9"})
            p.write_text(json.dumps(doc) + "\n", encoding="utf-8")
            self.assertNotEqual(
                verify_index_signature.main(["--index", str(p), "--keys", str(keys)]), 0,
            )


if __name__ == "__main__":
    unittest.main()
