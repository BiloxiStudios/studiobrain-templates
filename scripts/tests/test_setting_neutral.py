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


if __name__ == "__main__":
    unittest.main()
