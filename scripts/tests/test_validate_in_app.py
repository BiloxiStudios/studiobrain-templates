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

import json
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
  - id: on-device/gemma-4-e2b-it-q4f16-webgpu
    source: huggingface://onnx-community/gemma-4-E2B-it-ONNX
    dtype: q4f16
    device: webgpu
    revision: 9f4bef82ea6e296bc69f8a2f5939f73af81b07a6
    mirror_path: on-device/onnx-community__gemma-4-E2B-it-ONNX/9f4bef82ea6e296bc69f8a2f5939f73af81b07a6/
    license: apache-2.0
    license_artifact: licenses/apache-2.0.txt
    size: 1
    files:
      - name: model.onnx
        sha256: 0000000000000000000000000000000000000000000000000000000000000000
        size: 1
    capability: llm-chat
    context_length: 131072
    max_output_tokens: 8192
    tools: true
    thinking: optional
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
                matching = [
                    error for error in errors
                    if f"must not declare {field}" in error
                ]
                self.assertEqual(len(matching), 1, errors)

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
  - id: on-device/gemma-4-e2b-it-q4f16-webgpu
    source: huggingface://onnx-community/gemma-4-E4B-it-ONNX
    dtype: q4f16
    device: webgpu
"""
        errors, _ = self.check(body)
        self.assert_error_matching(errors, "duplicate weights row id")

    def test_chat_row_without_capability_metadata_warns(self):
        """A chat row that omits context_length/tools WARNs but still validates.

        The fields are optional in the schema so older catalogs keep passing;
        the warning is what stops a new row shipping with an unverifiable
        context window or an unstated tool-calling story.
        """
        for dropped in ("context_length: 131072\n", "tools: true\n"):
            with self.subTest(dropped=dropped.strip()):
                body = GOOD_IN_APP.replace("    " + dropped, "")
                errors, warnings = self.check(body)
                self.assertEqual(errors, [])
                field = dropped.split(":")[0]
                self.assertTrue(
                    any(f"omits {field}" in w for w in warnings),
                    f"expected a {field} warning, got {warnings!r}",
                )

    def test_tools_false_is_not_treated_as_omitted(self):
        """tools: false is an explicit answer, not a missing one."""
        body = GOOD_IN_APP.replace("tools: true", "tools: false")
        errors, warnings = self.check(body)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_embeddings_row_is_not_warned_for_missing_tools(self):
        """Only chat rows need a tool-calling story."""
        body = GOOD_IN_APP.split("weights:")[0] + """\
weights:
  - id: on-device/nomic-embed-text-v1.5-q8-any
    source: huggingface://nomic-ai/nomic-embed-text-v1.5
    dtype: q8
    device: any
    revision: e9b6763023c676ca8431644204f50c2b100d9aab
    mirror_path: on-device/nomic-ai__nomic-embed-text-v1.5/e9b6763023c676ca8431644204f50c2b100d9aab/
    license: apache-2.0
    license_artifact: licenses/apache-2.0.txt
    size: 1
    files:
      - name: model.onnx
        sha256: 0000000000000000000000000000000000000000000000000000000000000000
        size: 1
    capability: embeddings
    context_length: 8192
"""
        errors, warnings = self.check(body)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

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

    def test_requires_webgpu_is_in_app_only(self):
        cloud = """
id: cloudy-webgpu
kind: provider
wire: openai-compat
base_url: https://api.example.com
requires:
  webgpu: optional
"""
        errors, _ = self.check(cloud)
        self.assert_error_matching(
            errors, "requires.webgpu is 'wire: in-app' only"
        )


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
        # Spec SBAI-7625 §5 tiers as revised by the SBAI-7682 witness, plus the
        # SBAI-7726 asset-intelligence rows. Ids are namespaced so the cloud
        # money-leak guard can reject the lane by 'on-device/' prefix.
        self.assertEqual(
            sorted(rows),
            [
                "on-device/florence-2-base-ft-fp16-webgpu",
                "on-device/florence-2-base-ft-q8-wasm",
                "on-device/gemma-4-e2b-it-litert-web",
                "on-device/gemma-4-e2b-it-q4",
                "on-device/gemma-4-e2b-it-q4f16-webgpu",
                "on-device/gemma-4-e4b-it-litert-web",
                "on-device/gemma-4-e4b-it-q4f16-webgpu",
                "on-device/nomic-embed-text-v1.5-q8-any",
                "on-device/qwen3-0.6b-q4-any",
                "on-device/qwen3-0.6b-q8-wasm",
                "on-device/siglip2-base-256-vision-q4-webgpu",
                "on-device/siglip2-base-256-vision-q4f16-webgpu",
                "on-device/siglip2-base-256-vision-q8-wasm",
                "on-device/siglip2-so400m-256-vision-q4f16-webgpu",
                "on-device/whisper-base-q4-webgpu",
                "on-device/whisper-base-q8-wasm",
            ],
        )
        # Exactly one default PER CAPABILITY. `default` means "preferred row
        # for its capability/device tier"; a second default inside one
        # capability is an ambiguous selection, but chat/tagging/caption each
        # need their own.
        defaults: dict[str, list[str]] = {}
        for row in data["weights"]:
            if row.get("default"):
                defaults.setdefault(row.get("capability", "llm-chat"), []).append(row["id"])
        self.assertEqual(
            defaults,
            {
                # SBAI-8406 (2026-08-26, owner witnessed): litert-web promoted to
                # the llm-chat default; the ONNX q4f16-webgpu row is the fallback.
                "llm-chat": ["on-device/gemma-4-e2b-it-litert-web"],
                "asset-tagging": ["on-device/siglip2-base-256-vision-q4f16-webgpu"],
                "asset-caption": ["on-device/florence-2-base-ft-fp16-webgpu"],
                "stt": ["on-device/whisper-base-q4-webgpu"],
            },
        )
        # SBAI-7844, revised by SBAI-8406 (2026-08-26, owner witnessed): the
        # litert-lm rows are a SECOND engine. gemma-4-e2b-it-litert-web is now
        # the witnessed, production llm-chat default (no `experimental` flag);
        # gemma-4-e4b-it-litert-web remains the unwitnessed quality tier and
        # must stay experimental with no `default` flag -- an engine no
        # browser has benched must never silently become a default.
        litert = [r for r in data["weights"] if r.get("runtime") == "litert-lm"]
        self.assertEqual(
            [r["id"] for r in litert],
            ["on-device/gemma-4-e2b-it-litert-web", "on-device/gemma-4-e4b-it-litert-web"],
        )
        ids = [r["id"] for r in data["weights"]]
        for row in litert:
            if row["id"] == "on-device/gemma-4-e2b-it-litert-web":
                self.assertNotIn(
                    "experimental", row, f"{row['id']} is the witnessed default; must not be experimental"
                )
                self.assertTrue(row.get("default"), f"{row['id']} must be the llm-chat default")
            else:
                self.assertTrue(row["experimental"], f"{row['id']} must stay experimental")
                self.assertNotIn("default", row, f"{row['id']} must not be a default tier")
            self.assertTrue(row["file"].endswith("-web.litertlm"), row["file"])
            self.assertEqual(row["device"], "webgpu", "litert-lm is WebGPU-only")
            self.assertEqual(row["modality"], ["text"], "the litert web build is text-only")
            self.assertEqual(row["context_length"], 32768, "32k is the model's ceiling")
            self.assertFalse(row["tools"], f"{row['id']}: tools stay off until witnessed")
        # Declared LAST, after every transformers.js row: the stable-sort
        # tiebreak is what keeps the ONNX tier ahead at equal min_ram_gb.
        self.assertEqual(ids[-2:], [r["id"] for r in litert])
        # Same RAM floors as the ONNX rows they tie with, so neither outranks.
        floors = {r["id"]: r["min_ram_gb"] for r in data["weights"] if "min_ram_gb" in r}
        self.assertEqual(
            floors["on-device/gemma-4-e2b-it-litert-web"],
            floors["on-device/gemma-4-e2b-it-q4f16-webgpu"],
        )
        self.assertEqual(
            floors["on-device/gemma-4-e4b-it-litert-web"],
            floors["on-device/gemma-4-e4b-it-q4f16-webgpu"],
        )
        # Qwen is the labelled reduced-capability fallback, never a Gemma tier.
        self.assertTrue(rows["on-device/qwen3-0.6b-q4-any"]["fallback"])
        self.assertNotIn("gemma", rows["on-device/qwen3-0.6b-q4-any"]["source"].lower())
        self.assertEqual(
            rows["on-device/nomic-embed-text-v1.5-q8-any"]["capability"], "embeddings"
        )

    def test_no_gemma_wasm_row(self):
        """SBAI-7682: the Gemma WASM tier is falsified, not merely untested.

        ORT-web's WASM execution provider has no GatherBlockQuantized kernel,
        so Gemma 4's q4 ONNX cannot create a session there at all (witnessed
        after a 3.5 GB in-browser download), and its q8 weights are ~9 GB,
        over the wasm32 4 GB ceiling. Re-adding a Gemma WASM row would hand
        every WebGPU-less user a multi-gigabyte download that cannot run.
        """
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        gemma_wasm = [
            r["id"]
            for r in data["weights"]
            if "gemma" in r["source"].lower() and r.get("device") in ("wasm", "any")
        ]
        self.assertEqual(gemma_wasm, [], "no Gemma row may be reachable on WASM")

    def _stt_rows(self) -> dict:
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return {r["id"]: r for r in data["weights"] if r.get("capability") == "stt"}

    def test_stt_covers_both_runtimes(self):
        """SBAI-7837: a runtime with no STT row silently has no mic button.

        The whole point of the ticket is that voice input dead-ended. A tier
        that declares nothing here reproduces that, just one layer down.
        """
        rows = self._stt_rows()
        self.assertTrue(rows, "the on-device provider must declare stt rows")
        devices = {r.get("device") for r in rows.values()}
        for runtime in ("webgpu", "wasm"):
            self.assertTrue(
                runtime in devices or "any" in devices,
                f"no stt weights row is reachable on {runtime}: {sorted(rows)}",
            )

    def test_stt_declares_the_capability_on_the_provider(self):
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        # A row whose capability is not in `provides` is invisible to
        # capability matching and marketplace filtering.
        self.assertIn("stt", data["provides"])
        # ...and the provider must admit it accepts audio at all.
        self.assertIn("audio", data["slots"]["accepts"])
        for row in self._stt_rows().values():
            self.assertEqual(row.get("modality"), ["audio"])

    def test_no_q4f16_stt_row(self):
        """onnx-community/whisper-base publishes NO q4f16 weights.

        Its onnx/ tree carries fp32 / fp16 / int8 / uint8 / _quantized / _q4 /
        _bnb4 and nothing else, so a q4f16 row would 404 mid-download. Verified
        against huggingface.co/api/models/onnx-community/whisper-base/tree/main
        /onnx?recursive=true (SBAI-7837).
        """
        for row_id, row in self._stt_rows().items():
            dtypes = {row.get("dtype"), *(row.get("dtype_map") or {}).values()}
            self.assertNotIn("q4f16", dtypes, f"{row_id}: whisper-base has no q4f16 weights")

    def test_stt_wasm_tier_is_int8_not_q4(self):
        """q4 has no ORT-web WASM kernel, and for whisper it is also BIGGER.

        Block-4-bit quantizes MatMul weights only, so whisper-base's q4 decoder
        (123,602,419 B) is more than twice its q8 one (53,693,315 B). A WASM
        row on q4 would be unrunnable AND larger.
        """
        for row_id, row in self._stt_rows().items():
            if row.get("device") not in ("wasm", "any"):
                continue
            dtypes = {row.get("dtype"), *(row.get("dtype_map") or {}).values()}
            self.assertFalse(
                dtypes & {"q4", "q4f16", "bnb4"},
                f"{row_id}: the WASM stt tier must be plain int8/q8, got {sorted(dtypes)}",
            )

    def test_stt_webgpu_decoder_is_not_q8(self):
        """transformers.js #1317: a q8 decoder on the WebGPU EP emits GIBBERISH.

        Reproduced across whisper tiny/base/small/large-v3-turbo, and the same
        weights decode correctly on WASM -- so this is silent wrong output, not
        a load error something downstream could catch.
        """
        for row_id, row in self._stt_rows().items():
            if row.get("device") != "webgpu":
                continue
            decoder = (row.get("dtype_map") or {}).get("decoder_model_merged", row.get("dtype"))
            self.assertNotIn(
                decoder, ("q8", "int8"), f"{row_id}: q8 decoders are gibberish on WebGPU"
            )

    def test_stt_dtype_map_names_only_real_seq2seq_modules(self):
        """A misspelt module key does not error -- it silently falls back.

        transformers.js resolves a seq2seq model's sessions to exactly
        `encoder_model` and `decoder_model_merged` (src/models/session_config.js,
        MODEL_TYPES.Seq2Seq). Any other key is dropped with an info log, and the
        row then loads at the device default instead of the tier it declares.
        """
        for row_id, row in self._stt_rows().items():
            for module in (row.get("dtype_map") or {}):
                self.assertIn(
                    module,
                    ("encoder_model", "decoder_model_merged"),
                    f"{row_id}: {module!r} is not a whisper session key",
                )

    def test_every_device_tier_has_a_runnable_non_f16_row(self):
        """SBAI-7682: an f16-only tier dead-ends AFTER the download.

        q4f16 / fp16 graphs need the WebGPU `shader-f16` feature. The witness
        ran a hardware NVIDIA Blackwell adapter that grants WebGPU and does
        not expose it, so the catalog's q4f16 default downloaded ~3 GB and
        then aborted at OrtRun. Each runtime needs at least one chat row the
        executor can select without f16.
        """
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        f16 = {"q4f16", "fp16"}
        for device in ("webgpu", "wasm"):
            runnable = [
                r["id"]
                for r in data["weights"]
                if r.get("capability", "llm-chat") == "llm-chat"
                and r.get("device") in (device, "any")
                and r.get("dtype") not in f16
                and not r.get("fallback")
            ]
            self.assertTrue(
                runnable,
                f"device {device!r} has no selectable non-f16 chat row",
            )
        for row in data["weights"]:
            self.assertTrue(row["source"].startswith("huggingface://"), row)
            self.assertTrue(
                row["id"].startswith("on-device/"),
                f"weight row id must be namespaced so the money-leak guard "
                f"can match by prefix: {row['id']!r}",
            )

    def test_on_device_capability_metadata(self):
        """Every chat tier declares its window, output cap, and tool story."""
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = {r["id"]: r for r in data["weights"]}
        for rid, row in rows.items():
            if row.get("capability", "llm-chat") != "llm-chat":
                continue
            self.assertIn("context_length", row, rid)
            self.assertIn("max_output_tokens", row, rid)
            # Every chat row states its tool story explicitly -- the point of
            # this assertion is that no tier ships with the question unanswered.
            # `True` for every ONNX tier; the litert-lm rows say False, and that
            # is the honest answer rather than a missing one: the runtime's tool
            # support is real and structured, but no browser has closed a tool
            # loop on it yet, so the catalog does not claim one. When the
            # SBAI-7844 witness lands, that row flips to True in the same
            # change and this exemption goes away (SBAI-7729/7844).
            expected_tools = row.get("runtime") != "litert-lm"
            self.assertIs(row.get("tools"), expected_tools, rid)
            self.assertIn(row.get("thinking"), ("none", "optional", "always"), rid)
        # Gemma 4 is a 128k-context family; the Qwen fallback is not, and must
        # not inherit Gemma's window by copy-paste.
        for rid in (
            "on-device/gemma-4-e4b-it-q4f16-webgpu",
            "on-device/gemma-4-e2b-it-q4f16-webgpu",
            "on-device/gemma-4-e2b-it-q4",
        ):
            self.assertEqual(rows[rid]["context_length"], 131072, rid)
            self.assertEqual(rows[rid]["max_output_tokens"], 8192, rid)
        for rid in ("on-device/qwen3-0.6b-q4-any", "on-device/qwen3-0.6b-q8-wasm"):
            self.assertEqual(rows[rid]["context_length"], 32768, rid)
            self.assertEqual(rows[rid]["max_output_tokens"], 4096, rid)
        # The embeddings row has a window but no chat-only capability keys.
        nomic = rows["on-device/nomic-embed-text-v1.5-q8-any"]
        self.assertEqual(nomic["context_length"], 8192)
        self.assertNotIn("tools", nomic)
        self.assertNotIn("thinking", nomic)


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class AssetIntelligenceRowTests(unittest.TestCase):
    """SBAI-7726 §5: the asset-tagging / asset-caption rows and their guards."""

    def setUp(self):
        import yaml  # noqa: PLC0415

        path = ROOT / "templates" / "Providers" / "on-device.provider.yaml"
        self.data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.rows = {r["id"]: r for r in self.data["weights"]}

    def rows_for(self, capability: str) -> dict:
        return {
            rid: row
            for rid, row in self.rows.items()
            if row.get("capability") == capability
        }

    def test_provider_declares_the_new_capabilities(self):
        for tag in ("asset-tagging", "asset-caption"):
            self.assertIn(tag, self.data["provides"])
            self.assertIn(tag, validate._KNOWN_PROVIDES, f"{tag} must not WARN as unknown")
        # It scores images now, so the slot contract has to say so or no canvas
        # edge can ever reach it.
        self.assertIn("image", self.data["slots"]["accepts"])

    def test_siglip_rows_are_vision_tower_only_with_a_real_artifact(self):
        """The whole size story depends on never shipping the text tower.

        A row that forgets model_file_name downloads the COMBINED model (378 MB
        - 1.07 GB) instead of 55-95 MB, and a row whose artifact is missing
        downloads a vision tower with nothing to score against.
        """
        tagging = self.rows_for("asset-tagging")
        self.assertTrue(tagging, "no asset-tagging rows")
        for rid, row in tagging.items():
            self.assertEqual(row.get("model_file_name"), "vision_model", rid)
            self.assertEqual(row.get("taxonomy"), "studiobrain.asset-tags", rid)
            artifact_rel = row.get("taxonomy_embeddings")
            self.assertTrue(artifact_rel, f"{rid} has no taxonomy_embeddings")
            artifact = ROOT / artifact_rel
            self.assertTrue(artifact.is_file(), f"{rid} -> missing {artifact_rel}")
            stamp = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(stamp["taxonomy"]["id"], row["taxonomy"], rid)
            self.assertEqual(row.get("modality"), ["image"], rid)
            # Encoders have no chat window and emit no tokens.
            for chat_only in ("context_length", "max_output_tokens", "tools", "thinking"):
                self.assertNotIn(chat_only, row, f"{rid} declares chat-only key {chat_only}")

    def test_tier_artifacts_are_not_interchangeable(self):
        """base embeds at 768 dims, so400m at 1152 -- crossing them scores garbage."""
        dims = {}
        for rid, row in self.rows_for("asset-tagging").items():
            artifact = json.loads((ROOT / row["taxonomy_embeddings"]).read_text(encoding="utf-8"))
            dims.setdefault(row["source"], set()).add(artifact["model"]["embed_dim"])
            self.assertEqual(
                artifact["model"]["id"],
                row["source"].removeprefix("huggingface://"),
                f"{rid} points at an artifact built from a different repo",
            )
        for source, seen in dims.items():
            self.assertEqual(len(seen), 1, f"{source} rows disagree on embed_dim: {seen}")

    def test_asset_tagging_has_a_runnable_row_on_every_runtime(self):
        """Same SBAI-7682 doctrine as chat: q4f16 needs shader-f16, q4 has no
        WASM kernel. A tier with only f16 rows dead-ends after the download."""
        f16 = {"q4f16", "fp16"}
        tagging = self.rows_for("asset-tagging").values()
        webgpu_non_f16 = [
            r["id"] for r in tagging
            if r.get("device") in ("webgpu", "any") and r.get("dtype") not in f16
        ]
        self.assertTrue(webgpu_non_f16, "asset-tagging has no non-f16 WebGPU row")
        wasm = [
            r["id"] for r in tagging
            if r.get("device") in ("wasm", "any") and r.get("dtype") not in (f16 | {"q4"})
        ]
        self.assertTrue(wasm, "asset-tagging has no WASM-runnable (non-q4, non-f16) row")

    def test_caption_rows_declare_their_per_module_dtypes(self):
        """Florence-2 is four graphs. A scalar dtype cannot express the mix, and
        q4 on the conv-heavy vision encoder buys nothing (it is fp32-sized)."""
        caption = self.rows_for("asset-caption")
        self.assertTrue(caption, "no asset-caption rows")
        for rid, row in caption.items():
            self.assertIn("dtype_map", row, rid)
            self.assertEqual(
                sorted(row["dtype_map"]),
                ["decoder_model_merged", "embed_tokens", "encoder_model", "vision_encoder"],
                rid,
            )
            self.assertNotEqual(row["dtype_map"]["vision_encoder"], "q4", rid)
            self.assertEqual(row.get("modality"), ["text", "image"], rid)
        wasm = [r for r in caption.values() if r.get("device") == "wasm"]
        self.assertTrue(wasm, "asset-caption has no WASM row")
        for row in wasm:
            self.assertNotIn(row["dtype"], ("q4", "q4f16", "fp16"), row["id"])
            for module, dt in row["dtype_map"].items():
                self.assertNotIn(dt, ("q4", "q4f16", "fp16"), f"{row['id']}:{module}")

    def test_no_naflex_row(self):
        """siglip2-*-naflex-ONNX declares model_type 'siglip2', which has no
        entry in the transformers.js v4 registry -- it fails at load, AFTER the
        download. Only FixRes SigLIP-2 repos may be added."""
        offenders = [r["id"] for r in self.data["weights"] if "naflex" in r["source"].lower()]
        self.assertEqual(offenders, [], "NaFlex is unsupported in transformers.js")

    def test_no_fastvlm_row(self):
        """onnx-community/FastVLM-0.5B-ONNX ships under `apple-amlr`, not an OSI
        license. It stays out of this Apache-2.0 catalog until reviewed."""
        offenders = [
            r["id"]
            for r in self.data["weights"]
            if "fastvlm" in r["source"].lower() or "/apple/" in r["source"].lower()
        ]
        self.assertEqual(offenders, [], "FastVLM needs a license review before shipping")


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class TaxonomyEmbeddingsPointerTests(unittest.TestCase):
    """check_requires() must reject a row wired to the WRONG TIER's artifact.

    One taxonomy has one artifact per model tier and they are not
    interchangeable -- siglip2-base embeds at 768 dims, so400m at 1152. Both
    artifacts legitimately carry the SAME taxonomy id, so the taxonomy-id check
    cannot tell them apart; only the model the vectors came from can. A crossed
    pointer passes schema validation, passes the taxonomy stamp check, and then
    dot-products mismatched widths on the user's device AFTER the download has
    already been paid for.
    """

    PROVIDER = """\
id: on-device-test
kind: provider
display: On-Device (test)
wire: in-app
runtime: transformers.js
provides: [asset-tagging]
requires:
  platforms: [web, desktop, mobile]
  webgpu: optional
weights:
  - id: on-device/siglip2-base-256-vision-q4f16-webgpu
    source: huggingface://onnx-community/siglip2-base-patch16-256-ONNX
    model_file_name: vision_model
    dtype: q4f16
    device: webgpu
    revision: d1114256522a37ffa257a0a58017348ab0058db2
    mirror_path: on-device/onnx-community__siglip2-base-patch16-256-ONNX/d1114256522a37ffa257a0a58017348ab0058db2/
    license: apache-2.0
    license_artifact: licenses/apache-2.0.txt
    size: 1
    files:
      - name: vision_model.onnx
        sha256: 0000000000000000000000000000000000000000000000000000000000000000
        size: 1
    capability: asset-tagging
    taxonomy: studiobrain.asset-tags
    taxonomy_embeddings: taxonomies/{artifact}
"""

    TIERS = {
        "asset-tags.embeddings.json": ("onnx-community/siglip2-base-patch16-256-ONNX", 768),
        "asset-tags.so400m.embeddings.json": (
            "onnx-community/siglip2-so400m-patch16-256-ONNX",
            1152,
        ),
    }

    def run_pointing_at(self, artifact_name: str) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            (tmp / "taxonomies").mkdir(parents=True, exist_ok=True)
            for name, (model_id, dim) in self.TIERS.items():
                (tmp / "taxonomies" / name).write_text(
                    json.dumps(
                        {
                            "artifact_schema_version": 1,
                            "taxonomy": {
                                "id": "studiobrain.asset-tags",
                                "revision": "1.0.0",
                                "content_hash": "sha256:" + "0" * 64,
                            },
                            "model": {"id": model_id, "embed_dim": dim, "tower": "text"},
                            "scoring": {
                                "formula": "sigmoid(...)",
                                "logit_scale": 1.0,
                                "logit_bias": 0.0,
                            },
                            "label_count": 0,
                            "labels": [],
                        }
                    ),
                    encoding="utf-8",
                )
            return _run(
                tmp, {"x.provider.yaml": self.PROVIDER.format(artifact=artifact_name)}
            )

    def test_matching_tier_is_clean(self):
        errors, _ = self.run_pointing_at("asset-tags.embeddings.json")
        self.assertEqual(errors, [])

    def test_crossed_tier_is_an_error(self):
        errors, _ = self.run_pointing_at("asset-tags.so400m.embeddings.json")
        self.assertTrue(
            any("not interchangeable" in e for e in errors),
            f"a base row pointing at the so400m artifact must fail; got {errors!r}",
        )

    def test_missing_artifact_is_an_error(self):
        errors, _ = self.run_pointing_at("asset-tags.nope.embeddings.json")
        self.assertTrue(
            any("does not exist" in e for e in errors),
            f"a dangling taxonomy_embeddings pointer must fail; got {errors!r}",
        )


if __name__ == "__main__":
    unittest.main()
GOOD_LITERT = """
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
  - id: on-device/gemma-4-e2b-it-q4f16-webgpu
    source: huggingface://onnx-community/gemma-4-E2B-it-ONNX
    dtype: q4f16
    device: webgpu
    revision: 9f4bef82ea6e296bc69f8a2f5939f73af81b07a6
    mirror_path: on-device/onnx-community__gemma-4-E2B-it-ONNX/9f4bef82ea6e296bc69f8a2f5939f73af81b07a6/
    license: apache-2.0
    license_artifact: licenses/apache-2.0.txt
    size: 1
    files:
      - name: model.onnx
        sha256: 0000000000000000000000000000000000000000000000000000000000000000
        size: 1
    capability: llm-chat
    context_length: 131072
    max_output_tokens: 8192
    tools: true
    thinking: optional
    default: true
  - id: on-device/gemma-4-e2b-it-litert-web
    source: huggingface://litert-community/gemma-4-E2B-it-litert-lm
    file: gemma-4-E2B-it-web.litertlm
    runtime: litert-lm
    dtype: q4
    device: webgpu
    revision: 6b78abd019e61a1ca4cbe3b212d2c9ce8ff38a94
    mirror_path: on-device/litert-community__gemma-4-E2B-it-litert-lm/6b78abd019e61a1ca4cbe3b212d2c9ce8ff38a94/
    license: apache-2.0
    license_artifact: licenses/apache-2.0.txt
    size: 1
    files:
      - name: gemma-4-E2B-it-web.litertlm
        sha256: 0000000000000000000000000000000000000000000000000000000000000000
        size: 1
    capability: llm-chat
    context_length: 32768
    max_output_tokens: 8192
    tools: false
    thinking: none
    modality: [text]
    experimental: true
"""


def _drop_line(body: str, needle: str) -> str:
    """The catalog body with every line containing `needle` removed."""
    return "".join(line for line in body.splitlines(keepends=True) if needle not in line)


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class LitertRowTests(unittest.TestCase):
    """runtime: litert-lm invariants (SBAI-7844).

    Every branch here prevents the same shape of failure: a multi-gigabyte
    download that only dead-ends once it reaches the runtime. The shipped
    catalog is the happy path, so it proves none of them.
    """

    def check(self, body: str) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as td:
            return _run(pathlib.Path(td), {"x.provider.yaml": body})

    def assert_error_matching(self, errors: list[str], needle: str) -> None:
        self.assertTrue(
            any(needle in e for e in errors),
            f"expected an error containing {needle!r}, got {errors!r}",
        )

    def test_good_litert_row_is_clean(self):
        errors, warnings = self.check(GOOD_LITERT)
        self.assertEqual(errors, [])
        self.assertEqual(
            [w for w in warnings if "litert" in w.lower() or "file" in w.lower()], []
        )

    def test_litert_row_without_file_is_an_error(self):
        errors, _ = self.check(_drop_line(GOOD_LITERT, "file: gemma-4-E2B-it-web.litertlm"))
        self.assert_error_matching(errors, "no 'file'")

    def test_litert_row_with_non_litertlm_file_is_an_error(self):
        errors, _ = self.check(
            GOOD_LITERT.replace("gemma-4-E2B-it-web.litertlm", "gemma-4-E2B-it-web.task")
        )
        self.assert_error_matching(errors, ".litertlm files only")

    def test_non_web_litertlm_variant_warns(self):
        # -gpu and the NPU builds download fine and then fail inside the runtime.
        _, warnings = self.check(
            GOOD_LITERT.replace("gemma-4-E2B-it-web.litertlm", "gemma-4-E2B-it-gpu.litertlm")
        )
        self.assertTrue(
            any("-web" in w for w in warnings), f"expected a -web warning, got {warnings!r}"
        )

    def test_litert_row_claiming_non_text_modality_is_an_error(self):
        errors, _ = self.check(GOOD_LITERT.replace("modality: [text]", "modality: [text, image]"))
        self.assert_error_matching(errors, "text-only")

    def test_litert_row_on_wasm_is_an_error(self):
        # Only the litert row's device moves: it is the LAST `device:` line.
        head, sep, tail = GOOD_LITERT.rpartition("    device: webgpu")
        errors, _ = self.check(head + "    device: wasm" + tail if sep else GOOD_LITERT)
        self.assert_error_matching(errors, "WebGPU-only")

    def test_litert_row_over_the_context_ceiling_is_an_error(self):
        errors, _ = self.check(GOOD_LITERT.replace("context_length: 32768", "context_length: 131072"))
        self.assert_error_matching(errors, "ceiling is 32768")

    def test_file_on_a_transformers_row_warns(self):
        # `file` is litert-lm's addressing; transformers.js uses model_file_name.
        _, warnings = self.check(
            GOOD_LITERT.replace("    dtype: q4f16", "    file: model.onnx" + chr(10) + "    dtype: q4f16", 1)
        )
        self.assertTrue(
            any("model_file_name" in w for w in warnings),
            f"expected a model_file_name warning, got {warnings!r}",
        )

    def test_provider_level_litert_runtime_applies_to_unmarked_rows(self):
        # A provider whose header says litert-lm makes its rows litert rows.
        body = GOOD_LITERT.replace("runtime: transformers.js", "runtime: litert-lm", 1)
        errors, _ = self.check(body)
        self.assert_error_matching(errors, "no 'file'")
