#!/usr/bin/env python3
"""Exercise the real merge-hold workflow with controlled GitHub API responses."""
import os
import re
from pathlib import Path
import subprocess
import tempfile
import textwrap

root = Path(__file__).resolve().parents[2]
workflow = (root / ".github/workflows/merge-hold-gate.yml").read_text()
step = workflow.split("- name: Fail closed if a hold label is present\n", 1)[1]
step = step.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0]
step = textwrap.dedent(step)
assert "gh api" in step, "Test must exercise the live label lookup"

# The API is the only stub: execute the exact production shell and Python.
cases = [
    ("API unavailable, empty opened payload", 1, "", "[]", False),
    ("API unavailable, held payload", 1, "", '[{"name":"merge-hold"}]', False),
    ("live hold overrides empty payload", 0, '[{"name":"merge-hold"}]', "[]", False),
    ("live clear overrides stale hold", 0, "[]", '[{"name":"merge-hold"}]', True),
    ("manual merge is not a fence label", 0, '[{"name":"manual-merge"}]', "[]", True),
    ("malformed live JSON", 0, "not-json", "[]", False),
    ("empty live response", 0, "", "[]", False),
]
with tempfile.TemporaryDirectory(prefix="merge-hold-regression-") as directory:
    fixture = Path(directory)
    gh = fixture / "gh"
    gh.write_text('#!/bin/sh\nprintf "%s\\n" "$LIVE_LABELS"\nexit "$API_EXIT"\n')
    gh.chmod(0o755)
    failures = []
    for name, api_exit, live, payload, should_pass in cases:
        env = {**os.environ, "PATH": f"{fixture}:{os.environ['PATH']}",
               "GH_TOKEN": "offline-test", "REPO": "fixture/repo", "PR_NUMBER": "1",
               "API_EXIT": str(api_exit), "LIVE_LABELS": live, "LABELS_JSON": payload}
        result = subprocess.run(["bash", "-c", step], env=env, text=True,
                                capture_output=True, timeout=10)
        actual_pass = result.returncode == 0
        if actual_pass != should_pass:
            failures.append(name)
            print(f"FAIL {name}: exit={result.returncode}\n{result.stdout}{result.stderr}")
        else:
            print(f"PASS {name}")
    if failures:
        raise SystemExit(f"{len(failures)} workflow regression(s): {failures}")
print(f"All {len(cases)} workflow regressions passed")

# --- SBAI-8585: the CHANGES_REQUESTED step must stay fail-closed -----------------
review_step = workflow.split(
    "- name: Fail closed if reviewDecision is CHANGES_REQUESTED\n", 1)[1]
review_step = textwrap.dedent(review_step.split("        run: |\n", 1)[1])
assert "gh pr view" in review_step, "Test must exercise the reviewDecision lookup"

review_cases = [
    ("CHANGES_REQUESTED blocks", 0, "CHANGES_REQUESTED", False),
    ("APPROVED passes", 0, "APPROVED", True),
    ("REVIEW_REQUIRED passes", 0, "REVIEW_REQUIRED", True),
    ("no review decision passes", 0, "", True),
    ("review lookup failure blocks", 1, "", False),
]
with tempfile.TemporaryDirectory(prefix="merge-hold-review-") as directory:
    fixture = Path(directory)
    gh = fixture / "gh"
    gh.write_text('#!/bin/sh\nprintf "%s\\n" "$REVIEW_DECISION"\nexit "$API_EXIT"\n')
    gh.chmod(0o755)
    failures = []
    for name, api_exit, decision, should_pass in review_cases:
        env = {**os.environ, "PATH": f"{fixture}:{os.environ['PATH']}",
               "GH_TOKEN": "offline-test", "REPO": "fixture/repo", "PR_NUMBER": "1",
               "API_EXIT": str(api_exit), "REVIEW_DECISION": decision}
        result = subprocess.run(["bash", "-c", review_step], env=env, text=True,
                                capture_output=True, timeout=10)
        actual_pass = result.returncode == 0
        if actual_pass != should_pass:
            failures.append(name)
            print(f"FAIL {name}: exit={result.returncode}\n{result.stdout}{result.stderr}")
        else:
            print(f"PASS {name}")
    if failures:
        raise SystemExit(f"{len(failures)} reviewDecision regression(s): {failures}")
print(f"All {len(review_cases)} reviewDecision regressions passed")

# --- SBAI-8392/8585: the triggers that make the gate reflect live state ----------
for required_trigger in ("opened", "reopened", "synchronize", "labeled",
                         "unlabeled", "ready_for_review"):
    assert required_trigger in workflow.split("pull_request_review:", 1)[0], (
        f"pull_request trigger type '{required_trigger}' was dropped (SBAI-8392)")
assert "pull_request_review:" in workflow, "pull_request_review trigger dropped (SBAI-8585)"
print("PASS trigger set intact (6 pull_request types + pull_request_review)")

# --- SBAI-10544: duplicate same-SHA events must not cancel the required check ----
# Ported from studiobrain-cloud SBAI-10538 (cloud PR #1860); core carried the
# identical concurrency block. Evidence this encodes (gathered on cloud
# 2026-09-12 with `gh api`; core had not yet recorded its own incident):
#   cloud PR #1854, head 16a66c43: ONE timeline event (labeled: manual-merge,
#     23:51:25Z) produced TWO pull_request runs at the same SHA in the same
#     second (34659604093, 34659604221). cancel-in-progress killed the first.
#     The PR still reports mergeStateStatus=BLOCKED, mergeable=MERGEABLE, with
#     no hold label -- because the rollup carries a CANCELLED hold-label-gate
#     context alongside a LATER SUCCESS one. A cancelled required context is
#     not "superseded" by a newer successful sibling.
#   cloud PR #1858, head 1a550bd: force-push + ready_for_review (07:36:11Z) and
#     unlabeled review-hold (07:36:12Z) produced THREE runs at that one SHA
#     (34681164247/279/4409); two ended non-success with zero jobs and needed
#     manual re-runs (attempts 2 and 3) before the PR could merge at 08:22:32Z.
# Both incidents are duplicate/simultaneous events at the IDENTICAL head SHA,
# so no group key derived from the event payload (number, sha, action, event
# name) separates them. The gate must simply never be cancelled: it is a
# one-minute job whose check run is bound to the SHA it ran for, so a run left
# alive on a superseded SHA cannot gate the new head.
CONCURRENCY_EXPR = re.compile(r"\$\{\{\s*([A-Za-z0-9_.\-]+)\s*\}\}")


def parse_concurrency(text):
    """Return the workflow's top-level concurrency mapping, or None if absent."""
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if not line.startswith("concurrency:"):
            continue
        block = {}
        for follow in lines[index + 1:]:
            if follow and not follow[0].isspace():
                break
            stripped = follow.strip()
            if not stripped or stripped.startswith("#"):
                continue
            key, _, value = stripped.partition(":")
            block[key.strip()] = value.strip()
        return block
    return None


def replay(concurrency, events):
    """Apply GitHub's documented concurrency semantics to a run sequence.

    cancel-in-progress: true  -> a new run cancels in-progress AND pending runs
                                 in its group.
    cancel-in-progress: false -> a new run queues behind an in-progress run,
                                 and cancels any run already pending in the
                                 group (only one run may be pending per group).
    """
    runs = []
    for number, event in enumerate(events, start=1):
        context = {
            "github.event.pull_request.number": event["pr"],
            "github.event.pull_request.head.sha": event["sha"],
            "github.event.action": event.get("action", ""),
            "github.event_name": event.get("event_name", "pull_request"),
            "github.run_id": number,
            "github.workflow": "Merge Hold Gate",
            "github.ref": f"refs/pull/{event['pr']}/merge",
        }
        run = {"id": number, "sha": event["sha"], "group": None, "state": "running"}
        group = None
        if concurrency and concurrency.get("group"):
            group = CONCURRENCY_EXPR.sub(
                lambda m: str(context.get(m.group(1), "")), concurrency["group"])
        run["group"] = group
        if group is not None:
            cancels = str(concurrency.get("cancel-in-progress", "false")).lower() == "true"
            for other in runs:
                if other["group"] != group:
                    continue
                if cancels and other["state"] in ("running", "pending"):
                    other["state"] = "cancelled"
                elif not cancels and other["state"] == "pending":
                    other["state"] = "cancelled"
            if not cancels and any(o["group"] == group and o["state"] == "running"
                                   for o in runs):
                run["state"] = "pending"
        runs.append(run)
    return runs


def contexts_at(runs, sha):
    """Check-run conclusions posted against `sha`; a run only reports on its own SHA."""
    return [("cancelled" if r["state"] == "cancelled" else "success")
            for r in runs if r["sha"] == sha]


HEAD = "16a66c43b12e6fc1bd317e2da6f5b0bd523fa660"
OLD = "a87a2fb647c307c34d408a9a7b1caab1a50366a9"
# PR #1854: the same `labeled` action delivered twice, one second, one SHA.
PR_1854 = [{"pr": 1854, "sha": HEAD, "action": "labeled"},
           {"pr": 1854, "sha": HEAD, "action": "labeled"}]
# PR #1858: three distinct actions, one second, one SHA.
PR_1858 = [{"pr": 1858, "sha": HEAD, "action": "synchronize"},
           {"pr": 1858, "sha": HEAD, "action": "ready_for_review"},
           {"pr": 1858, "sha": HEAD, "action": "unlabeled"}]
# A genuinely superseded SHA: two events on the old head, then a new push.
SUPERSEDED = [{"pr": 1854, "sha": OLD, "action": "synchronize"},
              {"pr": 1854, "sha": OLD, "action": "labeled"},
              {"pr": 1854, "sha": HEAD, "action": "synchronize"}]

live = parse_concurrency(workflow)
concurrency_failures = []


def expect(name, condition, detail=""):
    if condition:
        print(f"PASS {name}")
    else:
        concurrency_failures.append(name)
        print(f"FAIL {name}: {detail}")


for label, events in (("PR #1854 duplicate delivery", PR_1854),
                      ("PR #1858 three same-SHA actions", PR_1858)):
    at_head = contexts_at(replay(live, events), HEAD)
    expect(f"{label}: no cancelled required check at head",
           "cancelled" not in at_head, f"contexts at head: {at_head}")
    expect(f"{label}: every duplicate reports success",
           at_head == ["success"] * len(events), f"contexts at head: {at_head}")

superseded_runs = replay(live, SUPERSEDED)
expect("new push: head SHA carries exactly one successful context",
       contexts_at(superseded_runs, HEAD) == ["success"],
       f"contexts at head: {contexts_at(superseded_runs, HEAD)}")
expect("new push: superseded-SHA runs post no context on the new head",
       all(r["sha"] == HEAD for r in superseded_runs if r["sha"] == HEAD)
       and len([r for r in superseded_runs if r["sha"] == HEAD]) == 1,
       "a superseded run leaked a context onto the new head")

# Counter-examples: the shapes that DO strand a cancelled required check. These
# keep the rejected fixes from being reintroduced as "simplifications".
rejected = [
    ("number-only group (the SBAI-10544 bug)",
     {"group": "merge-hold-gate-${{ github.event.pull_request.number }}",
      "cancel-in-progress": "true"}),
    ("number+sha group with cancel-in-progress (insufficient)",
     {"group": "merge-hold-gate-${{ github.event.pull_request.number }}"
               "-${{ github.event.pull_request.head.sha }}",
      "cancel-in-progress": "true"}),
]
for name, config in rejected:
    for label, events in (("#1854", PR_1854), ("#1858", PR_1858)):
        at_head = contexts_at(replay(config, events), HEAD)
        expect(f"rejected shape strands a cancelled check ({name}, {label})",
               "cancelled" in at_head, f"contexts at head: {at_head}")

# cancel-in-progress: false still cancels a run that is merely PENDING, so it
# only survives two duplicates -- #1858's three events strand one.
queued = {"group": "merge-hold-gate-${{ github.event.pull_request.number }}"
                   "-${{ github.event.pull_request.head.sha }}",
          "cancel-in-progress": "false"}
expect("rejected shape strands a cancelled check (sha group + queueing, #1858)",
       "cancelled" in contexts_at(replay(queued, PR_1858), HEAD),
       f"contexts at head: {contexts_at(replay(queued, PR_1858), HEAD)}")

if concurrency_failures:
    raise SystemExit(
        f"{len(concurrency_failures)} concurrency regression(s): {concurrency_failures}")
print("All SBAI-10544 concurrency regressions passed")
