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
  table: {columns: [{key: name}, {key: top_speed, display: unit}, {key: updated}]}
  sort: {default: updated, options: [name, top_speed]}
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
        # A leading digit is allowed: the shipped 3D Level map type is
        # `3d_level`, and existing maps store that id (review fix).
        for good in ("vehicle", "star_system", "level_3d", "npc2", "3d_level"):
            fm = {"entity_type": good, "template_category": "entity"}
            self.assertEqual(validate.template_errors(fm, good, REGISTRY), [], good)
        for bad in ("Vehicle", "star-system", "3D_level", "_x", ""):
            fm = {"entity_type": bad, "template_category": "entity"}
            self.assertTrue(validate.template_errors(fm, bad, REGISTRY), bad)

    def test_template_category_is_the_five_value_enum(self) -> None:
        for good in ("entity", "document", "map", "rule", "skill"):
            fm = {"entity_type": "x", "template_category": good}
            self.assertEqual(validate.template_errors(fm, good, REGISTRY), [], good)
        for bad in ("core", "system", "docs"):
            fm = {"entity_type": "x", "template_category": bad}
            self.assertTrue(validate.template_errors(fm, bad, REGISTRY), bad)

    def test_template_category_is_optional(self) -> None:
        # Core defaults a missing category to `entity`; user, community and
        # legacy templates without the key must validate.
        self.assertEqual(validate.template_errors({"entity_type": "vehicle"}, "x", REGISTRY), [])

    def test_template_fixture_passes_the_views_lint(self) -> None:
        fm = json.loads((ROOT / "schemas" / "fixtures" / "valid_template_custom_vehicle.json").read_text())
        self.assertEqual(validate.template_errors(fm, "fixture", REGISTRY), [])

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
            "table": {"columns": [{"key": "name"}, {"key": "rarity"}, {"key": "updated"}]},
            "board": {"group_by": "stage"},
            "sort": {"default": "power"},
            "facets": ["faction"],
        }
        errs = validate.check_views_semantics(views, {"name", "faction"}, "x", REGISTRY)
        flagged = sorted(e.split("names unknown field ")[1] for e in errs)
        self.assertEqual(flagged, ["'portrait'", "'power'", "'rarity'", "'stage'"])

    def test_updated_is_virtual_and_meta_keys_are_not_fields(self) -> None:
        views = {"table": {"columns": [{"key": "updated"}]}, "sort": {"default": "updated"}}
        self.assertEqual(validate.check_views_semantics(views, set(), "x", REGISTRY), [])
        # `category` and `version` are template metadata in core, never fields,
        # so a view naming them would be silently dropped at runtime.
        views = {"roles": {"card_fields": ["category"]}, "facets": ["version"]}
        errs = validate.check_views_semantics(views, {"category", "version"}, "x", REGISTRY)
        self.assertEqual(len(errs), 2, errs)

    def test_view_shapes_core_reads(self) -> None:
        # Core's resolver reads object columns and a plain sort key only.
        for bad in ({"table": {"columns": ["name"]}},
                    {"sort": {"default": "-updated"}},
                    {"roles": {"title": "colors.primary"}}):
            self.assertTrue(validate._validate_instance(bad, "views.json", "x"), bad)

    def test_cloud_and_plugin_views_are_registered_ids(self) -> None:
        views = {"default": "map", "enabled": ["map", "timeline", "cards", "plugin:x:y"]}
        self.assertEqual(validate.check_views_semantics(views, set(), "x", REGISTRY), [])

    def test_layout_views_may_name_template_fields(self) -> None:
        layout = {"entity_type": "x", "version": "1.0",
                  "sections": [{"id": "a", "fields": [{"key": "name", "ui_component": "text"}]}],
                  "views": {"roles": {"badges": ["rarity"]}}}
        self.assertTrue(validate.layout_errors(layout, "x", REGISTRY))
        self.assertEqual(validate.layout_errors(layout, "x", REGISTRY, {"rarity"}), [])

    def test_field_config_only_keys_are_not_fields(self) -> None:
        # Core derives fields from top-level frontmatter keys only; a key that
        # exists only under field_config is dropped from every view.
        fm = {"entity_type": "x", "name": "", "status": "a",
              "field_config": {"phase": {"type": "enum", "options": ["a", "b"]}},
              "views": {"board": {"group_by": "phase"}, "facets": ["status"]}}
        errs = validate.template_errors(fm, "x", REGISTRY)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("'phase'", errs[0])

    def test_template_metadata_fields_are_not_fields(self) -> None:
        # TEMPLATE_METADATA_FIELDS (created_date, last_updated, ...) are
        # skipped by core even though they are top-level keys.
        fm = {"entity_type": "x", "name": "", "created_date": "", "last_updated": "",
              "ui_color": "#000",
              "views": {"enabled": ["calendar"], "calendar": {"date_field": "created_date"},
                        "sort": {"default": "last_updated"},
                        "roles": {"card_fields": ["ui_color"]}}}
        errs = validate.template_errors(fm, "x", REGISTRY)
        flagged = sorted(e.split("names unknown field ")[1] for e in errs)
        self.assertEqual(flagged, ["'created_date'", "'last_updated'", "'ui_color'"])

    def test_grid_fields_must_name_fields(self) -> None:
        fm = {"entity_type": "x", "template_category": "entity", "power": 1,
              "grid_fields": ["power", "speed"]}
        errs = validate.template_errors(fm, "x", REGISTRY)
        self.assertEqual(len(errs), 1)
        self.assertIn("'speed'", errs[0])


class FrontmatterSplitTests(unittest.TestCase):
    def test_closes_only_on_a_delimiter_line(self) -> None:
        text = '---\nentity_type: x\ndescription: "Fast---very fast"\nrule: |\n  a --- b\n---\n# Body ---\n'
        fm, body = validate.split_frontmatter(text)
        data = yaml.safe_load(fm)
        self.assertEqual(data["description"], "Fast---very fast")
        self.assertEqual(data["rule"], "a --- b\n")
        self.assertIn("# Body ---", body)

    def test_missing_closing_delimiter(self) -> None:
        self.assertIsNone(validate.split_frontmatter("---\nentity_type: x\nnote: a---b\n"))
        self.assertIsNone(validate.split_frontmatter("entity_type: x\n"))


class RegistryExportTests(unittest.TestCase):
    def test_typescript_interface_lists_every_export_key(self) -> None:
        data = json.loads((ROOT / "schemas" / "registry" / "widget-ids.json").read_text())
        dts = (ROOT / "index.d.ts").read_text()
        body = dts[dts.index("export interface WidgetIds {"):]
        body = body[:body.index("\n}")]
        for key in data:
            if not key.startswith("$") and key != "source":
                self.assertIn(f"  {key}:", body, key)

    def test_template_metadata_fields_are_meta_keys(self) -> None:
        for key in ("created_date", "last_updated", "ui_icon", "generation_instructions"):
            self.assertIn(key, REGISTRY["meta_keys"], key)

    def test_export_is_internally_consistent(self) -> None:
        data = json.loads((ROOT / "schemas" / "registry" / "widget-ids.json").read_text())
        widgets = set(data["widgets"])
        self.assertEqual(len(widgets), len(data["widgets"]), "duplicate widget id")
        for alias, target in data["aliases"].items():
            self.assertNotIn(alias, widgets, f"alias {alias!r} shadows a registered id")
            # Core's normalizeWidgetId resolves one hop, and lint_widget_id
            # tells authors to use the target: it must be a canonical
            # registered widget, never another alias or a renderer-only id.
            self.assertIn(target, widgets, f"alias {alias!r} -> non-canonical {target!r}")
            self.assertNotIn(target, data["aliases"], f"alias {alias!r} chains to alias {target!r}")
        self.assertFalse(
            set(data["renderer_only"]) & set(data["aliases"]),
            "an id core aliases is not renderer-only",
        )
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

    def test_layout_driven_layouts_keep_the_hero_and_assets(self) -> None:
        # A layout_driven detail page renders only the layout's sections, so
        # one without these blocks loses the hero image and asset gallery the
        # auto-layout gave it. These five turned layout_driven in SBAI-15043.
        for name in ("brand", "district", "faction", "item", "location"):
            data = json.loads((ROOT / "templates" / "Layouts" / f"{name}.layout.json").read_text())
            components = [s.get("component") for s in data["sections"]]
            self.assertIn("primary-image", components, name)
            self.assertIn("entity-assets", components, name)

    def test_character_colour_widgets_hold_name_hex_objects(self) -> None:
        # eye_color / hair_color store {name, hex}; the layout widget wins over
        # field_config, so it must be the palette widget, not color-picker.
        layout = json.loads((ROOT / "templates" / "Layouts" / "character.layout.json").read_text())
        widgets = {f["key"]: f.get("ui_component")
                   for s in layout["sections"] for f in s.get("fields") or []}
        fm = _fm((ROOT / "templates" / "Standard" / "CHARACTER_TEMPLATE.md").read_text())
        for key in ("eye_color", "hair_color"):
            self.assertEqual(widgets[key], "color-palette", key)
            self.assertEqual(fm["field_config"][key]["widget"], "color-palette", key)
            self.assertIsInstance(fm[key], dict, key)

    def test_3d_level_map_keeps_its_entity_type(self) -> None:
        fm = _fm((ROOT / "templates" / "Standard" / "Maps" / "3D_Level_MAP_TEMPLATE.md").read_text())
        self.assertEqual(fm["entity_type"], "3d_level")

    def test_standard_templates_ship_the_tuned_views(self) -> None:
        def views(name: str) -> dict:
            return _fm((ROOT / "templates" / "Standard" / f"{name}_TEMPLATE.md").read_text())["views"]

        character = views("CHARACTER")
        self.assertEqual(character["default"], "cards")
        self.assertEqual(character["roles"]["badges"], ["faction", "status"])
        item = views("ITEM")
        self.assertEqual(item["default"], "gallery")
        self.assertIn("table", item["enabled"])
        self.assertEqual(set(item["roles"]["badges"]), {"rarity", "item_type"})
        for name in ("LOCATION", "BIOME"):
            self.assertEqual(views(name)["default"], "gallery", name)
            self.assertIn("map", views(name)["enabled"], name)
        quest = views("QUEST")
        self.assertEqual((quest["default"], quest["board"]["group_by"]), ("board", "status"))
        timeline = views("TIMELINE")
        self.assertEqual(timeline["default"], "calendar")
        self.assertIn("timeline", timeline["enabled"])
        self.assertTrue(timeline["calendar"]["date_field"])
        for name in ("FACTION", "BRAND", "DISTRICT"):
            self.assertEqual(views(name)["default"], "cards", name)
        self.assertEqual(views("DIALOGUE")["default"], "list")

    def test_character_year_fields_keep_their_existing_shape(self) -> None:
        # Existing characters store age as a string ("18", "mid-30s") and the
        # years as null. Core honours field_config.<k>.type and validates on
        # write without coercion, so declaring integer here 422s every save of
        # an untouched existing character. Keep them undeclared until a
        # migration or coercion ships.
        for rel in ("templates/Standard/CHARACTER_TEMPLATE.md",
                    "templates/Packs/starter-characters/templates/CHARACTER_TEMPLATE.md"):
            fm = _fm((ROOT / rel).read_text())
            self.assertIsInstance(fm["age"], str, rel)
            for key in ("age", "birth_year", "death_year"):
                self.assertNotIn("type", (fm.get("field_config") or {}).get(key) or {}, f"{rel} {key}")


if __name__ == "__main__":
    unittest.main()
