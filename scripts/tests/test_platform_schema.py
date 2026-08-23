"""SBAI-7974: platform.yaml + provider engine/limits contract.

Proves the drift-prevention doctrine in code:

* engine.category reuses MM v2 taxonomy, never a wire protocol
* limits aliases (max_tokens / max_output_tokens) must agree
* shipped catalog providers declare engine
* shipped platform files validate and reference real catalog ids
* unknown provider/weight refs are errors
"""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

import sys

sys.path.insert(0, str(ROOT / "scripts"))
import validate  # noqa: E402

SCHEMAS = ROOT / "schemas"
PROVIDERS = ROOT / "templates" / "Providers"
PLATFORMS = ROOT / "templates" / "Platforms"

ENGINE_TAXONOMY = [
    "local_inprocess",
    "local_spawned",
    "lan_endpoint",
    "distributed",
    "cloud_provider",
    "llm_router",
]


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _validator(name: str) -> Draft202012Validator:
    validator = validate.make_validator(name)
    assert validator is not None, "jsonschema is required for these tests"
    return validator


def _platform_errors(files: dict[str, str], providers: dict[str, str] | None = None) -> list[str]:
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        plat_dir = tmp / "templates" / "Platforms"
        plat_dir.mkdir(parents=True)
        for name, body in files.items():
            (plat_dir / name).write_text(body, encoding="utf-8")
        prov_dir = tmp / "templates" / "Providers"
        prov_dir.mkdir(parents=True)
        if providers:
            for name, body in providers.items():
                (prov_dir / name).write_text(body, encoding="utf-8")
        old_root, old_templates = validate.ROOT, validate.TEMPLATES_DIR
        validate.ROOT, validate.TEMPLATES_DIR = tmp, tmp / "templates"
        try:
            errors, _ = validate.check_platforms()
        finally:
            validate.ROOT, validate.TEMPLATES_DIR = old_root, old_templates
        return errors


GOOD_PROVIDER = """
id: on-device
kind: provider
wire: in-app
engine:
  category: local_inprocess
  requirement: preferred
  framework: transformers.js
runtime: transformers.js
provides: [llm-chat]
requires:
  platforms: [web, desktop, mobile]
weights:
  - id: on-device/gemma-4-e2b-it-q4f16-webgpu
    source: huggingface://onnx-community/gemma-4-E2B-it-ONNX
    dtype: q4f16
    device: webgpu
    max_output_tokens: 8192
"""

GOOD_PLATFORM = """
id: web
kind: platform
surface: web
engine: local_inprocess
limits:
  max_weights: 1
  max_tokens: 8192
defaults:
  - capability: llm-chat
    provider: on-device
    weight: on-device/gemma-4-e2b-it-q4f16-webgpu
"""


class EngineSchemaTests(unittest.TestCase):
    def test_taxonomy_enum_matches_mm_v2(self):
        engine = _load_schema("_engine.json")
        self.assertEqual(engine["$defs"]["taxonomy_category"]["enum"], ENGINE_TAXONOMY)

    def test_provider_schema_accepts_object_and_shorthand_engine(self):
        validator = _validator("provider.json")
        base = {"id": "p", "kind": "provider", "wire": "openai-compat"}
        validator.validate({**base, "engine": "cloud_provider"})
        validator.validate(
            {
                **base,
                "engine": {
                    "category": "llm_router",
                    "requirement": "preferred",
                    "framework": "openai",
                },
            }
        )

    def test_provider_schema_rejects_wire_as_engine(self):
        validator = _validator("provider.json")
        errors = list(
            validator.iter_errors(
                {"id": "p", "kind": "provider", "wire": "openai-compat", "engine": "openai-compat"}
            )
        )
        self.assertTrue(errors, "wire value must not be a valid engine.category")

    def test_limits_reject_unknown_keys(self):
        validator = _validator("provider.json")
        errors = list(
            validator.iter_errors(
                {
                    "id": "p",
                    "kind": "provider",
                    "wire": "openai-compat",
                    "limits": {"max_tokens": 128, "surprise": 1},
                }
            )
        )
        self.assertTrue(errors)


class PlatformSchemaTests(unittest.TestCase):
    def test_shipped_platforms_validate(self):
        validator = _validator("platform.json")
        files = sorted(PLATFORMS.glob("*.platform.yaml"))
        self.assertGreaterEqual(len(files), 4, "expected web/desktop/ios/android")
        for path in files:
            with self.subTest(path=path.name):
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                validator.validate(data)

    def test_schema_rejects_unknown_surface(self):
        validator = _validator("platform.json")
        errors = list(
            validator.iter_errors({"id": "x", "kind": "platform", "surface": "watchos"})
        )
        self.assertTrue(errors)

    def test_schema_rejects_unknown_keys(self):
        validator = _validator("platform.json")
        errors = list(
            validator.iter_errors(
                {"id": "web", "kind": "platform", "surface": "web", "wire": "in-app"}
            )
        )
        self.assertTrue(errors)


class PlatformValidatorTests(unittest.TestCase):
    def test_good_platform_is_clean(self):
        errors = _platform_errors(
            {"web.platform.yaml": GOOD_PLATFORM},
            {"on-device.provider.yaml": GOOD_PROVIDER},
        )
        self.assertEqual(errors, [])

    def test_unknown_provider_is_error(self):
        errors = _platform_errors(
            {"web.platform.yaml": GOOD_PLATFORM},
            {"other.provider.yaml": "id: other\nkind: provider\nwire: openai-compat\n"},
        )
        self.assertTrue(any("unknown provider" in e for e in errors), errors)

    def test_unknown_weight_is_error(self):
        body = GOOD_PLATFORM.replace(
            "on-device/gemma-4-e2b-it-q4f16-webgpu", "on-device/does-not-exist"
        )
        errors = _platform_errors(
            {"web.platform.yaml": body},
            {"on-device.provider.yaml": GOOD_PROVIDER},
        )
        self.assertTrue(any("unknown weight" in e for e in errors), errors)

    def test_wire_protocol_as_engine_is_error(self):
        _, errs = validate.normalize_engine("openai-compat", "p")
        self.assertTrue(any("wire protocol" in e for e in errs), errs)

    def test_shorthand_engine_normalizes_to_preferred(self):
        normalized, errs = validate.normalize_engine("lan_endpoint", "p")
        self.assertEqual(errs, [])
        self.assertEqual(normalized, {"category": "lan_endpoint", "requirement": "preferred"})


class CatalogEngineBackfillTests(unittest.TestCase):
    def test_every_shipped_provider_declares_engine(self):
        missing = []
        for path in sorted(PROVIDERS.glob("*.provider.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            normalized, errs = validate.normalize_engine(
                data.get("engine"), f"{path.name}: provider '{data.get('id')}'"
            )
            if errs or normalized is None:
                missing.append(f"{path.name}: {errs or 'engine missing'}")
        self.assertEqual(missing, [])

    def test_no_shipped_provider_uses_wire_as_engine(self):
        for path in sorted(PROVIDERS.glob("*.provider.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            engine = data.get("engine")
            category = engine if isinstance(engine, str) else (engine or {}).get("category")
            self.assertNotIn(category, validate.PROVIDER_WIRES, path.name)

    def test_max_tokens_disagreement_is_error(self):
        body = """
id: on-device
kind: provider
wire: in-app
engine: local_inprocess
runtime: transformers.js
requires:
  platforms: [web]
weights:
  - id: on-device/x
    source: huggingface://org/repo
    dtype: q8
    device: wasm
    max_tokens: 128
    max_output_tokens: 256
    revision: 0000000000000000000000000000000000000000
    license: mit
    license_artifact: licenses/mit.txt
    mirror_path: on-device/org__repo/0000000000000000000000000000000000000000/
    size: 1
    files:
      - name: model.onnx
        sha256: 0000000000000000000000000000000000000000000000000000000000000000
        size: 1
"""
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            prov = tmp / "templates" / "Providers"
            prov.mkdir(parents=True)
            (prov / "x.provider.yaml").write_text(body, encoding="utf-8")
            old_root, old_templates = validate.ROOT, validate.TEMPLATES_DIR
            validate.ROOT, validate.TEMPLATES_DIR = tmp, tmp / "templates"
            try:
                errors, _ = validate.check_requires()
            finally:
                validate.ROOT, validate.TEMPLATES_DIR = old_root, old_templates
        self.assertTrue(any("disagreeing" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
