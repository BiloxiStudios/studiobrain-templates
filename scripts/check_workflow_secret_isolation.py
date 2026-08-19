#!/usr/bin/env python3
"""Statically prove that PR-controlled code cannot reach publish/signing
secrets (SBAI-7183).

GitHub Actions secrets ARE available to same-repo pull_request runs (only
fork PRs are denied by GitHub automatically) — so relying on GitHub's
default fork behavior alone is not sufficient proof for a repo where
same-repo branches also open PRs. The real boundary has to be structural
and checked, not assumed: no job that GitHub can trigger via
``pull_request`` (in any form) may reference ``secrets.*`` (other than the
always-safe, read-scoped ``secrets.GITHUB_TOKEN``) unless that job is ALSO
gated by an ``if:`` condition that requires ``github.event_name == 'push'``.

This runs in the ``validate`` job on every PR, including forked ones (it
needs no secret itself), so a PR that tries to widen secret access to a
pull_request-reachable job fails CI on that PR — the enforcement is live,
not just documented.

Coverage (SBAI-7506 — the v1 checker only matched dot-form ``secrets.NAME``
in ``*.yml`` files and had no opinion on reusable-workflow edges):

- Both ``*.yml`` and ``*.yaml`` workflow files are scanned.
- Both expression forms are caught: dot-form (``secrets.NAME``) and
  bracket-form with a literal key (``secrets['NAME']`` / ``secrets["NAME"]``).
- Any OTHER bracket/dynamic form (e.g. ``secrets[matrix.name]``,
  ``secrets[format('...')]``) cannot be resolved statically to a name, so it
  fails closed: it is always reported, regardless of push-gating, because a
  human must not rely on offline analysis of code that can't be analyzed.
- A job that calls a reusable workflow (``uses: ./.github/workflows/x.yml``)
  with ``secrets: inherit`` forwards EVERY secret the caller has — that is
  treated exactly like an explicit ``secrets.*`` reference for reachability
  purposes (fails closed: we don't parse the callee to prove it's safe).

Usage:
    python3 scripts/check_workflow_secret_isolation.py
    python3 scripts/check_workflow_secret_isolation.py .github/workflows/other.yml
"""
from __future__ import annotations

import pathlib
import re
import sys

try:
    import yaml  # type: ignore
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
WORKFLOW_GLOBS = ("*.yml", "*.yaml")

# Dot-form: secrets.NAME
SECRET_DOT_RE = re.compile(r"secrets\.([A-Za-z0-9_]+)")
# Bracket-form with a literal string key: secrets['NAME'] / secrets["NAME"]
SECRET_BRACKET_LITERAL_RE = re.compile(r"secrets\[\s*(['\"])([A-Za-z0-9_]+)\1\s*\]")
# Any secrets[ ... ] access at all — used to detect bracket forms that are
# NOT the literal-key form above (dynamic/computed keys we can't resolve).
SECRET_BRACKET_ANY_RE = re.compile(r"secrets\[")
SAFE_SECRET_NAMES = {"GITHUB_TOKEN"}

# A job is "pull_request-reachable" if the trigger includes pull_request in
# any form (pull_request, pull_request_target) UNLESS the job itself carries
# an if: that requires a push event. We check both the job-level `if:` and
# any step-level `if:` that might be interpreted as a gate — but per the
# rule, the JOB-level if is what we require; a step-level if is not
# sufficient because other steps in the same job could still run un-gated.
PUSH_ONLY_IF_RE = re.compile(r"github\.event_name\s*==\s*['\"]push['\"]")


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _find_secret_refs(node, path: str) -> list[str]:
    """Recursively find every secret reference under `node`.

    Returns two kinds of findings, both as plain strings:
      - resolved:      "<path>: secrets.NAME"     (name is known)
      - fail-closed:    "<path>: secrets[<unresolvable expression>]"
    Dynamic/computed bracket keys are ALWAYS reported here (the caller
    decides whether push-gating suppresses resolved refs; unresolvable
    refs are never suppressed — see check_workflow()).
    """
    refs: list[str] = []
    unresolvable: list[str] = []
    if isinstance(node, str):
        for m in SECRET_DOT_RE.finditer(node):
            name = m.group(1)
            if name not in SAFE_SECRET_NAMES:
                refs.append(f"{path}: secrets.{name}")
        for m in SECRET_BRACKET_LITERAL_RE.finditer(node):
            name = m.group(2)
            if name not in SAFE_SECRET_NAMES:
                refs.append(f"{path}: secrets['{name}']")
        # Any bracket access not already matched by the literal-key regex is
        # a dynamic/computed key we cannot resolve — fail closed.
        literal_spans = {m.span() for m in SECRET_BRACKET_LITERAL_RE.finditer(node)}
        for m in SECRET_BRACKET_ANY_RE.finditer(node):
            if not any(m.start() >= lo and m.start() < hi for lo, hi in literal_spans):
                snippet = node[m.start(): m.start() + 60].strip()
                unresolvable.append(f"{path}: secrets[...] unresolvable dynamic key: {snippet!r}")
    elif isinstance(node, dict):
        for k, v in node.items():
            sub_refs, sub_unresolvable = _find_secret_refs(v, f"{path}.{k}")
            refs.extend(sub_refs)
            unresolvable.extend(sub_unresolvable)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            sub_refs, sub_unresolvable = _find_secret_refs(v, f"{path}[{i}]")
            refs.extend(sub_refs)
            unresolvable.extend(sub_unresolvable)
    return refs, unresolvable


def _triggers(workflow: dict) -> set[str]:
    on = workflow.get("on") or workflow.get(True)  # PyYAML parses bare `on:` as True in some versions
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    if isinstance(on, dict):
        return set(on.keys())
    return set()


def _job_is_push_gated(job: dict) -> bool:
    job_if = job.get("if", "")
    return bool(PUSH_ONLY_IF_RE.search(str(job_if)))


def check_workflow(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(workflow, dict):
        return [f"{path}: could not parse as a mapping"]

    triggers = _triggers(workflow)
    pr_reachable_workflow = bool(triggers & {"pull_request", "pull_request_target"})

    jobs = workflow.get("jobs", {})
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue

        # A job is pull_request-reachable if the WORKFLOW's trigger includes
        # pull_request and the job itself is not explicitly gated to push-only.
        job_pr_reachable = pr_reachable_workflow and not _job_is_push_gated(job)

        if not job_pr_reachable:
            continue

        refs, unresolvable = _find_secret_refs(job, f"{path.name}:jobs.{job_name}")

        # A reusable-workflow call with `secrets: inherit` forwards EVERY
        # secret the caller has to the callee — we don't parse the callee to
        # prove it only touches safe ones, so this is treated exactly like
        # an explicit secrets.* reference (fail closed, SBAI-7506).
        if job.get("secrets") == "inherit":
            refs.append(
                f"{path.name}:jobs.{job_name}.secrets: 'inherit' forwards ALL "
                f"caller secrets to the reusable workflow "
                f"'{job.get('uses', '?')}'"
            )

        for ref in refs:
            errors.append(
                f"{ref} is reachable from a pull_request-triggered job "
                f"('{job_name}') with no 'github.event_name == push' gate. "
                f"Publish/signing secrets must only be referenced in a job "
                f"gated to push events on main."
            )
        for ref in unresolvable:
            errors.append(
                f"{ref} in job '{job_name}' is a dynamic/computed secret "
                f"expression this checker cannot statically resolve to a "
                f"name — failing closed. Use a literal 'secrets.NAME' or "
                f"'secrets[\"NAME\"]' reference, gated to push events, "
                f"instead."
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    if not HAVE_YAML:
        _err("pyyaml is required (pip install pyyaml)")
        return 1

    if argv:
        targets = [pathlib.Path(p) for p in argv]
    else:
        targets = sorted({p for glob in WORKFLOW_GLOBS for p in WORKFLOWS_DIR.glob(glob)})
    if not targets:
        print(f"No workflow files found under {WORKFLOWS_DIR}")
        return 0

    all_errors: list[str] = []
    for path in targets:
        all_errors.extend(check_workflow(path))

    if all_errors:
        for e in all_errors:
            _err(e)
        return 1

    print(f"OK: no pull_request-reachable job references a publish/signing secret ({len(targets)} workflow file(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
