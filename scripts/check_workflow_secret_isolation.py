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

SECRET_REF_RE = re.compile(r"secrets\.([A-Za-z0-9_]+)")
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
    """Recursively find every 'secrets.<NAME>' reference under `node`."""
    refs = []
    if isinstance(node, str):
        for m in SECRET_REF_RE.finditer(node):
            name = m.group(1)
            if name not in SAFE_SECRET_NAMES:
                refs.append(f"{path}: secrets.{name}")
    elif isinstance(node, dict):
        for k, v in node.items():
            refs.extend(_find_secret_refs(v, f"{path}.{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            refs.extend(_find_secret_refs(v, f"{path}[{i}]"))
    return refs


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

        refs = _find_secret_refs(job, f"{path.name}:jobs.{job_name}")
        if refs:
            for ref in refs:
                errors.append(
                    f"{ref} is reachable from a pull_request-triggered job "
                    f"('{job_name}') with no 'github.event_name == push' gate. "
                    f"Publish/signing secrets must only be referenced in a job "
                    f"gated to push events on main."
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    if not HAVE_YAML:
        _err("pyyaml is required (pip install pyyaml)")
        return 1

    targets = [pathlib.Path(p) for p in argv] if argv else sorted(WORKFLOWS_DIR.glob("*.yml"))
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
