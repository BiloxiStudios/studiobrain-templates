"""Catalog route and starter contracts for SBAI-7890."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest

import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalog = _load_module("build_catalog_index", ROOT / "scripts" / "build_catalog_index.py")
validate = _load_module("validate", ROOT / "scripts" / "validate.py")


class ProviderRouteContractTests(unittest.TestCase):
    def _route_errors(self, body: str) -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            providers_dir = tmp / "templates" / "Providers"
            providers_dir.mkdir(parents=True)
            (providers_dir / "route.provider.yaml").write_text(body, encoding="utf-8")
            old_root, old_templates = validate.ROOT, validate.TEMPLATES_DIR
            validate.ROOT, validate.TEMPLATES_DIR = tmp, tmp / "templates"
            try:
                errors, _ = validate.check_requires()
            finally:
                validate.ROOT, validate.TEMPLATES_DIR = old_root, old_templates
        return errors

    def test_published_index_exposes_route_and_starter(self):
        entries = {entry["id"]: entry for entry in catalog.build_entries(ROOT)}
        self.assertEqual(entries["openai"]["route"], "aigateway")
        self.assertIs(entries["openai"]["starter"], True)
        self.assertEqual(entries["openai-direct"]["route"], "direct")
        self.assertIs(entries["openai-direct"]["starter"], False)

    def test_shipped_provider_routes_match_owner_locked_contract(self):
        providers = {}
        for path in sorted((ROOT / "templates" / "Providers").glob("*.provider.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            providers[data["id"]] = data

        for provider_id in ("openai", "anthropic", "grok", "workers-ai", "groq"):
            with self.subTest(provider=provider_id):
                provider = providers[provider_id]
                self.assertEqual(provider["route"], "aigateway")
                self.assertIs(provider["starter"], True)
                self.assertEqual(provider["billing"], ["brainbits", "byok"])
                self.assertIn("gateway.ai.cloudflare.com", provider["base_url"])

        direct = providers["openai-direct"]
        self.assertEqual(direct["route"], "direct")
        self.assertIs(direct["starter"], False)
        self.assertEqual(direct["billing"], ["byok"])
        self.assertEqual(direct["base_url"], "https://api.openai.com")

    def test_schema_rejects_unknown_route(self):
        schema = json.loads((ROOT / "schemas" / "provider.json").read_text(encoding="utf-8"))
        provider = {
            "id": "bad-route",
            "kind": "provider",
            "wire": "openai-compat",
            "route": "surprise",
        }
        errors = list(Draft202012Validator(schema).iter_errors(provider))
        self.assertTrue(errors, "unknown route must be rejected")

    def test_direct_route_rejects_brainbits_and_starter(self):
        errors = self._route_errors(
            "id: bad-direct\nkind: provider\nwire: openai-compat\n"
            "route: direct\nstarter: true\nbilling: [brainbits, byok]\n"
        )
        self.assertTrue(any("route 'direct'" in error and "brainbits" in error for error in errors), errors)
        self.assertTrue(any("starter" in error and "aigateway" in error for error in errors), errors)

    def test_aigateway_route_requires_both_billing_modes(self):
        errors = self._route_errors(
            "id: bad-gateway\nkind: provider\nwire: openai-compat\n"
            "route: aigateway\nstarter: true\nbilling: [byok]\n"
            "base_url: https://gateway.ai.cloudflare.com/v1/x/y/compat\n"
        )
        self.assertTrue(any("billing [brainbits, byok]" in error for error in errors), errors)

    def test_groq_and_grok_are_distinct_aigateway_slugs(self):
        # SBAI-7876: Groq (LPU inference platform) and Grok (xAI's model) are
        # different vendors that happen to be near-homophones -- assert they
        # ship as two distinct catalog rows, not a collapsed/duplicated one.
        providers = {}
        for path in sorted((ROOT / "templates" / "Providers").glob("*.provider.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            providers[data["id"]] = data

        self.assertIn("groq", providers)
        self.assertIn("grok", providers)
        self.assertNotEqual(providers["groq"]["display"], providers["grok"]["display"])
        for provider_id in ("groq", "grok"):
            with self.subTest(provider=provider_id):
                provider = providers[provider_id]
                self.assertEqual(provider["route"], "aigateway")
                self.assertEqual(provider["billing"], ["brainbits", "byok"])

    def test_huggingface_router_reuses_existing_huggingface_slug(self):
        # SBAI-7876: model-manager's SBAI-7875 (#881) added a distinct
        # [cloud.huggingface-router] gateway.toml section to disambiguate
        # from the LOCAL [huggingface] weights/cache config -- but that is a
        # model-manager-internal split. In the templates catalog, the
        # existing huggingface.provider.yaml already targets
        # router.huggingface.co/v1/chat/completions (the same "Router"
        # contract), so no second slug (e.g. huggingface-router) may exist
        # here -- it would duplicate huggingface per the SBAI-7612 contract.
        provider_dir = ROOT / "templates" / "Providers"
        ids = {yaml.safe_load(p.read_text(encoding="utf-8"))["id"] for p in provider_dir.glob("*.provider.yaml")}
        self.assertIn("huggingface", ids)
        self.assertNotIn("huggingface-router", ids)

        huggingface = yaml.safe_load((provider_dir / "huggingface.provider.yaml").read_text(encoding="utf-8"))
        self.assertIn("router.huggingface.co", huggingface["base_url"])
        self.assertEqual(huggingface["billing"], ["byok"])
        self.assertNotIn("route", huggingface)

    def test_validator_rejects_duplicate_provider_slugs(self):
        body = "id: duplicate\nkind: provider\nwire: openai-compat\n"
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            providers_dir = tmp / "templates" / "Providers"
            providers_dir.mkdir(parents=True)
            (providers_dir / "a.provider.yaml").write_text(body, encoding="utf-8")
            (providers_dir / "b.provider.yaml").write_text(body, encoding="utf-8")
            old_root, old_templates = validate.ROOT, validate.TEMPLATES_DIR
            validate.ROOT, validate.TEMPLATES_DIR = tmp, tmp / "templates"
            try:
                errors = validate.check_providers_and_abilities()
            finally:
                validate.ROOT, validate.TEMPLATES_DIR = old_root, old_templates
        self.assertTrue(any("duplicate provider id 'duplicate'" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
