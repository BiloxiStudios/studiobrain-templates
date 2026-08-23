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


if __name__ == "__main__":
    unittest.main()
