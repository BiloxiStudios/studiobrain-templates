"""Check that the shipped Biome field guide can present the original template."""

import json
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
LAYOUT = ROOT / "templates/Layouts/biome.layout.json"
TEMPLATE = ROOT / "templates/Standard/BIOME_TEMPLATE.md"


class BiomeFieldGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = json.loads(LAYOUT.read_text())
        cls.template = yaml.safe_load(TEMPLATE.read_text().split("---", 2)[1])
        view = cls.layout["view_config"]
        cls.sections = {
            section["id"]: section for section in cls.layout["sections"] + view["view_only_sections"]
        }
        cls.tabs = {tab["id"]: tab["content"]["section_ids"] for tab in view["tabs"]}

    def test_each_template_season_has_its_own_selectable_section(self):
        season_sections = [self.sections[key] for key in self.tabs["seasons"]]
        expected = {f"seasonal_changes.{season}" for season in self.template["seasonal_changes"]}
        self.assertEqual({section["fields"][0]["key"] for section in season_sections}, expected)
        self.assertEqual(len(season_sections), len(expected))
        for section in season_sections:
            self.assertTrue(section["title"].strip())
            self.assertTrue(section["collapsed_default"])

    def test_guide_reads_the_authored_palette_location_and_narrative(self):
        guide = [self.sections[key] for key in self.tabs["guide"]]
        fields = {field["key"]: field for section in guide for field in section.get("fields", [])}
        self.assertTrue(fields.keys() <= self.template.keys())
        self.assertEqual(fields["dominant_colors"]["ui_component"], "color-group")
        self.assertEqual(fields["parent_location"]["reference_type"], "location")
        blocks = {section.get("component") for section in guide}
        self.assertIn("markdown-content", blocks)
        media_blocks = {self.sections[key].get("component") for key in self.tabs["media"]}
        self.assertTrue({"primary-image", "entity-assets"} <= media_blocks)

    def test_every_authored_section_remains_reachable_from_the_detail_view(self):
        self.assertEqual({key for keys in self.tabs.values() for key in keys}, self.sections.keys())
