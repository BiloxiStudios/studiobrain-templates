"""Negative-evidence tests for the ``wire: in-app`` invariants in
scripts/validate.py (SBAI-7625 / SBAI-7626).

The on-device provider is the free tier: it runs Gemma 4 weights on the
user's own hardware, so it must never acquire a URL, an auth block, or a
billing/pricing field, and ``runtime`` / ``weights`` must never appear on a
provider that actually talks to the network. The catalog file that ships in
this repo is the happy path only, which proves none of the ERROR branches --
these tests build synthetic catalogs in a tmpdir and prove each branch fires
(and, just as importantly, does not fire on the good file).

Also pins the desktop-only aggregation rule: a provider that declares
``platforms: [web, desktop, mobile]`` is NOT desktop-only and must not force
every canvas that uses it to become desktop-only.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import validate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

GOOD_IN_APP = """
id: on-device-test
kind: provider
display: On-Device (test)
wire: in-app
runtime: transformers.js
provides: [llm-chat]
requires:
  platforms: [web, desktop, mobile]
  webgpu: optional
weights:
  - id: gemma-4-e2b-it-q4f16-webgpu
    source: huggingface://onnx-community/gemma-4-E2B-it-ONNX
    dtype: q4f16
    device: webgpu
    capability: llm-chat
    default: true
"""


def _run(tmp: pathlib.Path, files: dict[str, str]) -> tuple[list[str], list[str]]:
    """Run check_requires() against a synthetic catalog tree."""
    providers_dir = tmp / "templates" / "Providers"
    providers_dir.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        (providers_dir / name).write_text(body, encoding="utf-8")
    old_root, old_templates = validate.ROOT, validate.TEMPLATES_DIR
    validate.ROOT, validate.TEMPLATES_DIR = tmp, tmp / "templates"
    try:
        return validate.check_requires()
    finally:
        validate.ROOT, validate.TEMPLATES_DIR = old_root, old_templates


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class InAppInvariantTests(unittest.TestCase):
    def assert_error_matching(self, errors: list[str], needle: str) -> None:
        self.assertTrue(
            any(needle in e for e in errors),
            f"expected an error containing {needle!r}, got {errors!r}",
        )

    def check(self, body: str) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as td:
            return _run(pathlib.Path(td), {"x.provider.yaml": body})

    def test_good_in_app_provider_is_clean(self):
        errors, warnings = self.check(GOOD_IN_APP)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_wire_call_fields_are_rejected(self):
        for field, snippet in (
            ("base_url", "base_url: https://api.openai.com/v1"),
            ("endpoint", "endpoint: /v1/chat/completions"),
            ("auth", "auth:\n  env: OPENAI_API_KEY"),
            ("request", "request:\n  method: POST"),
            ("response", "response:\n  text_path: choices.0.message.content"),
        ):
            with self.subTest(field=field):
                errors, _ = self.check(GOOD_IN_APP + snippet + "\n")
                self.assert_error_matching(errors, f"must not declare {field}")

    def test_money_fields_are_rejected(self):
        for field, snippet in (
            ("billing", "billing: [brainbits]"),
            ("billing", "billing: [byok]"),
            ("pricing", "pricing:\n  source: endpoint\n  endpoint: /prices"),
        ):
            with self.subTest(snippet=snippet):
                errors, _ = self.check(GOOD_IN_APP + snippet + "\n")
                self.assert_error_matching(errors, f"must not declare {field}")

    def test_runtime_is_required(self):
        body = GOOD_IN_APP.replace("runtime: transformers.js\n", "")
        errors, _ = self.check(body)
        self.assert_error_matching(errors, "runtime is required")

    def test_at_least_one_weights_row_is_required(self):
        body = GOOD_IN_APP.split("weights:")[0] + "weights: []\n"
        errors, _ = self.check(body)
        self.assert_error_matching(errors, "requires at least one weights row")

    def test_non_huggingface_source_warns_but_does_not_error(self):
        body = GOOD_IN_APP.replace(
            "huggingface://onnx-community/gemma-4-E2B-it-ONNX",
            "https://example.com/weights.onnx",
        )
        errors, warnings = self.check(body)
        self.assertEqual(errors, [])
        self.assertTrue(
            any("expected 'huggingface://<repo-id>'" in w for w in warnings),
            f"expected a source warning, got {warnings!r}",
        )

    def test_empty_source_errors(self):
        body = GOOD_IN_APP.replace(
            "source: huggingface://onnx-community/gemma-4-E2B-it-ONNX",
            'source: ""',
        )
        errors, _ = self.check(body)
        self.assert_error_matching(errors, "empty source")

    def test_duplicate_weights_row_ids_error(self):
        body = GOOD_IN_APP + """\
  - id: gemma-4-e2b-it-q4f16-webgpu
    source: huggingface://onnx-community/gemma-4-E4B-it-ONNX
    dtype: q4f16
    device: webgpu
"""
        errors, _ = self.check(body)
        self.assert_error_matching(errors, "duplicate weights row id")

    def test_runtime_and_weights_are_in_app_only(self):
        cloud = """
id: cloudy
kind: provider
wire: openai-compat
runtime: transformers.js
base_url: https://api.example.com
weights:
  - id: sneaky
    source: huggingface://foo/bar
    dtype: q4
    device: webgpu
"""
        errors, _ = self.check(cloud)
        self.assert_error_matching(errors, "runtime is 'wire: in-app' only")
        self.assert_error_matching(errors, "weights is 'wire: in-app' only")


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class DesktopOnlyAggregationTests(unittest.TestCase):
    """A multi-platform provider must not make its canvases desktop-only."""

    CANVAS = """
id: uses-provider
kind: canvas
steps:
  - id: s1
    provider: {pid}
"""

    def run_pair(self, provider_body: str, pid: str) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            return _run(
                tmp,
                {
                    "p.provider.yaml": provider_body,
                    "c.canvas.yaml": self.CANVAS.format(pid=pid),
                },
            )

    def test_desktop_only_provider_still_forces_desktop(self):
        body = """
id: blenderish
kind: provider
wire: process
endpoint: blender
requires:
  platforms: [desktop]
"""
        errors, _ = self.run_pair(body, "blenderish")
        self.assertTrue(
            any("uses desktop-only provider" in e for e in errors),
            f"desktop-only enforcement regressed: {errors!r}",
        )

    def test_multi_platform_in_app_provider_does_not_force_desktop(self):
        errors, _ = self.run_pair(GOOD_IN_APP, "on-device-test")
        self.assertEqual(
            [e for e in errors if "desktop-only" in e],
            [],
            "on-device runs on web/desktop/mobile and must not force a canvas "
            f"to desktop-only: {errors!r}",
        )


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class ShippedCatalogTests(unittest.TestCase):
    """The real on-device.provider.yaml must satisfy every invariant, and the
    §5 weight matrix must not silently lose a tier."""

    def test_shipped_catalog_has_no_requires_errors(self):
        errors, _ = validate.check_requires()
        self.assertEqual(errors, [])

    def test_on_device_weight_matrix(self):
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["wire"], "in-app")
        self.assertNotIn("billing", data, "the on-device free tier must never declare billing")
        self.assertNotIn("pricing", data)
        rows = {r["id"]: r for r in data["weights"]}
        # Spec SBAI-7625 §5 tiers, all five present.
        self.assertEqual(
            sorted(rows),
            [
                "gemma-4-e2b-it-q4-wasm",
                "gemma-4-e2b-it-q4f16-webgpu",
                "gemma-4-e4b-it-q4f16-webgpu",
                "nomic-embed-text-v1.5-q8-any",
                "qwen3-0.6b-q4-any",
            ],
        )
        # Exactly one free-tier default, and it is the E2B WebGPU tier.
        defaults = [r["id"] for r in data["weights"] if r.get("default")]
        self.assertEqual(defaults, ["gemma-4-e2b-it-q4f16-webgpu"])
        # The WASM step-down is the experimental one; Qwen is the labelled
        # reduced-capability fallback, never a Gemma tier.
        self.assertTrue(rows["gemma-4-e2b-it-q4-wasm"]["experimental"])
        self.assertEqual(rows["gemma-4-e2b-it-q4-wasm"]["device"], "wasm")
        self.assertTrue(rows["qwen3-0.6b-q4-any"]["fallback"])
        self.assertNotIn("gemma", rows["qwen3-0.6b-q4-any"]["source"].lower())
        self.assertEqual(rows["nomic-embed-text-v1.5-q8-any"]["capability"], "embeddings")
        for row in data["weights"]:
            self.assertTrue(row["source"].startswith("huggingface://"), row)


if __name__ == "__main__":
    unittest.main()
