"""Template-driven auto-layout data checks in scripts/validate.py (SBAI-15043).

Users define their own entity types, so a brand-new custom template (any
slug, no layout, no per-type schema) must validate. Shipped data must use
canonical widget ids from the exported core registry
(schemas/registry/widget-ids.json), and ``views`` must name real fields.
Each ERROR branch is proven on synthetic input, and the shipped templates and
layouts are proven clean.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import validate  # noqa: E402

import yaml  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
REGISTRY = validate.load_widget_registry()

CUSTOM_VEHICLE = """---
template_version: "1.0"
template_category: "entity"
entity_type: "vehicle"
ui_icon: "Car"
ui_color: "#0ea5e9"
id: "[snake_case_name]"
field_config:
  photo: {type: image}
  top_speed: {type: number, unit: "km/h", min: 0}
  class: {type: enum, options: [car, truck, bike]}
  status: {type: enum, options: [concept, built]}
  features: {type: tags, allow_custom: true}
  owner: {type: reference, reference_type: character, widget: entity-selector}
  first_seen: {type: date}
views:
  default: board
  enabled: [board, cards, table, calendar, gallery]
  roles: {image: photo, badges: [class, status], card_fields: [top_speed]}
  board: {group_by: status}
  calendar: {date_field: first_seen}
  sort: {default: "-updated", options: [name, top_speed]}
  facets: [class, features]
name: "Vehicle Display Name"
photo: ""
top_speed: 0
class: car
status: concept
features: []
owner: ""
first_seen: ""
---
# Vehicle
"""


def _fm(text: str) -> dict:
    return yaml.safe_load(text.split("---", 2)[1])


class CustomTemplateTests(unittest.TestCase):
    def test_custom_slug_template_validates_with_no_layout_or_type_schema(self) -> None:
        self.assertFalse((ROOT / "schemas" / "vehicle.json").exists())
        self.assertEqual(validate.template_errors(_fm(CUSTOM_VEHICLE), "vehicle", REGISTRY), [])

    def test_slug_rules(self) -> None:
        for good in ("vehicle", "star_system", "level_3d", "npc2"):
            fm = {"entity_type": good, "template_category": "entity"}
            self.assertEqual(validate.template_errors(fm, good, REGISTRY), [], good)
        for bad in ("Vehicle", "star-system", "3d_level", "_x", ""):
            fm = {"entity_type": bad, "template_category": "entity"}
            self.assertTrue(validate.template_errors(fm, bad, REGISTRY), bad)

    def test_template_category_is_the_five_value_enum(self) -> None:
        for good in ("entity", "document", "map", "rule", "skill"):
            fm = {"entity_type": "x", "template_category": good}
            self.assertEqual(validate.template_errors(fm, good, REGISTRY), [], good)
        for bad in ("core", "system", "docs"):
            fm = {"entity_type": "x", "template_category": bad}
            self.assertTrue(validate.template_errors(fm, bad, REGISTRY), bad)

    def test_unknown_field_type_is_open(self) -> None:
        fm = {"entity_type": "x", "template_category": "entity",
              "field_config": {"orbit": {"type": "orbital_elements"}}}
        self.assertEqual(validate.template_errors(fm, "x", REGISTRY), [])


class WidgetLintTests(unittest.TestCase):
    def test_canonical_and_plugin_ids_pass(self) -> None:
        for widget in ("text", "select", "entity-multiselect", "color-picker",
                       "plugin:garage:spec-sheet"):
            self.assertEqual(validate.lint_widget_id(widget, REGISTRY, "f"), [], widget)

    def test_alias_is_flagged_with_its_canonical_id(self) -> None:
        cases = {
            "dropdown": "select",
            "tag-list": "tag-input",
            "color": "color-picker",
            "color-select": "color-picker",
            "skin-tone-palette": "color-palette",
            "entity-multi-selector": "entity-multiselect",
            "read-only-text": "read-only",
        }
        for alias, canonical in cases.items():
            errs = validate.lint_widget_id(alias, REGISTRY, "f")
            self.assertEqual(len(errs), 1, alias)
            self.assertIn(repr(canonical), errs[0])

    def test_unknown_and_empty_ids_are_flagged(self) -> None:
        self.assertIn("unknown widget id", validate.lint_widget_id("image-upload", REGISTRY, "f")[0])
        self.assertTrue(validate.lint_widget_id("", REGISTRY, "f"))
        self.assertTrue(validate.lint_widget_id("plugin:only-one-part", REGISTRY, "f"))

    def test_template_field_config_widgets_are_linted(self) -> None:
        fm = {"entity_type": "x", "template_category": "document",
              "field_config": {"genre": {"widget": "dropdown", "options": ["a"]}}}
        errs = validate.template_errors(fm, "x", REGISTRY)
        self.assertEqual(len(errs), 1)
        self.assertIn("field_config.genre.widget", errs[0])

    def test_layout_widgets_sub_fields_and_components_are_linted(self) -> None:
        layout = {
            "entity_type": "x", "version": "1.0",
            "sections": [
                {"id": "a", "fields": [
                    {"key": "k", "ui_component": "color"},
                    {"key": "rows", "ui_component": "object-array",
                     "sub_fields": [{"key": "c", "ui_component": "tag-list"}, {"key": "d"}]},
                ]},
                {"id": "b", "component": "entity-gizmo"},
                {"id": "c", "component": "plugin:time-tracker:time-log"},
            ],
        }
        errs = validate.layout_errors(layout, "x", REGISTRY)
        self.assertEqual(len(errs), 3, errs)
        self.assertTrue(any("'color-picker'" in e for e in errs))
        self.assertTrue(any("sub_fields[0]" in e and "'tag-input'" in e for e in errs))
        self.assertTrue(any("entity-gizmo" in e for e in errs))


class ViewsSemanticsTests(unittest.TestCase):
    def test_default_must_be_enabled(self) -> None:
        errs = validate.check_views_semantics(
            {"default": "board", "enabled": ["cards", "table"]}, {"name"}, "x", REGISTRY)
        self.assertEqual(len(errs), 1)
        self.assertIn("not in views.enabled", errs[0])

    def test_unknown_field_references_are_flagged(self) -> None:
        views = {
            "roles": {"image": "portrait", "badges": ["faction"]},
            "table": {"columns": ["name", {"key": "rarity"}, "updated"]},
            "board": {"group_by": "stage"},
            "sort": {"default": "-power"},
            "facets": ["faction"],
        }
        errs = validate.check_views_semantics(views, {"name", "faction"}, "x", REGISTRY)
        flagged = sorted(e.split("names unknown field ")[1] for e in errs)
        self.assertEqual(flagged, ["'portrait'", "'power'", "'rarity'", "'stage'"])

    def test_pseudo_keys_and_dotted_paths_are_known(self) -> None:
        views = {"table": {"columns": ["updated", "created", "colors.primary"]},
                 "sort": {"default": "-updated"}}
        self.assertEqual(validate.check_views_semantics(views, {"colors"}, "x", REGISTRY), [])

    def test_cloud_and_plugin_views_are_registered_ids(self) -> None:
        views = {"default": "map", "enabled": ["map", "timeline", "cards", "plugin:x:y"]}
        self.assertEqual(validate.check_views_semantics(views, set(), "x", REGISTRY), [])

    def test_layout_views_may_name_template_fields(self) -> None:
        layout = {"entity_type": "x", "version": "1.0",
                  "sections": [{"id": "a", "fields": [{"key": "name", "ui_component": "text"}]}],
                  "views": {"roles": {"badges": ["rarity"]}}}
        self.assertTrue(validate.layout_errors(layout, "x", REGISTRY))
        self.assertEqual(validate.layout_errors(layout, "x", REGISTRY, {"rarity"}), [])

    def test_grid_fields_must_name_fields(self) -> None:
        fm = {"entity_type": "x", "template_category": "entity", "power": 1,
              "grid_fields": ["power", "speed"]}
        errs = validate.template_errors(fm, "x", REGISTRY)
        self.assertEqual(len(errs), 1)
        self.assertIn("'speed'", errs[0])


class RegistryExportTests(unittest.TestCase):
    def test_export_is_internally_consistent(self) -> None:
        data = json.loads((ROOT / "schemas" / "registry" / "widget-ids.json").read_text())
        widgets = set(data["widgets"])
        self.assertEqual(len(widgets), len(data["widgets"]), "duplicate widget id")
        renderable = widgets | set(data["renderer_only"])
        for alias, target in data["aliases"].items():
            self.assertNotIn(alias, widgets, f"alias {alias!r} shadows a registered id")
            self.assertIn(target, renderable, f"alias {alias!r} -> unregistered {target!r}")
        views_schema = json.loads((ROOT / "schemas" / "views.json").read_text())
        schema_kinds = set(views_schema["$defs"]["viewKind"]["anyOf"][0]["enum"])
        exported = set(data["views"]["core"]) | set(data["views"]["cloud"])
        self.assertEqual(schema_kinds, exported)


class ShippedDataTests(unittest.TestCase):
    def test_shipped_templates_are_clean(self) -> None:
        self.assertEqual(validate.check_templates(REGISTRY), [])

    def test_shipped_layouts_are_clean(self) -> None:
        self.assertEqual(validate.check_layouts(REGISTRY), [])

    def test_spec_layouts_are_layout_driven(self) -> None:
        for name in ("brand", "district", "faction", "item", "location"):
            data = json.loads((ROOT / "templates" / "Layouts" / f"{name}.layout.json").read_text())
            self.assertIs(data.get("view_config", {}).get("layout_driven"), True, name)

    def test_character_age_and_birth_year_are_integers(self) -> None:
        for rel in ("templates/Standard/CHARACTER_TEMPLATE.md",
                    "templates/Packs/starter-characters/templates/CHARACTER_TEMPLATE.md"):
            fm = _fm((ROOT / rel).read_text())
            self.assertIsInstance(fm["age"], int, rel)
            for key in ("age", "birth_year"):
                self.assertEqual(fm["field_config"][key]["type"], "integer", f"{rel} {key}")


if __name__ == "__main__":
    unittest.main()
