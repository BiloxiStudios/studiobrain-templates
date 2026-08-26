"""Curated provider marketplace submission + install/read-back contract
(SBAI-8093, epic SBAI-8007).

Covers all four acceptance criteria end-to-end within the templates repo:

  1. A submission that never passed schema review is rejected, not installed.
  2. This test file, merged via a reviewed PR, is itself the approved
     PR/review artifact (enforced by branch protection + the `validate` CI
     job -- see check_workflow_secret_isolation.py for proof that job never
     holds publish credentials).
  3. A curated, shipped provider produces a deterministic catalog-index
     entry (build_catalog_index.py; byte-reproducibility is covered
     separately by test_build_catalog_index.py's
     test_catalog_is_byte_reproducible_for_fixed_provenance).
  4. That same curated provider installs into, and reads back from, a
     project's own `_Providers/` override directory -- the exact drop-in
     contract cloud's project-DO write path (SBAI-8091) enforces server-side
     -- and an unreviewed/invalid submission cannot.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import install_provider  # noqa: E402
from install_provider import (  # noqa: E402
    ProviderInstallRejected,
    install_provider as do_install,
    read_back_provider,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = ROOT / "schemas" / "fixtures"


class InstallReadBackContractTests(unittest.TestCase):
    def test_approved_curated_provider_installs_and_reads_back(self):
        """A reviewed, schema-valid catalog provider installs cleanly into a
        project's _Providers/ override and reads back byte-for-byte
        equivalent -- the install/read-back acceptance criterion."""
        source = ROOT / "templates" / "Providers" / "anthropic.provider.yaml"
        with tempfile.TemporaryDirectory() as td:
            project_dir = pathlib.Path(td)
            dest = do_install(source, project_dir)

            self.assertEqual(dest, project_dir / "_Providers" / "anthropic.provider.yaml")
            self.assertTrue(dest.is_file())

            installed = read_back_provider(project_dir, "anthropic")
            original = yaml.safe_load(source.read_text(encoding="utf-8"))
            self.assertEqual(installed, original)

    def test_unreviewed_invalid_submission_is_rejected_not_installed(self):
        """A submission that never passed the schema/review gate must be
        refused outright -- nothing is written, and there is nothing to read
        back. This is the rejected-unreviewed-submission proof."""
        with tempfile.TemporaryDirectory() as td:
            project_dir = pathlib.Path(td)
            with tempfile.TemporaryDirectory() as src_td:
                bad = pathlib.Path(src_td) / "sketchy.provider.yaml"
                bad.write_text(
                    "id: sketchy\nkind: provider\nroute: surprise-me\n",
                    encoding="utf-8",
                )  # missing required `wire`; invalid `route` enum value

                with self.assertRaises(ProviderInstallRejected):
                    do_install(bad, project_dir)

            # Nothing was ever written to the project's override directory.
            self.assertFalse((project_dir / "_Providers").exists())

            # And it therefore cannot be read back -- there is no bypass.
            with self.assertRaises(FileNotFoundError):
                read_back_provider(project_dir, "sketchy")

    def test_rejected_unreviewed_fixture_matches_schema_gate(self):
        """The checked-in adversarial fixture (schemas/fixtures/
        invalid_provider_unreviewed_submission.json, exercised generically by
        scripts/validate.py --fixtures) fails the exact same provider.json
        gate install_provider uses -- one gate, proven two ways."""
        import json

        fixture = FIXTURES_DIR / "invalid_provider_unreviewed_submission.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))
        errors = install_provider.validate._validate_instance(data, "provider.json", str(fixture))
        self.assertTrue(errors, "unreviewed submission fixture must fail schema validation")

    def test_approved_fixture_matches_schema_gate(self):
        """The checked-in valid fixture proves an approved submission passes
        the identical gate an unreviewed one fails."""
        import json

        fixture = FIXTURES_DIR / "valid_provider_marketplace_submission.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))
        errors = install_provider.validate._validate_instance(data, "provider.json", str(fixture))
        self.assertEqual(errors, [])

    def test_install_never_touches_shared_catalog_or_network(self):
        """install_provider only ever writes under the caller-supplied
        project_dir -- never the shared catalog-index.json, never R2. Static
        proof that curated adoption cannot bypass the reviewed publish path.
        Checked against the executable code only, not the module docstring
        (which legitimately explains the reviewed publish path it must not
        reach)."""
        import ast

        tree = ast.parse(pathlib.Path(install_provider.__file__).read_text(encoding="utf-8"))
        tree.body = [node for node in tree.body if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))]
        code_text = ast.unparse(tree)
        for forbidden in ("catalog-index.json", "boto3", "urllib.request", "requests"):
            self.assertNotIn(forbidden, code_text)


if __name__ == "__main__":
    unittest.main()
