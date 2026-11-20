"""Ordinary starter templates may describe a project's own risks and conditions."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setting_names import scan_roots


class DefaultTemplateFieldTests(unittest.TestCase):
    def test_detects_sample_fields_and_choices_only_in_default_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stock = root / "templates/Standard"
            sample = root / "templates/Packs/sample-city-of-brains"
            stock.mkdir(parents=True)
            sample.mkdir(parents=True)
            content = (
                'zombie_risk: none\n'
                'infection_status: clean\n'
                '  infected: "25%"\n'
                '{"value": "zombie", "label": "Zombie"}\n'
                'story_significance: "infection vector"\n'
                'activity: "infection prevention research"\n'
                'hazards: []\n'
            )
            (stock / "LOCATION_TEMPLATE.md").write_text(content, encoding="utf-8")
            (sample / "example.md").write_text(content, encoding="utf-8")
            hits = scan_roots(root, ("templates",))
            expected = [
                f"templates/Standard/LOCATION_TEMPLATE.md:{line}: {value.strip()}"
                for line, value in enumerate(content.splitlines()[:5], start=1)
            ]
            self.assertEqual(hits, expected)
