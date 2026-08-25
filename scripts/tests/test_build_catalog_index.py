"""Regression tests for the pricing operand + canvas step_count contract
(SBAI-7675).

The catalog index feeds the marketplace's approx-cost badge:
``approx_cost = provider.pricing.amount * canvas.step_count``. Both halves of
that formula must be honest: a provider's price is a typed, provider-neutral
operand (currency/unit/amount) that is present ONLY when the source YAML
declares one -- never invented, never defaulted to 0 -- and a canvas's
step_count is always the literal length of its parsed ``steps`` list, not a
hand-maintained number that can drift from the graph.

No real file under templates/Providers declares a pricing operand (the repo
deliberately does not invent vendor prices), so these tests build synthetic
catalog trees in a tmpdir -- the same pattern test_validate_in_app.py uses --
rather than polluting the real catalog with fixture pricing data.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build_catalog_index as bci  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

PRICED_PROVIDER = """
id: priced-test
kind: provider
display: Priced Test Provider
wire: http
base_url: https://example.com
endpoint: /generate
provides: [image-gen]
billing: [byok]
pricing:
  source: table
  operand:
    currency: USD
    unit: per-step
    amount: 0.04
"""

UNPRICED_PROVIDER = """
id: unpriced-test
kind: provider
display: Unpriced Test Provider
wire: http
base_url: https://example.com
endpoint: /generate
provides: [image-gen]
billing: [byok]
"""

TABLE_ONLY_PROVIDER = """
id: table-only-test
kind: provider
display: Table Only Test Provider
wire: http
base_url: https://example.com
endpoint: /generate
provides: [image-gen]
billing: [byok]
pricing:
  source: table
  table:
    some-model: 0.02
"""

WEIGHTED_PROVIDER = """
id: weighted-test
kind: provider
display: Weighted Test Provider
wire: in-app
runtime: transformers.js
provides: [llm-chat]
weights:
  - id: weighted-test/q4-webgpu
    capability: llm-chat
    dtype: q4
    device: webgpu
    min_ram_gb: 8
    revision: abc123
    source: huggingface://example/model
  - id: weighted-test/q8-wasm
    capability: llm-chat
    dtype: q8
    device: wasm
    max_output_tokens: 2048
"""

MULTI_STEP_CANVAS = """
id: multi-step-test
kind: canvas
name: Multi Step Test
entity_types: [item]
slots:
  brief:
    modality: text
    ref: entity.item.description
  out1:
    modality: image
    out: entity.item.primary_image
steps:
  - id: step-one
    provider: priced-test
    in:
      prompt: brief
    out:
      image: out1
  - id: step-two
    provider: priced-test
    in:
      image: out1
    out:
      image: out1
  - id: step-three
    provider: priced-test
    in:
      image: out1
    out:
      image: out1
"""

SINGLE_STEP_CANVAS = """
id: single-step-test
kind: canvas
name: Single Step Test
entity_types: [item]
slots:
  brief:
    modality: text
    ref: entity.item.description
  out1:
    modality: image
    out: entity.item.primary_image
steps:
  - id: only-step
    provider: priced-test
    in:
      prompt: brief
    out:
      image: out1
"""

PROVIDER_WITH_BOOTSTRAP = """
id: bootstrap-test
kind: provider
display: Bootstrap Test Provider
wire: openai-compat
base_url: http://127.0.0.1:11434
bootstrap:
  base_url_env: TEST_URL
  base_url_env_aliases: [FALLBACK_URL, DEFAULT_URL]
endpoint: /v1/chat/completions
provides: [llm-chat]
"""

PROVIDER_WITH_MM_CLOUD = """
id: mm-cloud-test
kind: provider
display: MM Cloud Test Provider
wire: openai-compat
base_url: http://127.0.0.1:7077
mm_cloud:
  id: test-provider
  kind: openai
  api_key_env: TEST_API_KEY
  base_url: https://api.test.com
endpoint: /v1/chat/completions
provides: [llm-chat]
"""

PROVIDER_WITH_BOTH = """
id: both-test
kind: provider
display: Both Test Provider
wire: openai-compat
base_url: http://127.0.0.1:8080
bootstrap:
  base_url_env: PRIMARY_URL
  base_url_env_aliases: [BACKUP_URL]
mm_cloud:
  id: cloud-id
  kind: anthropic
  api_key_env: CLOUD_KEY
  base_url: https://api.anthropic.com
endpoint: /v1/chat/completions
provides: [llm-chat]
"""


def _write_tree(tmp: pathlib.Path, providers: dict[str, str], canvases: dict[str, str]) -> None:
    providers_dir = tmp / "templates" / "Providers"
    providers_dir.mkdir(parents=True, exist_ok=True)
    for name, body in providers.items():
        (providers_dir / name).write_text(body, encoding="utf-8")
    canvas_dir = tmp / "templates" / "Canvas"
    canvas_dir.mkdir(parents=True, exist_ok=True)
    for name, body in canvases.items():
        (canvas_dir / name).write_text(body, encoding="utf-8")


@unittest.skipUnless(bci.yaml is not None, "pyyaml required")
class PricingOperandTests(unittest.TestCase):
    def test_priced_provider_exposes_typed_operand(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"priced.provider.yaml": PRICED_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "priced-test")
        self.assertEqual(
            provider["pricing"], {"currency": "USD", "unit": "per-step", "amount": 0.04}
        )

    def test_unpriced_provider_has_no_pricing_key(self):
        """Absence, not a zero amount, is how the index spells 'unknown'."""
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"unpriced.provider.yaml": UNPRICED_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "unpriced-test")
        self.assertNotIn("pricing", provider)

    def test_table_only_pricing_has_no_pricing_key(self):
        """An unstructured 'table' with no 'operand' is not a badge-able price."""
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"table.provider.yaml": TABLE_ONLY_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "table-only-test")
        self.assertNotIn("pricing", provider)

    def test_compact_pricing_operand_rejects_partial_operands(self):
        for bad in (
            {"unit": "per-step", "amount": 1},  # missing currency
            {"currency": "USD", "amount": 1},  # missing unit
            {"currency": "USD", "unit": "per-step"},  # missing amount
            {"currency": "USD", "unit": "per-step", "amount": "1"},  # amount not numeric
            "not-a-dict",
        ):
            with self.subTest(bad=bad):
                self.assertIsNone(bci._compact_pricing_operand({"operand": bad}))

    def test_compact_pricing_operand_none_when_absent(self):
        self.assertIsNone(bci._compact_pricing_operand(None))
        self.assertIsNone(bci._compact_pricing_operand({}))
        self.assertIsNone(bci._compact_pricing_operand({"source": "table", "table": {}}))


@unittest.skipUnless(bci.yaml is not None, "pyyaml required")
class ProviderModelsTests(unittest.TestCase):
    def test_provider_weights_are_published_as_models_without_losing_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"weighted.provider.yaml": WEIGHTED_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "weighted-test")
        self.assertEqual([row["id"] for row in provider["models"]], [
            "weighted-test/q4-webgpu",
            "weighted-test/q8-wasm",
        ])
        self.assertEqual(provider["models"][0]["revision"], "abc123")
        self.assertEqual(provider["models"][0]["min_ram_gb"], 8)
        self.assertEqual(provider["models"][1]["device"], "wasm")

    def test_malformed_weights_fail_closed_instead_of_publishing_empty_models(self):
        with self.assertRaisesRegex(RuntimeError, "weights must be a list"):
            bci._provider_models({"id": "not-a-list"})
        with self.assertRaisesRegex(RuntimeError, r"weights\[0\] must be a mapping"):
            bci._provider_models(["not-a-row"])


@unittest.skipUnless(bci.yaml is not None, "pyyaml required")
class CanvasStepCountTests(unittest.TestCase):
    def test_multi_step_canvas_step_count(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {}, {"multi.canvas.yaml": MULTI_STEP_CANVAS})
            entries = bci.build_entries(tmp)
        canvas = next(e for e in entries if e["id"] == "multi-step-test")
        self.assertEqual(canvas["step_count"], 3)

    def test_single_step_canvas_step_count(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {}, {"single.canvas.yaml": SINGLE_STEP_CANVAS})
            entries = bci.build_entries(tmp)
        canvas = next(e for e in entries if e["id"] == "single-step-test")
        self.assertEqual(canvas["step_count"], 1)

    def test_step_count_is_the_literal_parsed_length(self):
        """Adding a step to the source YAML must move step_count by exactly one --
        proves the field tracks the parsed graph, not a cached/independent number."""
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(
                tmp,
                {},
                {
                    "single.canvas.yaml": SINGLE_STEP_CANVAS,
                    "multi.canvas.yaml": MULTI_STEP_CANVAS,
                },
            )
            entries = bci.build_entries(tmp)
        counts = {e["id"]: e["step_count"] for e in entries if e["kind"] == "canvas"}
        self.assertEqual(counts, {"single-step-test": 1, "multi-step-test": 3})


@unittest.skipUnless(bci.yaml is not None, "pyyaml required")
class RootScopingTests(unittest.TestCase):
    """build_entries(root=...) must scan UNDER root, not the module's own ROOT.

    Regression guard: SCAN used to be built once at import time from the
    module-level TEMPLATES_DIR, so passing a different root only affected the
    id->path relativization, not what got scanned -- a custom root silently
    fell back to scanning the real repo. _scan(root) closes that gap.
    """

    def test_synthetic_root_does_not_leak_real_catalog_entries(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"unpriced.provider.yaml": UNPRICED_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        ids = {e["id"] for e in entries}
        self.assertEqual(ids, {"unpriced-test"})
        # A real catalog provider (e.g. "openai") must not appear -- proves
        # the scan actually rooted at tmp, not ROOT.
        self.assertNotIn("openai", ids)

    def test_synthetic_root_paths_are_relative_to_root(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"unpriced.provider.yaml": UNPRICED_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "unpriced-test")
        self.assertEqual(provider["path"], "templates/Providers/unpriced.provider.yaml")


@unittest.skipUnless(bci.yaml is not None, "pyyaml required")
class ShippedCatalogTests(unittest.TestCase):
    """No real provider invents a price, and every real canvas gets a step_count."""

    def test_no_shipped_provider_has_invented_pricing(self):
        """Sanity pin: this ticket adds the CONTRACT, not vendor price data.

        If this ever fails because a real provider legitimately gained a
        sourced price, that's fine -- update this test alongside the PR that
        adds it, with the rate-card source in the commit message.
        """
        entries = bci.build_entries(ROOT)
        priced = [e for e in entries if e["kind"] == "provider" and "pricing" in e]
        self.assertEqual(priced, [], f"unexpected invented pricing on: {priced!r}")

    def test_every_shipped_canvas_has_a_step_count(self):
        entries = bci.build_entries(ROOT)
        canvases = [e for e in entries if e["kind"] == "canvas"]
        self.assertTrue(canvases, "no canvas entries found in the shipped catalog")
        for canvas in canvases:
            self.assertIn("step_count", canvas, canvas["id"])
            self.assertGreaterEqual(canvas["step_count"], 1, canvas["id"])

    def test_on_device_provider_publishes_webgpu_and_wasm_model_rows(self):
        entries = bci.build_entries(ROOT)
        provider = next(e for e in entries if e["id"] == "on-device")
        models = {row["id"]: row for row in provider["models"]}
        self.assertEqual(models["on-device/gemma-4-e2b-it-q4"]["dtype"], "q4")
        self.assertEqual(models["on-device/gemma-4-e2b-it-q4"]["device"], "webgpu")
        self.assertEqual(models["on-device/qwen3-0.6b-q8-wasm"]["device"], "wasm")


@unittest.skipUnless(bci.yaml is not None, "pyyaml required")
class BootstrapMmCloudTests(unittest.TestCase):
    """Tests for SBAI-8017: bootstrap env aliases and mm_cloud mapping."""

    def test_provider_with_bootstrap_exposes_env_aliases(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"bootstrap.provider.yaml": PROVIDER_WITH_BOOTSTRAP}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "bootstrap-test")
        self.assertIn("bootstrap", provider)
        self.assertEqual(provider["bootstrap"]["base_url_env"], "TEST_URL")
        self.assertEqual(provider["bootstrap"]["base_url_env_aliases"], ["FALLBACK_URL", "DEFAULT_URL"])

    def test_provider_with_mm_cloud_exposes_routing_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"mm-cloud.provider.yaml": PROVIDER_WITH_MM_CLOUD}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "mm-cloud-test")
        self.assertIn("mm_cloud", provider)
        self.assertEqual(provider["mm_cloud"]["id"], "test-provider")
        self.assertEqual(provider["mm_cloud"]["kind"], "openai")
        self.assertEqual(provider["mm_cloud"]["api_key_env"], "TEST_API_KEY")
        self.assertEqual(provider["mm_cloud"]["base_url"], "https://api.test.com")

    def test_provider_with_both_bootstrap_and_mm_cloud(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"both.provider.yaml": PROVIDER_WITH_BOTH}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "both-test")
        self.assertIn("bootstrap", provider)
        self.assertIn("mm_cloud", provider)
        self.assertEqual(provider["bootstrap"]["base_url_env"], "PRIMARY_URL")
        self.assertEqual(provider["mm_cloud"]["id"], "cloud-id")

    def test_provider_without_bootstrap_omits_fields(self):
        """Providers without bootstrap/mm_cloud should not have those keys."""
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            _write_tree(tmp, {"unpriced.provider.yaml": UNPRICED_PROVIDER}, {})
            entries = bci.build_entries(tmp)
        provider = next(e for e in entries if e["id"] == "unpriced-test")
        self.assertNotIn("bootstrap", provider)
        self.assertNotIn("mm_cloud", provider)

    def test_real_ollama_has_bootstrap(self):
        """Integration test: the real ollama provider has bootstrap metadata."""
        entries = bci.build_entries(ROOT)
        ollama = next((e for e in entries if e["id"] == "ollama"), None)
        self.assertIsNotNone(ollama, "ollama provider not found")
        self.assertIn("bootstrap", ollama)
        self.assertEqual(ollama["bootstrap"]["base_url_env"], "OLLAMA_URL")

    def test_real_model_manager_has_bootstrap(self):
        """Integration test: the real model-manager provider has bootstrap metadata."""
        entries = bci.build_entries(ROOT)
        mm = next((e for e in entries if e["id"] == "model-manager"), None)
        self.assertIsNotNone(mm, "model-manager provider not found")
        self.assertIn("bootstrap", mm)
        self.assertEqual(mm["bootstrap"]["base_url_env"], "AI_GATEWAY_URL")

    def test_real_openai_has_mm_cloud(self):
        """Integration test: the real openai provider has mm_cloud metadata."""
        entries = bci.build_entries(ROOT)
        openai_entry = next((e for e in entries if e["id"] == "openai"), None)
        self.assertIsNotNone(openai_entry, "openai provider not found")
        self.assertIn("mm_cloud", openai_entry)
        self.assertEqual(openai_entry["mm_cloud"]["id"], "openai")
        self.assertEqual(openai_entry["mm_cloud"]["kind"], "openai")

    def test_catalog_is_byte_reproducible_for_fixed_provenance(self):
        """Two builds from one source revision and timestamp are identical."""
        generated_at = "2026-08-24T00:00:00Z"
        first = bci.render(bci.build_index(generated_at, ROOT))
        second = bci.render(bci.build_index(generated_at, ROOT))
        self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))
        self.assertEqual(json.loads(first)["generated_at"], generated_at)

    def test_catalog_contains_env_names_not_credential_values(self):
        """Executable catalog metadata may name secrets, never carry values."""
        entries = bci.build_entries(ROOT)
        forbidden_value_keys = {"api_key", "password", "secret", "token", "credential"}

        def walk(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(
                        key.lower(),
                        forbidden_value_keys,
                        f"credential value field published at {'.'.join((*path, key))}",
                    )
                    walk(child, (*path, key))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, (*path, str(index)))

        walk(entries)


if __name__ == "__main__":
    unittest.main()
