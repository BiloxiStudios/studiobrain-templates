#!/usr/bin/env python3
"""Build catalog-index.json -- the flat badge index the marketplace lanes
consume (SBAI-7611, epic SBAI-7608).

Scans the catalog drop-in locations:

  templates/Providers/*.provider.yaml   -> kind "provider"
  templates/Standard/*.ability.yaml     -> kind "ability"
  templates/Workflows/*.workflow.yaml   -> kind "canvas" (one-release alias)
  templates/Canvas/*.canvas.yaml        -> kind "canvas" (canonical, SBAI-7650)

and emits catalog-index.json at the repo root:

  {"index_schema_version": 1, "generated_at": ..., "entries": [...]}

Each entry carries badges only -- id, kind, name/display, description, path,
plus per-kind badge metadata (providers: wire/runtime/provides/requires/
billing/slots/pricing; canvas entries: requires/slots/domains/entity_types/
step_count; abilities: provider). Full file bodies stay in the YAML; the
index stays small. wire/runtime badge the marketplace on execution mode,
e.g. "on-device" for wire: in-app.

A provider's ``pricing`` badge is the typed ``{currency, unit, amount}``
operand from ``pricing.operand`` (SBAI-7675) -- present only when the source
YAML declares one; absent means the marketplace does not know the price and
must render "unknown", never "$0". A canvas's ``step_count`` is always the
literal length of its parsed ``steps`` list, so ``approx_cost = pricing.amount
* step_count`` is honest for a per-step-priced provider and undefined
(not zero) otherwise.

Entries are sorted by (kind, id) so diffs are stable. ``generated_at`` is
deterministic: pass --generated-at (CI passes the commit's author timestamp,
the same derivation the catalog-index CI job uses), otherwise it falls back to
HEAD's commit timestamp, then wall clock.

Usage:
    python3 scripts/build_catalog_index.py
    python3 scripts/build_catalog_index.py --generated-at 2026-08-21T00:00:00Z
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
DEFAULT_OUT = ROOT / "catalog-index.json"
INDEX_SCHEMA_VERSION = 1


def _scan(root: pathlib.Path) -> list[tuple[str, pathlib.Path, tuple[str, ...]]]:
    """(kind, directory, glob patterns) rooted under ``root``, not the module's
    own ROOT -- so callers (tests included) can point the scan at a synthetic
    tree via ``build_entries(root=...)`` without touching the real catalog.
    Canvas/*.canvas.yaml is the SBAI-7651 rename target for
    Workflows/*.workflow.yaml -- both are accepted so the index does not
    break across the rename.
    """
    templates_dir = root / "templates"
    return [
        ("provider", templates_dir / "Providers", ("*.provider.yaml", "*.provider.yml")),
        ("ability", templates_dir / "Standard", ("*.ability.yaml", "*.ability.yml")),
        ("canvas", templates_dir / "Workflows", ("*.workflow.yaml", "*.workflow.yml")),
        ("canvas", templates_dir / "Canvas", ("*.canvas.yaml", "*.canvas.yml")),
    ]


def iter_catalog_files(root: pathlib.Path = ROOT) -> Iterable[tuple[str, pathlib.Path]]:
    """Yield (kind, path) for every catalog file, in deterministic order."""
    for kind, directory, patterns in _scan(root):
        if not directory.exists():
            continue
        for pattern in patterns:
            for path in sorted(directory.rglob(pattern)):
                yield kind, path


def _compact_canvas_slots(slots: Any) -> dict[str, Any]:
    """Reduce workflow slots to badge data: modality + optional flag.

    Slot refs/outs are file-body wiring, not badges -- the marketplace only
    needs to show what goes in and out.
    """
    compact: dict[str, Any] = {}
    if not isinstance(slots, dict):
        return compact
    for name in sorted(slots):
        slot = slots[name]
        if not isinstance(slot, dict):
            continue
        badge: dict[str, Any] = {}
        if slot.get("modality"):
            badge["modality"] = slot["modality"]
        if slot.get("optional"):
            badge["optional"] = True
        compact[str(name)] = badge
    return compact


def _compact_requires(requires: Any) -> dict[str, Any]:
    """Keep only the requires badges the marketplace shows.

    platforms + env, plus ``webgpu`` for wire: in-app providers -- it is a
    hard runnability gate (``required`` means a device without WebGPU cannot
    run the provider at all), so dropping it would make such a provider look
    universally installable in the index.
    """
    compact: dict[str, Any] = {}
    if not isinstance(requires, dict):
        return compact
    if requires.get("platforms"):
        compact["platforms"] = list(requires["platforms"])
    if requires.get("webgpu"):
        compact["webgpu"] = str(requires["webgpu"])
    if requires.get("env"):
        compact["env"] = list(requires["env"])
    return compact


def _compact_pricing_operand(pricing: Any) -> dict[str, Any] | None:
    """Typed price operand badge, or None if pricing is unknown (SBAI-7675).

    Only ``pricing.operand`` -- currency + unit + amount, schema-enforced in
    schemas/provider.json -- is a badge-able, provider-neutral price. The
    unstructured ``table`` / ``endpoint`` fields have no consumer contract and
    stay out of the index. A provider with no operand, or an operand missing
    any of the three fields, gets no ``pricing`` key at all: absence is how
    the index spells "unknown", so a consumer can never mistake it for free
    (amount 0 is not a legal spelling of unknown -- the schema forbids it).
    """
    if not isinstance(pricing, dict):
        return None
    operand = pricing.get("operand")
    if not isinstance(operand, dict):
        return None
    currency, unit, amount = operand.get("currency"), operand.get("unit"), operand.get("amount")
    if not currency or not unit or not isinstance(amount, (int, float)):
        return None
    return {"currency": str(currency), "unit": str(unit), "amount": amount}


def build_entries(root: pathlib.Path = ROOT) -> list[dict[str, Any]]:
    """Parse every catalog file and return the sorted entry list."""
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for kind, path in iter_catalog_files(root):
        if yaml is None:
            raise RuntimeError("pyyaml is required to build the catalog index")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise RuntimeError(f"{path}: YAML parse error: {exc}") from exc
        if not isinstance(data, dict):
            raise RuntimeError(f"{path}: top-level YAML is not a mapping")
        if not data.get("id"):
            raise RuntimeError(f"{path}: missing required 'id'")
        entry_id = str(data["id"])
        if (kind, entry_id) in seen:
            raise RuntimeError(f"{path}: duplicate (kind={kind!r}, id={entry_id!r})")
        seen.add((kind, entry_id))

        entry: dict[str, Any] = {"id": entry_id, "kind": kind}
        name = data.get("name") or data.get("display")
        if name:
            entry["name"] = str(name)
        if data.get("description"):
            entry["description"] = str(data["description"])
        entry["path"] = path.relative_to(root).as_posix()

        requires = _compact_requires(data.get("requires"))
        if requires:
            entry["requires"] = requires

        if kind == "provider":
            if data.get("wire"):
                entry["wire"] = str(data["wire"])
            if data.get("route"):
                entry["route"] = str(data["route"])
            if "starter" in data:
                entry["starter"] = bool(data["starter"])
            if data.get("runtime"):
                entry["runtime"] = str(data["runtime"])
            if data.get("provides"):
                entry["provides"] = list(data["provides"])
            if data.get("billing"):
                entry["billing"] = list(data["billing"])
            if data.get("slots"):
                entry["slots"] = data["slots"]
            operand = _compact_pricing_operand(data.get("pricing"))
            if operand:
                entry["pricing"] = operand
        elif kind == "canvas":
            slots = _compact_canvas_slots(data.get("slots"))
            if slots:
                entry["slots"] = slots
            if data.get("domains"):
                entry["domains"] = list(data["domains"])
            if data.get("entity_types"):
                entry["entity_types"] = list(data["entity_types"])
            steps = data.get("steps")
            if isinstance(steps, list):
                # Deterministic: the literal length of the parsed steps list --
                # never a hand-authored field, so it can't drift from the
                # actual graph the way a manually maintained count would.
                entry["step_count"] = len(steps)
        elif kind == "ability":
            if data.get("provider"):
                entry["provider"] = str(data["provider"])

        entries.append(entry)

    entries.sort(key=lambda e: (e["kind"], e["id"]))
    return entries


def default_generated_at(root: pathlib.Path = ROOT) -> str:
    """HEAD commit timestamp (deterministic per commit), else wall clock."""
    try:
        out = subprocess.run(
            ["git", "show", "-s", "--format=%cI", "HEAD"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        stamp = datetime.fromisoformat(out)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        stamp = datetime.now(timezone.utc)
    return stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_index(generated_at: str, root: pathlib.Path = ROOT) -> dict[str, Any]:
    return {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "generated_at": generated_at,
        "entries": build_entries(root),
    }


def render(index: dict[str, Any]) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build catalog-index.json (marketplace badge index).")
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output path (default: catalog-index.json at the repo root).",
    )
    parser.add_argument(
        "--generated-at",
        help="ISO-8601 UTC timestamp for generated_at. Default: HEAD commit "
             "timestamp (deterministic per commit), falling back to wall clock.",
    )
    args = parser.parse_args(argv)

    generated_at = args.generated_at or default_generated_at()
    index = build_index(generated_at)
    out = pathlib.Path(args.out)
    # newline="\n" keeps the committed artifact byte-identical across platforms.
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(index))

    counts: dict[str, int] = {}
    for entry in index["entries"]:
        counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1
    summary = ", ".join(f"{n} {k}" for k, n in sorted(counts.items()))
    print(f"wrote {out}: {len(index['entries'])} entries ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
