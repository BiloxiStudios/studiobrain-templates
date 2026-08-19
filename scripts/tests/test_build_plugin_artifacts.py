"""Tests for scripts/build_plugin_artifacts.py (SBAI-7183): exercises the
full build/smoke pipeline against a throwaway v2 plugin fixture so the CI
"build" step is proven to work end-to-end, not just parse without error on
an empty plugins/ directory.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build_plugin_artifacts as build_mod  # noqa: E402

VALID_MANIFEST = {
    "id": "fixture-plugin",
    "name": "Fixture Plugin",
    "version": "0.1.0",
    "description": "Test fixture for the v2 build pipeline.",
    "type": "frontend-only",
    "manifest_version": 2,
    "author": "test",
    "compat": {"min_core_version": "1.2.0"},
    "surfaces": [
        {
            "type": "panel",
            "id": "notes",
            "label": "Notes",
            "artifact": {"path": "frontend/panels/notes.html"},
            "placement": {"location": "entity-sidebar", "order": 1, "icon": "sticky-note"},
            "capabilities": ["entity:read"],
            "permissions": ["entity:read"],
        }
    ],
    "permissions": ["entity:read"],
}


class BuildPluginArtifactsTest(unittest.TestCase):
    def _make_plugin_dir(self, root: pathlib.Path, manifest: dict, artifact_text: str = "<div>notes</div>"):
        plugin_dir = root / manifest["id"]
        (plugin_dir / "frontend" / "panels").mkdir(parents=True)
        (plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        (plugin_dir / "frontend" / "panels" / "notes.html").write_text(artifact_text, encoding="utf-8")
        return plugin_dir

    def test_builds_valid_v2_plugin_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugins_dir.mkdir()
            self._make_plugin_dir(plugins_dir, VALID_MANIFEST)
            out_dir = tmp_path / "dist"

            rc = build_mod.build(plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef")
            self.assertEqual(rc, 0)

            index = json.loads((out_dir / "_plugins.index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(index["plugins"]), 1)
            entry = index["plugins"][0]
            self.assertEqual(entry["id"], "fixture-plugin")
            self.assertEqual(len(entry["artifacts"]), 1)

            # Q3 registry-index completeness (manager review, SBAI-7183):
            # capabilities requested, min host version, per-surface artifact
            # URL/key, and panel placement metadata must all be present.
            self.assertEqual(entry["capabilities"], ["entity:read"])
            self.assertEqual(entry["min_host_version"], "1.2.0")
            artifact = entry["artifacts"][0]
            self.assertEqual(artifact["r2_key"], "plugins/fixture-plugin/0.1.0/frontend/panels/notes.html")
            self.assertEqual(artifact["capabilities"], ["entity:read"])
            self.assertEqual(artifact["placement"]["location"], "entity-sidebar")
            self.assertEqual(artifact["placement"]["order"], 1)
            self.assertIsNone(artifact["url"], "url must be null when no --public-base-url is given")

            staged = out_dir / "plugins" / "fixture-plugin" / "0.1.0"
            self.assertTrue((staged / "plugin.json").exists())
            self.assertTrue((staged / "frontend" / "panels" / "notes.html").exists())
            self.assertTrue((staged / "_checksums.json").exists())

    def test_public_base_url_produces_full_artifact_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugins_dir.mkdir()
            self._make_plugin_dir(plugins_dir, VALID_MANIFEST)
            out_dir = tmp_path / "dist"

            rc = build_mod.build(
                plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef",
                public_base_url="https://pub-example.r2.dev/",
            )
            self.assertEqual(rc, 0)
            index = json.loads((out_dir / "_plugins.index.json").read_text(encoding="utf-8"))
            artifact = index["plugins"][0]["artifacts"][0]
            self.assertEqual(
                artifact["url"],
                "https://pub-example.r2.dev/plugins/fixture-plugin/0.1.0/frontend/panels/notes.html",
            )

    def test_protocol_adapter_manifest_v2_is_rejected_not_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugin_dir = plugins_dir / "wasm-adapter"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "plugin.json").write_text(
                json.dumps(
                    {
                        "id": "wasm-adapter",
                        "name": "WASM Adapter",
                        "version": "0.1.0",
                        "description": "Protocol adapter, not buildable yet.",
                        "type": "protocol-adapter",
                        "manifest_version": 2,
                        "service_type": "video",
                        "exports": {
                            "adapt_request": {},
                            "adapt_response": {},
                            "health_check": {},
                        },
                    }
                ),
                encoding="utf-8",
            )

            out_dir = tmp_path / "dist"
            rc = build_mod.build(plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef")
            self.assertNotEqual(
                rc, 0,
                "a protocol-adapter manifest_version=2 plugin must FAIL the build "
                "(SBAI-7184 not landed yet), not be silently skipped",
            )
            index = json.loads((out_dir / "_plugins.index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["plugins"], [], "the rejected plugin must not appear in the index")

    def test_reproducible_build_same_commit_same_built_at_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugins_dir.mkdir()
            self._make_plugin_dir(plugins_dir, VALID_MANIFEST)

            out_a = tmp_path / "dist-a"
            out_b = tmp_path / "dist-b"
            build_mod.build(plugins_dir, out_a, "2026-01-01T00:00:00Z", "deadbeef")
            build_mod.build(plugins_dir, out_b, "2026-01-01T00:00:00Z", "deadbeef")

            index_a = (out_a / "_plugins.index.json").read_bytes()
            index_b = (out_b / "_plugins.index.json").read_bytes()
            self.assertEqual(
                index_a, index_b,
                "two builds given the SAME --built-at for the SAME commit must "
                "produce a byte-identical index (manager review, SBAI-7183)",
            )

    def test_missing_artifact_file_fails_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugin_dir = plugins_dir / "broken-plugin"
            plugin_dir.mkdir(parents=True)
            manifest = dict(VALID_MANIFEST, id="broken-plugin")
            (plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
            # Deliberately do NOT create frontend/panels/notes.html.

            out_dir = tmp_path / "dist"
            rc = build_mod.build(plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef")
            self.assertNotEqual(rc, 0, "build must fail when a declared artifact is missing")

            index = json.loads((out_dir / "_plugins.index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["plugins"], [], "the broken plugin must not appear in the index")

    def test_empty_artifact_file_fails_smoke_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            self._make_plugin_dir(plugins_dir, VALID_MANIFEST, artifact_text="")

            out_dir = tmp_path / "dist"
            rc = build_mod.build(plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef")
            self.assertNotEqual(rc, 0, "an empty artifact file must fail the smoke test")

    def test_v1_legacy_plugin_is_skipped_not_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugin_dir = plugins_dir / "legacy-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "plugin.json").write_text(
                json.dumps(
                    {
                        "id": "legacy-plugin",
                        "name": "Legacy",
                        "version": "1.0.0",
                        "description": "v1",
                        "type": "full",
                        "capabilities": {},
                    }
                ),
                encoding="utf-8",
            )

            out_dir = tmp_path / "dist"
            rc = build_mod.build(plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef")
            self.assertEqual(rc, 0, "v1 plugins are out of scope, not build failures")
            index = json.loads((out_dir / "_plugins.index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["plugins"], [])

    def test_empty_plugins_dir_produces_empty_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plugins_dir = tmp_path / "plugins"
            plugins_dir.mkdir()
            out_dir = tmp_path / "dist"

            rc = build_mod.build(plugins_dir, out_dir, "2026-01-01T00:00:00Z", "deadbeef")
            self.assertEqual(rc, 0)
            index = json.loads((out_dir / "_plugins.index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["plugins"], [])


if __name__ == "__main__":
    unittest.main()
