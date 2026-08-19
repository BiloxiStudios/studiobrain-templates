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
    "surfaces": [
        {
            "type": "panel",
            "id": "notes",
            "label": "Notes",
            "artifact": {"path": "frontend/panels/notes.html"},
            "placement": {"location": "entity-sidebar"},
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

            staged = out_dir / "plugins" / "fixture-plugin" / "0.1.0"
            self.assertTrue((staged / "plugin.json").exists())
            self.assertTrue((staged / "frontend" / "panels" / "notes.html").exists())
            self.assertTrue((staged / "_checksums.json").exists())

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
