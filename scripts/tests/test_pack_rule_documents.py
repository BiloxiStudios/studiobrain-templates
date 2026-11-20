"""Rule authoring enters CI through the normal pack validator."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import validate


@unittest.skipUnless(validate.HAVE_JSONSCHEMA and validate.HAVE_YAML, "needs jsonschema and pyyaml")
class PackRuleDocuments(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        templates = pathlib.Path(temporary.name) / "templates"
        self.pack = templates / "Packs" / "sample-kitchen"
        self.pack.mkdir(parents=True)
        patched = patch.object(validate, "TEMPLATES_DIR", templates)
        patched.start()
        self.addCleanup(patched.stop)
        self.rule = {"id": "kitchen_001", "rule": "No meat in a recipe.", "validation_type": "error",
                     "fields": ["ingredients"], "forbidden_terms": ["beef", "ham"]}

    def write(self, name, document):
        path = self.pack / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = validate.yaml.safe_dump(document)
        path.write_text(f"---\n{text}---\n\n# Rules\n" if path.suffix == ".md" else text)
        return path

    def test_mixed_levels_and_old_collections(self):
        for key in ("rules", "mandatory"):
            entries = [dict(self.rule, allowed_phrases=["vegan ham"]), "Taste before serving",
                       {"content": "Write one action per step"},
                       {"rule": "Portions", "validation_type": "warning", "required_fields": "servings"},
                       {"rule": "Allergens", "validation_type": "suggestion"},
                       {"rule": "Local units", "validation_type": "info"}]
            path = self.write("rules/VEGAN_RECIPE_RULES.md", {"entity_type": "vegan_recipe", key: entries})
            self.assertEqual(validate.pack_rule_errors(path), [])

    def test_errors_name_the_file_and_refuse_malformed_authoring(self):
        for patch_values in ({"validation_type": "notice"}, {"severity": "urgent"},
                             {"severity": "info"}, {"forbidden_terms": []},
                             {"forbidden_terms": [" "]}, {"required_fields": {"field": "name"}},
                             {"validation_type": "warning", "enforcement": "block"}):
            with self.subTest(patch_values=patch_values):
                self.write("named/recipe-guide.md", {"rules": [dict(self.rule, **patch_values)]})
                errors = validate.check_pack_rule_files(self.pack, {"rules": ["named/recipe-guide.md"]})
                self.assertTrue(any("recipe-guide.md" in e for e in errors), errors)

    def test_blocking_declaration_and_duplicate_ids(self):
        rule = self.rule.copy()
        del rule["forbidden_terms"]
        for extra in ({}, {"allowed_phrases": ["ham"]}, {"verify": {"via": "machine"}}):
            path = self.write("rules/a.yaml", {"rules": [dict(rule, **extra)]})
            self.assertIn("declared check", " ".join(validate.pack_rule_errors(path)))
        for extra in ({"references": {"owner": "chef"}}, {"required_fields": ["sku"]},
                      {"verify": {"via": "agent"}}, {"field": "unit", "allowed_values": ["g"]}):
            path = self.write("rules/a.yaml", {"rules": [dict(rule, **extra)]})
            self.assertEqual(validate.pack_rule_errors(path), [])
        path = self.write("rules/a.yaml", {"rules": [self.rule, self.rule]})
        self.assertIn("duplicate rule id", " ".join(validate.pack_rule_errors(path)))

        path = self.write("rules/a.yaml", {"mandatory": ["Prose", {"id": "rule_001", "rule": "More prose"}]})
        self.assertIn("duplicate rule id", " ".join(validate.pack_rule_errors(path)))

    def test_pack_validation_loads_canonical_and_declared_paths_once(self):
        manifest = {"id": "sample-kitchen", "rules": ["rules/FRESH_RULES.md", "forms/notes.md"]}
        (self.pack / "pack.json").write_text(json.dumps(manifest))
        self.write("rules/FRESH_RULES.md", {"rules": [dict(self.rule, validation_type="oops")]})
        self.write("forms/notes.md", {"mandatory": [self.rule], "rules": []})
        errors = validate.check_packs()
        self.assertEqual(sum("FRESH_RULES.md:" in e for e in errors), 1, errors)
        self.assertTrue(any("forms/notes.md" in e for e in errors), errors)

    def test_guides_and_old_assembly_pack(self):
        self.write("rules/guide.md", {"entity_type": "pack-doc"})
        self.write("rules/guidance.yaml", {"field_rules": {"sku": {"instruction": "Include the SKU"}}})
        self.assertEqual(validate.check_pack_rule_files(self.pack, {}), [])
        self.pack = self.pack.parent / "starter-assemblies"
        shipped = pathlib.Path(__file__).resolve().parents[2] / "templates/Packs/starter-assemblies/rules/assembly-rules.yaml"
        original = validate.yaml.safe_load(shipped.read_text())["rules"][0]
        path = self.write("rules/assembly-rules.yaml", {"rules": [original]})
        self.assertEqual(validate.pack_rule_errors(path), [])
        self.write("rules/assembly-rules.yaml", {"rules": [dict(original, rule="An unrelated blocking rule")]})
        self.assertIn("declared check", " ".join(validate.pack_rule_errors(path)))
        self.write("rules/assembly-rules.yaml", {"rules": [original, dict(original, id="pack_asm_005")]})
        self.assertEqual(len(validate.pack_rule_errors(path)), 1)
        path = self.write("rules/OTHER_RULES.md", {"rules": [original]})
        self.assertTrue(validate.pack_rule_errors(path))

    def test_native_rule_ids_need_an_explicit_level_and_matching_type(self):
        row = {"id": "char_002", "rule": "Character naming"}
        path = self.write("rules/CHARACTER_RULES.md", {"entity_type": "character", "rules": [row]})
        self.assertIn("explicitly", " ".join(validate.pack_rule_errors(path)))
        row["validation_type"] = "error"
        self.write("rules/CHARACTER_RULES.md", {"entity_type": "character", "rules": [row]})
        self.assertEqual(validate.pack_rule_errors(path), [])
        self.write("rules/CHARACTER_RULES.md", {"entity_type": "recipe", "rules": [row]})
        self.assertIn("declared check", " ".join(validate.pack_rule_errors(path)))

    def test_bad_paths_and_unreadable_frontmatter(self):
        path = self.write("rules/recipe.md", {"rules": [self.rule]})
        path.write_text("---\nrules: [\n---\n")
        self.write("rules/FRESH_RULES.md", {})
        (self.pack / "rules/outside.md").symlink_to(pathlib.Path("/"))
        entries = {"rules": ["absent.md", "../some-pack/rules.yaml", "rules/missing.json", str(path)]}
        errors = "\n".join(validate.check_pack_rule_files(self.pack, entries))
        for phrase in ("recipe.md", "FRESH_RULES.md", "outside this pack", "absent.md", "missing.json", "relative rule path"):
            self.assertIn(phrase, errors)
