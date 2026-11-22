"""A pack's `rulesets` must name catalog rulesets (SBAI-15328)."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import validate


class PackRulesets(unittest.TestCase):
    def test_known_id_passes_and_unknown_id_is_reported(self):
        pack_file = validate.TEMPLATES_DIR / "Packs" / "theme-anime-manga" / "pack.json"
        manifest = json.loads(pack_file.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest["rulesets"]), 2)
        self.assertEqual(validate.check_pack_rulesets(pack_file, manifest), [])
        errors = validate.check_pack_rulesets(pack_file, {"rulesets": ["NOT_A_RULESET"]})
        self.assertEqual(len(errors), 1)
        self.assertIn("NOT_A_RULESET", errors[0])

    def test_every_theme_pack_is_indexed_and_resolves(self):
        packs = validate.TEMPLATES_DIR / "Packs"
        indexed = {e["id"] for e in json.loads((packs / "index.json").read_text(encoding="utf-8"))}
        themed = [p for p in sorted(packs.glob("theme-*/pack.json"))]
        self.assertGreaterEqual(len(themed), 10)
        for pack_file in themed:
            manifest = json.loads(pack_file.read_text(encoding="utf-8"))
            self.assertIn(manifest["id"], indexed)
            self.assertEqual(validate.check_pack_rulesets(pack_file, manifest), [])


if __name__ == "__main__":
    unittest.main()
