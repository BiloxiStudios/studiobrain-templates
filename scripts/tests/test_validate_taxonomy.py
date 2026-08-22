"""Taxonomy + precomputed-embedding invariants (SBAI-7726).

The device downloads a SigLIP vision tower and NOTHING else: every label
vector and the sigmoid calibration come from a committed JSON artifact it
trusts blindly. That makes three things safety-critical, and none of them can
be expressed in a JSON Schema:

  1. ``content_hash`` really is the hash of the axes block (it lives in the
     file it stamps, so only a recompute proves it),
  2. each ``*.embeddings.json`` still matches its taxonomy label-for-label and
     IN ORDER -- a reordered axis silently relabels every asset,
  3. the calibration constants are the model's real learned values -- get
     them wrong and every score in the product is wrong, quietly.

The shipped files are the happy path only, so the negative branches are
proven against synthetic taxonomies in a tmpdir.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import validate  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
TAXONOMY = ROOT / "taxonomies" / "asset-tags.yaml"
BASE_ARTIFACT = ROOT / "taxonomies" / "asset-tags.embeddings.json"
SO400M_ARTIFACT = ROOT / "taxonomies" / "asset-tags.so400m.embeddings.json"

# studiobrain-app/packages/desktop/src-tauri/src/asset_tagger.rs:36-92 -- the
# 50-term TAG_VOCABULARY this taxonomy was seeded from. Pinned here so a future
# edit cannot silently drop a term that assets in the wild are already tagged
# with (assets.tags is matched by a case-sensitive JSON LIKE, so a renamed id
# orphans every existing tag).
TAG_VOCABULARY_SEED = {
    "objects": [
        "character", "vehicle", "weapon", "building", "furniture", "food",
        "plant", "animal", "creature", "robot", "tool", "artifact",
    ],
    "style": [
        "concept_art", "pixel_art", "3d_render", "photograph", "sketch",
        "painting", "ui_element", "icon", "sprite", "texture", "wireframe",
    ],
    "mood": [
        "dark", "bright", "colorful", "muted", "warm", "cool", "dramatic",
        "peaceful", "eerie",
    ],
    "setting": [
        "indoor", "outdoor", "urban", "rural", "fantasy", "sci_fi", "modern",
        "medieval", "underwater", "space",
    ],
    "composition": [
        "portrait", "landscape", "close_up", "wide_shot", "top_down",
        "isometric", "side_view", "panoramic",
    ],
}


def _tools():
    return validate._load_taxonomy_tools()


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class ShippedTaxonomyTests(unittest.TestCase):
    def setUp(self):
        import yaml  # noqa: PLC0415

        self.doc = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))

    def test_shipped_taxonomy_and_artifacts_validate(self):
        self.assertEqual(validate.check_taxonomies(), [])

    def test_seeded_from_the_desktop_tag_vocabulary(self):
        for axis, terms in TAG_VOCABULARY_SEED.items():
            self.assertIn(axis, self.doc["axes"], f"axis {axis} disappeared")
            got = [t["id"] for t in self.doc["axes"][axis]["terms"]]
            missing = [t for t in terms if t not in got]
            self.assertEqual(missing, [], f"axis {axis} dropped seed terms {missing}")
        total_seed = sum(len(v) for v in TAG_VOCABULARY_SEED.values())
        self.assertEqual(total_seed, 50, "the seed itself is the 50-term vocabulary")

    def test_cloud_analysis_axes_are_covered(self):
        """The cloud assets-worker analysis shape has colors + details fields;
        without these axes an on-device analysis can never populate them."""
        for axis in ("colors", "details"):
            self.assertIn(axis, self.doc["axes"])
            self.assertTrue(self.doc["axes"][axis]["terms"])

    def test_term_ids_are_unique_across_the_whole_taxonomy(self):
        """`term` (not `id`) is what lands in assets.tags, so two axes sharing a
        term id would make the persisted tag ambiguous."""
        seen: dict[str, str] = {}
        for axis, body in self.doc["axes"].items():
            for term in body["terms"]:
                tid = term["id"]
                self.assertNotIn(
                    tid, seen, f"term {tid!r} appears in both {seen.get(tid)} and {axis}"
                )
                seen[tid] = axis

    def test_content_hash_is_the_real_hash(self):
        self.assertEqual(self.doc["content_hash"], _tools().content_hash(self.doc))

    def test_content_hash_covers_axis_order_not_just_term_order(self):
        """Reordering axes re-pairs every vector with a different label.

        ``build_labels`` walks axes in document order and the artifact stores
        one vector per label in that order, so an axis swap silently relabels
        the whole taxonomy. ``content_hash`` is the only staleness signal a
        consumer gets, so it has to move when that happens -- a canonical form
        built from a sorted-keys mapping hashes identically before and after
        the swap and would not.
        """
        import copy  # noqa: PLC0415

        tools = _tools()
        base = tools.content_hash(self.doc)

        swapped = copy.deepcopy(self.doc)
        keys = list(self.doc["axes"])
        self.assertGreater(len(keys), 1, "need >1 axis for this to mean anything")
        swapped["axes"] = {k: self.doc["axes"][k] for k in reversed(keys)}
        self.assertNotEqual(
            [lbl["id"] for lbl in tools.build_labels(swapped)],
            [lbl["id"] for lbl in tools.build_labels(self.doc)],
            "precondition: the swap must change label order",
        )
        self.assertNotEqual(
            tools.content_hash(swapped), base, "axis order must be part of content_hash"
        )

        reordered_terms = copy.deepcopy(self.doc)
        first = keys[0]
        reordered_terms["axes"][first]["terms"] = list(
            reversed(self.doc["axes"][first]["terms"])
        )
        self.assertNotEqual(
            tools.content_hash(reordered_terms), base, "term order must be part of content_hash"
        )

        # Cosmetic-only edits must NOT invalidate a good artifact.
        cosmetic = copy.deepcopy(self.doc)
        cosmetic["axes"][first]["display"] = "Totally Different Display Name"
        cosmetic["description"] = "reworded"
        self.assertEqual(
            tools.content_hash(cosmetic), base, "display/description are not part of the pre-image"
        )


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class ArtifactTests(unittest.TestCase):
    """Both tier artifacts, checked for the things a schema cannot see."""

    def artifacts(self):
        for path in (BASE_ARTIFACT, SO400M_ARTIFACT):
            yield path, json.loads(path.read_text(encoding="utf-8"))

    def test_label_order_matches_the_taxonomy(self):
        import yaml  # noqa: PLC0415

        doc = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))
        expected = _tools().build_labels(doc)
        for path, artifact in self.artifacts():
            got = [
                {k: label[k] for k in ("id", "axis", "term", "text")}
                for label in artifact["labels"]
            ]
            self.assertEqual(got, expected, path.name)

    def test_vectors_are_unit_length_and_the_declared_width(self):
        for path, artifact in self.artifacts():
            dim = artifact["model"]["embed_dim"]
            for label in artifact["labels"]:
                vec = label["embedding"]
                self.assertEqual(len(vec), dim, f"{path.name}:{label['id']}")
                norm = math.sqrt(sum(x * x for x in vec))
                self.assertAlmostEqual(norm, 1.0, places=3, msg=f"{path.name}:{label['id']}")

    def test_tiers_have_distinct_widths_and_their_own_calibration(self):
        base = json.loads(BASE_ARTIFACT.read_text(encoding="utf-8"))
        so400m = json.loads(SO400M_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(base["model"]["embed_dim"], 768)
        self.assertEqual(so400m["model"]["embed_dim"], 1152)
        self.assertNotEqual(
            base["scoring"]["logit_scale"],
            so400m["scoring"]["logit_scale"],
            "each checkpoint has its own learned calibration; copying one onto "
            "the other silently miscalibrates every score",
        )

    def test_base_calibration_matches_the_reference_checkpoint(self):
        """Pinned against google/siglip2-base-patch16-256's own tensors.

        Verified end-to-end against the HF PyTorch reference: with these
        constants, sigmoid(logit_scale * cos + logit_bias) reproduces
        SiglipModel's logits_per_image exactly. The checkpoint stores
        logit_scale in log space, so logit_scale must be exp(logit_scale_raw)
        -- shipping the raw 4.7265 as the multiplier is the easy, silent bug.
        """
        art = json.loads(BASE_ARTIFACT.read_text(encoding="utf-8"))
        scoring = art["scoring"]
        self.assertAlmostEqual(scoring["logit_scale_raw"], 4.726512908935547, places=6)
        self.assertAlmostEqual(scoring["logit_scale"], 112.9011784315, places=6)
        self.assertAlmostEqual(scoring["logit_bias"], -16.77180290222168, places=6)
        self.assertAlmostEqual(
            scoring["logit_scale"], math.exp(scoring["logit_scale_raw"]), places=6
        )
        self.assertTrue(scoring["embeddings_l2_normalized"])
        self.assertIn("sigmoid", scoring["formula"])

    def test_selection_policy_is_shipped_with_the_calibration(self):
        """A bare probability cut emits zero tags: SigLIP's sigmoid is
        calibrated for specific-caption retrieval, and this taxonomy is
        deliberately generic. The artifact has to carry the rank-based policy
        or every consumer re-derives it wrong."""
        for path, artifact in self.artifacts():
            scoring = artifact["scoring"]
            self.assertGreaterEqual(scoring["default_top_k_per_axis"], 1, path.name)
            self.assertLess(
                scoring["default_threshold"], 0.05,
                f"{path.name}: a high absolute floor would tag nothing",
            )
            self.assertIn("selection_note", scoring, path.name)

    def test_provenance_is_complete(self):
        for path, artifact in self.artifacts():
            model = artifact["model"]
            self.assertTrue(model["id"].startswith("onnx-community/"), path.name)
            self.assertEqual(len(model["revision"]), 40, f"{path.name}: not a pinned commit sha")
            self.assertEqual(model["tower"], "text", path.name)
            self.assertEqual(model["tokenizer"]["padding"], "max_length", path.name)
            self.assertEqual(model["tokenizer"]["max_length"], 64, path.name)
            src = artifact["scoring"]["calibration_source"]
            self.assertEqual(len(src["revision"]), 40, path.name)


@unittest.skipUnless(validate.HAVE_YAML, "pyyaml required")
class NegativeBranchTests(unittest.TestCase):
    """Prove each check_taxonomies() failure branch actually fires."""

    GOOD_YAML = """\
id: test.tax
kind: taxonomy
display: Test
revision: 1.0.0
content_hash: {content_hash}
axes:
  shape:
    hypothesis_template: a photo of {{}}.
    terms:
      - id: circle
        prompt: a circle
      - id: square
        prompt: a square
"""

    def build(self, tmp: pathlib.Path, *, yaml_text: str | None = None, artifact=None):
        import yaml  # noqa: PLC0415

        tools = _tools()
        skeleton = self.GOOD_YAML.format(content_hash="sha256:" + "0" * 64)
        doc = yaml.safe_load(skeleton)
        good_text = self.GOOD_YAML.format(content_hash=tools.content_hash(doc))
        (tmp / "t.yaml").write_text(yaml_text or good_text, encoding="utf-8")
        if artifact is not None:
            (tmp / "t.embeddings.json").write_text(
                json.dumps(artifact), encoding="utf-8"
            )
        old = validate.TAXONOMIES_DIR
        validate.TAXONOMIES_DIR = tmp
        try:
            return validate.check_taxonomies()
        finally:
            validate.TAXONOMIES_DIR = old

    def good_artifact(self, **overrides):
        import yaml  # noqa: PLC0415

        tools = _tools()
        doc = yaml.safe_load(self.GOOD_YAML.format(content_hash="sha256:" + "0" * 64))
        labels = tools.build_labels(doc)
        art = {
            "artifact_schema_version": 1,
            "taxonomy": {
                "id": "test.tax",
                "revision": "1.0.0",
                "content_hash": tools.content_hash(doc),
            },
            "model": {
                "id": "onnx-community/x",
                "revision": "a" * 40,
                "file": "onnx/text_model.onnx",
                "embed_dim": 2,
                "tower": "text",
            },
            "scoring": {"formula": "sigmoid(...)", "logit_scale": 1.0, "logit_bias": 0.0},
            "label_count": len(labels),
            "labels": [dict(l, embedding=[1.0, 0.0]) for l in labels],
        }
        art.update(overrides)
        return art

    def assert_error_matching(self, errors, needle):
        self.assertTrue(
            any(needle in e for e in errors),
            f"expected an error containing {needle!r}, got {errors!r}",
        )

    def test_good_pair_is_clean(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(self.build(pathlib.Path(td), artifact=self.good_artifact()), [])

    def test_stale_content_hash_errors(self):
        bad = self.GOOD_YAML.format(content_hash="sha256:" + "b" * 64)
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), yaml_text=bad)
        self.assert_error_matching(errors, "content_hash is stale")

    def test_stale_artifact_errors(self):
        art = self.good_artifact()
        art["taxonomy"]["content_hash"] = "sha256:" + "c" * 64
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "artifact is STALE")

    def test_reordered_labels_error(self):
        art = self.good_artifact()
        art["labels"] = list(reversed(art["labels"]))
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "taxonomy order says")

    def test_label_count_mismatch_errors(self):
        art = self.good_artifact()
        art["labels"] = art["labels"][:1]
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "label vectors but the taxonomy has")

    def test_wrong_vector_width_errors(self):
        art = self.good_artifact()
        art["labels"][0]["embedding"] = [1.0, 0.0, 0.0]
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "model.embed_dim says")

    def test_non_unit_vector_errors(self):
        art = self.good_artifact()
        art["labels"][0]["embedding"] = [3.0, 4.0]
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "expected a unit vector")

    def test_missing_calibration_errors(self):
        art = self.good_artifact()
        del art["scoring"]["logit_scale"]
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "scoring.logit_scale missing")

    def test_artifact_for_unknown_taxonomy_errors(self):
        art = self.good_artifact()
        art["taxonomy"]["id"] = "nope"
        with tempfile.TemporaryDirectory() as td:
            errors = self.build(pathlib.Path(td), artifact=art)
        self.assert_error_matching(errors, "which no taxonomies/*.yaml declares")


if __name__ == "__main__":
    unittest.main()
