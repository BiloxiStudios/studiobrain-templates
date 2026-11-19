"""Default starter rules and templates must not name one sample setting."""
from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import setting_names  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


class SettingNeutralTests(unittest.TestCase):
    def test_default_packs_do_not_name_the_sample_setting(self):
        hits = setting_names.scan_roots(ROOT)
        self.assertEqual(hits, [], "\n".join(hits[:40]))

    def test_word_list_catches_a_setting_name(self):
        self.assertRegex("a City of Brains street", setting_names._PATTERN)
        self.assertIsNone(setting_names._PATTERN.search("a harbor street in this project"))

    def test_sample_pack_is_outside_the_default_roots(self):
        self.assertNotIn(
            "templates/Packs/sample-city-of-brains",
            setting_names.DEFAULT_RELATIVE_ROOTS,
        )
        self.assertNotIn(
            "templates/Packs/starter-assemblies",
            setting_names.DEFAULT_RELATIVE_ROOTS,
        )

    def test_listed_packs_have_installable_members(self):
        # The picker lists templates/Packs/index.json. A listed pack must
        # carry templates, rules, includes, a templates/ directory, or
        # example files. An examples-only pack stays optional: auto_install
        # and is_default false, so a new project does not receive it.
        # This does not require any one sample pack to remain listed.
        import json

        index = json.loads((ROOT / "templates/Packs/index.json").read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in index]
        self.assertIn("core-essentials", ids)

        for entry in index:
            pack_dir = ROOT / entry["path"]
            pack = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
            tdir = pack_dir / "templates"
            cloud_members = bool(
                pack.get("templates")
                or pack.get("rules")
                or pack.get("includes")
                or (tdir.is_dir() and any(tdir.iterdir()))
            )
            examples = [rel for rel in (pack.get("examples") or []) if isinstance(rel, str) and rel]
            self.assertTrue(
                cloud_members or examples,
                f"{entry['id']}: listed in index.json but has nothing to install",
            )
            if examples and not cloud_members:
                self.assertIs(pack.get("auto_install"), False, entry["id"])
                self.assertIs(pack.get("is_default"), False, entry["id"])
                for rel in examples:
                    self.assertTrue((pack_dir / rel).is_file(), f"{entry['id']}: missing {rel}")

        core = json.loads(
            (ROOT / "templates/Packs/core-essentials/pack.json").read_text(encoding="utf-8")
        )
        self.assertIs(core.get("auto_install"), True)
        self.assertIs(core.get("is_default"), True)


if __name__ == "__main__":
    unittest.main()
