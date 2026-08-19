"""Negative-evidence tests for scripts/check_workflow_secret_isolation.py
(SBAI-7183): proves the checker actually catches a secret leaking into a
pull_request-reachable job, and does not false-positive on the real,
correctly-gated workflow.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import check_workflow_secret_isolation as checker  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

BAD_WORKFLOW = """
name: bad
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  leaky:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ secrets.R2_ACCESS_KEY_ID }}"
"""

GOOD_WORKFLOW = """
name: good
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "no secrets here"
  publish:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - run: echo "${{ secrets.R2_ACCESS_KEY_ID }}"
"""

GITHUB_TOKEN_ONLY_WORKFLOW = """
name: token-only
on:
  pull_request:
    branches: [main]
jobs:
  checkout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
"""


class CheckWorkflowSecretIsolationTest(unittest.TestCase):
    def _check(self, contents: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "wf.yml"
            path.write_text(contents, encoding="utf-8")
            return checker.check_workflow(path)

    def test_catches_secret_in_ungated_pull_request_job(self):
        errors = self._check(BAD_WORKFLOW)
        self.assertTrue(errors, "checker must flag a secret in an ungated PR-reachable job")
        self.assertIn("R2_ACCESS_KEY_ID", errors[0])

    def test_allows_secret_in_push_gated_job(self):
        errors = self._check(GOOD_WORKFLOW)
        self.assertEqual(errors, [], f"push-gated job must not be flagged: {errors}")

    def test_github_token_is_always_safe(self):
        errors = self._check(GITHUB_TOKEN_ONLY_WORKFLOW)
        self.assertEqual(errors, [], f"GITHUB_TOKEN must never be flagged: {errors}")

    def test_real_repo_workflows_pass(self):
        """The actual checked-in workflow(s) must pass this checker — this is
        what runs in CI on every PR."""
        workflows_dir = ROOT / ".github" / "workflows"
        all_errors = []
        for path in sorted(workflows_dir.glob("*.yml")):
            all_errors.extend(checker.check_workflow(path))
        self.assertEqual(all_errors, [], f"real workflow(s) failed the isolation check: {all_errors}")


if __name__ == "__main__":
    unittest.main()
