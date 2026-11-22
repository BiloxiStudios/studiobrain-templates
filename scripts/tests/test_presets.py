"""Catalog generation presets and the packs that list them (SBAI-15331)."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import validate


class Presets(unittest.TestCase):
    def test_catalog_presets_validate_and_match_the_index(self):
        self.assertEqual(validate.check_presets(), [])
        files = list((validate.ROOT / "presets").glob("*.preset.json"))
        self.assertGreaterEqual(len(files), 100)
        media = {json.loads(f.read_text(encoding="utf-8"))["media_type"] for f in files}
        self.assertTrue({"image", "video", "audio"} <= media)

    def test_presets_name_no_provider_or_model(self):
        for path in (validate.ROOT / "presets").glob("*.preset.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("provider", data, path.name)
            self.assertNotIn("model", data, path.name)

    def test_pack_preset_ids_resolve(self):
        pack_file = validate.TEMPLATES_DIR / "Packs" / "theme-anime-manga" / "pack.json"
        manifest = json.loads(pack_file.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest["presets"]), 5)
        self.assertEqual(validate.check_pack_presets(pack_file, manifest), [])
        errors = validate.check_pack_presets(pack_file, {"presets": ["NOT_A_PRESET"]})
        self.assertEqual(len(errors), 1)
        self.assertIn("NOT_A_PRESET", errors[0])


if __name__ == "__main__":
    unittest.main()
