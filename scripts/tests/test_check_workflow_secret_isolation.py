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

BRACKET_LITERAL_WORKFLOW = """
name: bracket-literal
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  leaky:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ secrets['R2_ACCESS_KEY_ID'] }}"
"""

BRACKET_DYNAMIC_WORKFLOW = """
name: bracket-dynamic
on:
  pull_request:
    branches: [main]
jobs:
  leaky:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env_name: [staging, production]
    steps:
      - run: echo "${{ secrets[format('{0}_TOKEN', matrix.env_name)] }}"
"""

REUSABLE_WORKFLOW_SECRETS_INHERIT = """
name: reusable-inherit
on:
  pull_request:
    branches: [main]
jobs:
  call-it:
    uses: ./.github/workflows/other.yml
    secrets: inherit
"""

REUSABLE_WORKFLOW_PUSH_GATED_INHERIT = """
name: reusable-inherit-gated
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  call-it:
    if: github.event_name == 'push'
    uses: ./.github/workflows/other.yml
    secrets: inherit
"""


class CheckWorkflowSecretIsolationTest(unittest.TestCase):
    def _check(self, contents: str, filename: str = "wf.yml") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / filename
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

    def test_catches_bracket_literal_secret_in_yaml_extension(self):
        # Also proves *.yaml (not just *.yml) is understood by check_workflow
        # directly (the extension-glob coverage is proven by main()/the
        # WORKFLOW_GLOBS constant, exercised in test_real_repo_workflows_pass).
        errors = self._check(BRACKET_LITERAL_WORKFLOW, filename="wf.yaml")
        self.assertTrue(errors, "bracket-literal secrets['NAME'] must be caught")
        self.assertIn("R2_ACCESS_KEY_ID", errors[0])

    def test_catches_dynamic_bracket_secret_fail_closed(self):
        errors = self._check(BRACKET_DYNAMIC_WORKFLOW)
        self.assertTrue(errors, "an unresolvable dynamic secrets[...] expression must fail closed")
        self.assertIn("dynamic/computed secret expression", errors[0])

    def test_catches_reusable_workflow_secrets_inherit_when_pr_reachable(self):
        errors = self._check(REUSABLE_WORKFLOW_SECRETS_INHERIT)
        self.assertTrue(errors, "secrets: inherit on a PR-reachable reusable-workflow call must be caught")
        self.assertIn("inherit", errors[0])

    def test_allows_reusable_workflow_secrets_inherit_when_push_gated(self):
        errors = self._check(REUSABLE_WORKFLOW_PUSH_GATED_INHERIT)
        self.assertEqual(errors, [], f"push-gated secrets: inherit must not be flagged: {errors}")

    def test_real_repo_workflows_pass(self):
        """The actual checked-in workflow(s) must pass this checker — this is
        what runs in CI on every PR."""
        workflows_dir = ROOT / ".github" / "workflows"
        all_errors = []
        for glob in checker.WORKFLOW_GLOBS:
            for path in sorted(workflows_dir.glob(glob)):
                all_errors.extend(checker.check_workflow(path))
        self.assertEqual(all_errors, [], f"real workflow(s) failed the isolation check: {all_errors}")


if __name__ == "__main__":
    unittest.main()
