"""Tests for the weights-mirror manifest builder + verifier (SBAI-7881, epic
SBAI-7842).

Every test here runs entirely offline against synthetic tmpdirs -- no test
calls a bucket API, and none calls the network (the ``--verify-remote`` HTTP
path is exercised nowhere in this file). That is the literal proof of the
ticket's "no production bucket mutation in tests" requirement: the staging-set
gate is tested against a plain JSON fixture standing in for whatever process
(SBAI-7882) eventually produces a real one.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build_mirror_manifest as bmm  # noqa: E402
import verify_mirror_manifest as vmm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

GOOD_ROW = {
    "id": "on-device/test-row",
    "source": "huggingface://onnx-community/test-repo",
    "revision": "9f4bef82ea6e296bc69f8a2f5939f73af81b07a6",
    "mirror_path": "on-device/onnx-community__test-repo/9f4bef82ea6e296bc69f8a2f5939f73af81b07a6/",
    "license": "apache-2.0",
    "license_artifact": "licenses/apache-2.0.txt",
    "size": 30,
    "files": [
        {"name": "model.onnx", "sha256": "a" * 64, "size": 10},
        {"name": "model.onnx_data", "sha256": "b" * 64, "size": 20},
    ],
}


def _entry(**overrides):
    entry = json.loads(json.dumps(GOOD_ROW))  # deep copy
    entry.update(overrides)
    return entry


class CheckStructuralTests(unittest.TestCase):
    def test_valid_entry_is_clean(self):
        errors = vmm.check_structural([_entry()], root=ROOT)
        self.assertEqual(errors, [])

    def test_mutable_revision_is_refused(self):
        for bad in ("main", "latest", "HEAD", "9f4bef8"):  # short SHA is also refused
            with self.subTest(revision=bad):
                errors = vmm.check_structural([_entry(revision=bad)], root=ROOT)
                self.assertTrue(
                    any("not an immutable pin" in e for e in errors),
                    f"revision {bad!r} must be refused; got {errors!r}",
                )

    def test_unlisted_license_is_refused(self):
        for bad in ("apple-amlr", "gpl-3.0", ""):
            with self.subTest(license=bad):
                errors = vmm.check_structural([_entry(license=bad)], root=ROOT)
                self.assertTrue(
                    any("not in the redistributable allow-list" in e for e in errors),
                    f"license {bad!r} must be refused; got {errors!r}",
                )

    def test_missing_license_artifact_file_is_refused(self):
        errors = vmm.check_structural(
            [_entry(license_artifact="licenses/does-not-exist.txt")], root=ROOT
        )
        self.assertTrue(any("does not exist on disk" in e for e in errors))

    def test_present_license_artifact_file_passes(self):
        errors = vmm.check_structural([_entry(license_artifact="licenses/mit.txt")], root=ROOT)
        self.assertEqual(errors, [])

    def test_bad_sha256_is_refused(self):
        entry = _entry()
        entry["files"][0]["sha256"] = "not-hex"
        errors = vmm.check_structural([entry], root=ROOT)
        self.assertTrue(any("is not 64 lowercase hex characters" in e for e in errors))

    def test_size_drift_from_files_sum_is_refused(self):
        errors = vmm.check_structural([_entry(size=999)], root=ROOT)
        self.assertTrue(
            any("does not equal the sum of files" in e for e in errors),
            f"a hand-edited size that disagrees with files[].size must fail; got {errors!r}",
        )

    def test_empty_files_is_refused(self):
        errors = vmm.check_structural([_entry(files=[])], root=ROOT)
        self.assertTrue(any("no files declared" in e for e in errors))

    def test_two_rows_sharing_an_object_key_with_identical_content_is_fine(self):
        """Sibling dtype rows on the same source+revision legitimately share a
        mirror prefix -- the SAME file published once is not a collision."""
        a = _entry(id="row-a")
        b = _entry(id="row-b")  # identical mirror_path + files -> same object keys, same bytes
        errors = vmm.check_structural([a, b], root=ROOT)
        self.assertEqual(errors, [])

    def test_two_rows_sharing_an_object_key_with_different_content_is_refused(self):
        a = _entry(id="row-a")
        b = _entry(id="row-b")
        b["files"][0]["sha256"] = "c" * 64  # same name, same mirror_path, DIFFERENT hash
        errors = vmm.check_structural([a, b], root=ROOT)
        self.assertTrue(
            any("collides with row" in e for e in errors),
            f"a checksum collision on one object key must fail; got {errors!r}",
        )


class CheckStagingTests(unittest.TestCase):
    """The staging-set gate is pure JSON-vs-JSON comparison -- no network, no bucket."""

    def test_object_present_in_staging_set_passes(self):
        with tempfile.TemporaryDirectory() as td:
            staging = pathlib.Path(td) / "staged.json"
            staging.write_text(json.dumps({
                "objects": [
                    GOOD_ROW["mirror_path"] + "model.onnx",
                    GOOD_ROW["mirror_path"] + "model.onnx_data",
                ]
            }), encoding="utf-8")
            errors = vmm.check_staging([_entry()], staging)
        self.assertEqual(errors, [])

    def test_object_absent_from_staging_set_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            staging = pathlib.Path(td) / "staged.json"
            staging.write_text(json.dumps({"objects": []}), encoding="utf-8")
            errors = vmm.check_staging([_entry()], staging)
        self.assertTrue(
            any("absent from the mirror staging set" in e for e in errors),
            f"an unstaged object must fail; got {errors!r}",
        )

    def test_unreadable_staging_file_is_an_error_not_a_crash(self):
        errors = vmm.check_staging([_entry()], pathlib.Path("/nonexistent/staged.json"))
        self.assertTrue(any("cannot read staging set" in e for e in errors))


class BuildMirrorManifestTests(unittest.TestCase):
    """build_entries scans templates/Providers/*.provider.yaml for wire:in-app
    weights rows -- rows missing the mirror contract fields are skipped, not
    errored (that gate belongs to check_structural/check_requires)."""

    COMPLETE_PROVIDER = """
id: on-device-test
kind: provider
wire: in-app
runtime: transformers.js
provides: [llm-chat]
weights:
  - id: on-device/complete-row
    source: huggingface://onnx-community/test-repo
    dtype: q4
    device: webgpu
    revision: 9f4bef82ea6e296bc69f8a2f5939f73af81b07a6
    mirror_path: on-device/onnx-community__test-repo/9f4bef82ea6e296bc69f8a2f5939f73af81b07a6/
    license: apache-2.0
    license_artifact: licenses/apache-2.0.txt
    size: 10
    files:
      - name: model.onnx
        sha256: {sha}
        size: 10
"""

    INCOMPLETE_PROVIDER = """
id: on-device-incomplete
kind: provider
wire: in-app
runtime: transformers.js
provides: [llm-chat]
weights:
  - id: on-device/incomplete-row
    source: huggingface://onnx-community/other-repo
    dtype: q4
    device: webgpu
"""

    NON_IN_APP_PROVIDER = """
id: cloud-test
kind: provider
wire: openai-compat
base_url: https://api.example.com
"""

    def _build(self, files: dict[str, str]):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            providers_dir = tmp / "templates" / "Providers"
            providers_dir.mkdir(parents=True)
            for name, body in files.items():
                (providers_dir / name).write_text(body, encoding="utf-8")
            return bmm.build_entries(tmp)

    def test_complete_row_is_included(self):
        entries = self._build({
            "x.provider.yaml": self.COMPLETE_PROVIDER.format(sha="d" * 64),
        })
        self.assertEqual([e["id"] for e in entries], ["on-device/complete-row"])
        self.assertEqual(entries[0]["provider"], "on-device-test")

    def test_incomplete_row_is_skipped_not_errored(self):
        """A row mid-backfill (missing mirror fields) must not crash the build --
        scripts/validate.py's check_requires is what flags it as an error."""
        entries = self._build({"x.provider.yaml": self.INCOMPLETE_PROVIDER})
        self.assertEqual(entries, [])

    def test_non_in_app_provider_is_ignored(self):
        entries = self._build({"x.provider.yaml": self.NON_IN_APP_PROVIDER})
        self.assertEqual(entries, [])

    def test_duplicate_row_id_across_files_raises(self):
        with self.assertRaises(RuntimeError):
            self._build({
                "a.provider.yaml": self.COMPLETE_PROVIDER.format(sha="d" * 64),
                "b.provider.yaml": self.COMPLETE_PROVIDER.format(sha="e" * 64).replace(
                    "on-device-test", "on-device-test-2"
                ),
            })


class ShippedMirrorManifestTests(unittest.TestCase):
    """The real templates/Providers/*.provider.yaml + mirror-manifest.json must
    both satisfy the contract -- this is what scripts/validate.py's
    check_mirror_manifest() enforces in CI."""

    def test_shipped_catalog_has_no_structural_errors(self):
        entries = bmm.build_entries(ROOT)
        self.assertTrue(entries, "expected at least one backfilled wire:in-app weights row")
        errors = vmm.check_structural(entries, root=ROOT)
        self.assertEqual(errors, [])

    def test_shipped_catalog_has_no_blocked_licenses(self):
        entries = bmm.build_entries(ROOT)
        offenders = [e["id"] for e in entries if e["license"] not in vmm._ALLOWED_LICENSES]
        self.assertEqual(offenders, [], "FastVLM/apple-amlr-class licenses must never ship")


if __name__ == "__main__":
    unittest.main()
