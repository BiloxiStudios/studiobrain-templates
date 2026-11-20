"""Pack authors run these checks on their installable content before publishing."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import validate


class PackValidationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.templates = pathlib.Path(tmp.name) / "templates"
        self.pack = self.templates / "Packs" / "kitchen"
        self.pack.mkdir(parents=True)
        templates_patch = patch.object(validate, "TEMPLATES_DIR", self.templates)
        templates_patch.start()
        self.addCleanup(templates_patch.stop)

    def write(self, name, content):
        file = self.pack / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        return file

    def example(self, kind):
        return f"""---
entity_type: {kind}
id: smoky_tacos
template_version: '1.0'
created_date: '2026-11-19'
last_updated: '2026-11-19'
status: approved
---
"""

    def test_custom_example_and_stock_instance(self):
        self.write("examples/tacos.md", self.example("vegan_recipe"))
        self.write("examples/stock.md", self.example("character").replace("approved", "active"))
        self.write("templates/VEGAN_RECIPE_TEMPLATE.md", "template placeholder")
        self.write("rules/check.md", "rule content")
        self.write("examples/README.md", "author notes")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(validate.check_entity_frontmatter(), [])
        self.assertIn("2 entity", output.getvalue())
        stock = self.pack / "examples/stock.md"
        stock.write_text(stock.read_text().replace("active", "not_a_stock_status"))
        self.assertIn("not_a_stock_status", "\n".join(validate.check_entity_frontmatter()))

    def test_custom_identity_and_required_pack_discriminator(self):
        self.write("examples/invalid.md", self.example("vegan_recipe").replace("smoky_tacos", "Bad ID"))
        self.write("examples/untyped.md", "---\nid: missing_type\n---\n")
        errors = "\n".join(validate.check_entity_frontmatter())
        self.assertIn("Bad ID", errors)
        self.assertIn("untyped.md", errors)

    def test_custom_type_can_share_a_non_entity_schema_name(self):
        self.write("examples/layout.md", self.example("layout"))
        self.assertEqual(validate.check_entity_frontmatter(), [])

    def test_bad_widgets_in_pack_and_manifest_layouts(self):
        manifest = {"layouts": ["forms/card.json", "layouts/nested/detail.json"]}
        self.write("pack.json", json.dumps(manifest))
        section = {"id": "identity", "fields": [{"key": "name", "ui_component": "unknown_widget"}]}
        layout = {"entity_type": "vegan_recipe", "version": "1.0", "sections": [section]}
        self.write("forms/card.json", json.dumps(layout))
        layout["sections"] = []
        layout["view_config"] = {"view_only_sections": [section]}
        self.write("layouts/nested/detail.json", json.dumps(layout))
        errors = validate.check_layouts()
        self.assertEqual(len([e for e in errors if "unknown widget" in e]), 2, errors)
        self.assertTrue(any("view_only_sections" in e and "detail.json" in e for e in errors))

    def test_pack_custom_view_components_resolve(self):
        tab = {"id": "summary", "content": {"type": "component_block", "block_id": "missing-panel"}}
        layout = {"entity_type": "observatory", "version": "1.0", "sections": [],
                  "viewer_component": "missing-viewer", "editor_component": "entity-assets",
                  "view_config": {"tabs": [tab]}, "tabs": [tab]}
        self.write("layouts/observatory.json", json.dumps(layout))
        errors = validate.check_layouts()
        self.assertEqual(sum("missing-panel" in e for e in errors), 2)
        self.assertEqual(sum("missing-viewer" in e for e in errors), 1)
        layout["viewer_component"] = "plugin:charts:viewer"
        tab["content"]["block_id"] = "static-content"
        self.write("layouts/observatory.json", json.dumps(layout))
        self.assertEqual(validate.check_layouts(), [])

    def test_pack_layout_paths_and_invalid_json(self):
        self.write("pack.json", json.dumps({"layouts": ["missing.json", "../../../outside.json"]}))
        self.write("layouts/broken.json", "{")
        errors = "\n".join(validate.check_layouts())
        for name in ["missing.json", "outside.json", "broken.json"]:
            self.assertIn(name, errors)
