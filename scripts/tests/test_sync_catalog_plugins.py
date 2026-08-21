"""Tests for scripts/sync_catalog_plugins.py (SBAI-7210).

Covers the acceptance bar from the ticket: fail-closed signature/checksum
verification, idempotent re-sync, bounded per-entry failure reporting, and
the request shape matching cloud's PublishPluginRequest contract
(SBAI-7209, crates/sb-cloud/src/routes/catalog.rs). Uses a fake HTTP
transport (no network, no credentials) so these run in every PR job.
"""
from __future__ import annotations

import base64
import json
import pathlib
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

# Real (not importlib-loader) imports: registers the modules in sys.modules
# under these exact names so @patch("sync_catalog_plugins.publish_entry")
# style string-target patching below can resolve them.
import sync_catalog_plugins  # noqa: E402
import sign_index  # noqa: E402

TEST_SEED_B64 = base64.b64encode(bytes(range(32))).decode("ascii")
TEST_KEY_ID = "test-index-key"
TEST_PUBLIC_KEY_B64 = base64.b64encode(
    Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    .public_key()
    .public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
).decode("ascii")


def _entry(entry_id="demo-plugin", **overrides):
    base = {
        "id": entry_id,
        "name": "Demo Plugin",
        "version": "1.0.0",
        "description": "A demo plugin.",
        "author": "Biloxi Studios",
        "category": "utility",
        "manifest_sha256": "a" * 64,
        "capabilities": ["read"],
        "min_host_version": "1.0.0",
        "artifacts": [
            {"path": "panel.html", "sha256": "b" * 64, "url": "https://pub.example/plugins/demo-plugin/1.0.0/panel.html"},
        ],
        "r2_prefix": "plugins/demo-plugin/1.0.0/",
    }
    base.update(overrides)
    return base


def _write_signed_index(dir_: pathlib.Path, plugins: list[dict]) -> tuple[pathlib.Path, pathlib.Path]:
    index_path = dir_ / "_plugins.index.json"
    index_path.write_text(
        json.dumps(
            {
                "index_schema_version": 2,
                "generated_at": "2026-08-21T00:00:00Z",
                "source_commit": "0" * 40,
                "plugins": plugins,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert sign_index.sign(index_path, TEST_KEY_ID, TEST_SEED_B64) == 0

    keys_path = dir_ / "keys.json"
    keys_path.write_text(
        json.dumps({"keys": [{"key_id": TEST_KEY_ID, "public_key": TEST_PUBLIC_KEY_B64}]}),
        encoding="utf-8",
    )
    return index_path, keys_path


class FakeResponse:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class RequestShapeAndContractTests(unittest.TestCase):
    def test_build_publish_request_matches_cloud_contract_fields(self):
        body = sync_catalog_plugins.build_publish_request(_entry())
        self.assertEqual(
            set(body.keys()),
            {"name", "version", "description", "author", "checksum", "source_url", "active", "manifest"},
        )
        self.assertEqual(body["checksum"], "a" * 64)
        self.assertEqual(body["source_url"], "https://pub.example/plugins/demo-plugin/1.0.0/panel.html")
        self.assertTrue(body["active"])
        self.assertIsInstance(body["manifest"], dict)
        # id/name/version/description/author are top-level publish fields,
        # not duplicated inside the opaque manifest blob.
        self.assertNotIn("name", body["manifest"])
        self.assertNotIn("id", body["manifest"])

    def test_missing_artifact_url_falls_back_to_empty_source_url(self):
        entry = _entry(artifacts=[{"path": "x", "sha256": "c" * 64}])
        body = sync_catalog_plugins.build_publish_request(entry)
        self.assertEqual(body["source_url"], "")


class FailClosedTests(unittest.TestCase):
    def test_unsigned_index_aborts_entirely(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path = d / "_plugins.index.json"
            index_path.write_text(json.dumps({"index_schema_version": 2, "generated_at": "x", "plugins": [_entry()]}), encoding="utf-8")
            keys_path = d / "keys.json"
            keys_path.write_text(json.dumps({"keys": [{"key_id": TEST_KEY_ID, "public_key": TEST_PUBLIC_KEY_B64}]}), encoding="utf-8")

            rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)
            self.assertEqual(rc, 1)

    def test_tampered_index_aborts_entirely(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [_entry()])
            doc = json.loads(index_path.read_text(encoding="utf-8"))
            doc["plugins"].append({"id": "injected", "manifest_sha256": "e" * 64})
            index_path.write_text(json.dumps(doc), encoding="utf-8")

            rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)
            self.assertEqual(rc, 1)

    @patch("sync_catalog_plugins.publish_entry")
    def test_entry_missing_checksum_is_refused_but_others_still_publish(self, mock_publish):
        mock_publish.return_value = {"status": "published"}
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            good = _entry("good-plugin")
            bad = _entry("bad-plugin")
            del bad["manifest_sha256"]
            index_path, keys_path = _write_signed_index(d, [good, bad])

            rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)

            self.assertEqual(rc, 1, "a failed entry must make the overall run non-zero")
            mock_publish.assert_called_once()
            self.assertEqual(mock_publish.call_args[0][2], "good-plugin")

    def test_empty_index_is_a_successful_noop(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [])
            rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)
            self.assertEqual(rc, 0)


class IdempotencyTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_rerunning_sync_sends_identical_request_body_and_succeeds_both_times(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"status": "published", "id": "demo-plugin", "kind": "plugins"})
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [_entry()])

            rc1 = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)
            rc2 = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)

            self.assertEqual(rc1, 0)
            self.assertEqual(rc2, 0)
            self.assertEqual(mock_urlopen.call_count, 2)
            req1 = mock_urlopen.call_args_list[0][0][0]
            req2 = mock_urlopen.call_args_list[1][0][0]
            self.assertEqual(req1.data, req2.data, "same index content must produce byte-identical PUT bodies (idempotent rerun)")
            self.assertEqual(req1.full_url, req2.full_url)

    @patch("urllib.request.urlopen")
    def test_put_targets_the_contract_url_and_method(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"status": "published"})
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [_entry("my-id")])
            sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="secret-tok", dry_run=False)

            req = mock_urlopen.call_args[0][0]
            self.assertEqual(req.full_url, "https://cloud.example/api/catalog/plugins/my-id")
            self.assertEqual(req.get_method(), "PUT")
            self.assertEqual(req.get_header("Authorization"), "Bearer secret-tok")
            # Cloudflare Bot Fight Mode (error 1010) blocks the default
            # "Python-urllib/x.y" UA outright — measured live 2026-08-21,
            # the pipeline's first trusted-run attempt 403'd on exactly
            # this. Every request this script makes must set a real UA.
            self.assertEqual(req.get_header("User-agent"), sync_catalog_plugins.USER_AGENT)


class BoundedFailureAndAuthTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_one_rejected_entry_does_not_block_others(self, mock_urlopen):
        def side_effect(req, timeout=None):
            if "bad-plugin" in req.full_url:
                raise urllib.error.HTTPError(req.full_url, 409, "Conflict", {}, None)
            return FakeResponse({"status": "published"})

        mock_urlopen.side_effect = side_effect
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [_entry("good-plugin"), _entry("bad-plugin")])
            rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="t", dry_run=False)

            self.assertEqual(rc, 1)
            self.assertEqual(mock_urlopen.call_count, 2, "both entries must be attempted despite one failing")

    @patch("urllib.request.urlopen")
    def test_auth_rejection_aborts_remaining_entries_immediately(self, mock_urlopen):
        def side_effect(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)

        mock_urlopen.side_effect = side_effect
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [_entry("plugin-a"), _entry("plugin-b"), _entry("plugin-c")])
            rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token="bad-token", dry_run=False)

            self.assertEqual(rc, 1)
            self.assertEqual(mock_urlopen.call_count, 1, "must not retry the same broken credential against every entry")

    def test_dry_run_makes_no_network_call_and_requires_no_token(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            index_path, keys_path = _write_signed_index(d, [_entry()])
            with patch("urllib.request.urlopen") as mock_urlopen:
                rc = sync_catalog_plugins.sync(index_path, keys_path, "https://cloud.example", token=None, dry_run=True)
                self.assertEqual(rc, 0)
                mock_urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
