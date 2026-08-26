#!/usr/bin/env python3
"""Install a curated catalog provider into a project's own override
directory, and read it back (SBAI-8093, epic SBAI-8007).

This is the templates-repo half of the curated provider marketplace. The
cloud repo (SBAI-8091, PR #1215) owns the live Durable Object write/merge
path for a project's provider catalog (``project_yaml_files``) and enforces
admin/member policy server-side; this script proves the artifact contract
those writes rely on, entirely within the templates repo:

  1. A curated provider only reaches ``templates/Providers/`` via a reviewed
     GitHub PR (branch protection) that the ``validate`` CI job schema-checks
     with ``scripts/validate.py`` (schemas/provider.json). That job never
     receives R2 or admin credentials -- see
     ``scripts/check_workflow_secret_isolation.py`` -- so nothing can reach
     the published catalog or a project's own store without passing through
     that reviewed, schema-gated path.
  2. Once merged, ``scripts/build_catalog_index.py`` deterministically
     regenerates ``catalog-index.json`` and it is published to R2
     (``scripts/publish_catalog_index_to_r2.py``, push-to-main only).
  3. A project adopts a catalog provider by copying the *exact* reviewed
     YAML into its own drop-in override directory
     (``_Providers/<id>.provider.yaml`` -- see schemas/README.md), which
     ``schemas/provider.json`` governs identically for both the shared
     catalog and a project override. ``install_provider`` performs that copy
     but -- like cloud's ``validateProviderYaml`` gate (SBAI-8091) -- refuses
     to write anything that fails schema validation. There is no bypass: a
     submission that was never reviewed/approved (and therefore never
     schema-clean) cannot be installed, and therefore can never be read back.

Usage:
    python3 scripts/install_provider.py <source.provider.yaml> <project_dir>
    python3 scripts/install_provider.py --read-back <project_dir> <provider_id>
"""
from __future__ import annotations

import argparse
import pathlib
import sys

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - covered by validate.py's own guard
    yaml = None  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402  (local import, path patched above)


class ProviderInstallRejected(RuntimeError):
    """Raised when a submission fails schemas/provider.json and cannot be
    installed -- the only gate, and it cannot be bypassed."""


def install_provider(source: pathlib.Path, project_dir: pathlib.Path) -> pathlib.Path:
    """Validate ``source`` against schemas/provider.json and, only if it
    passes, copy it into ``project_dir/_Providers/<id>.provider.yaml``.

    Returns the installed path. Raises ProviderInstallRejected -- and writes
    nothing -- if the submission does not validate.
    """
    if yaml is None:
        raise RuntimeError("pyyaml is required to install a provider file")

    text = source.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ProviderInstallRejected(f"{source}: YAML parse error: {exc}") from exc

    if not isinstance(data, dict):
        raise ProviderInstallRejected(f"{source}: top-level YAML is not a mapping")

    errors = validate._validate_instance(data, "provider.json", str(source))
    if errors:
        raise ProviderInstallRejected(
            f"{source}: rejected -- does not satisfy schemas/provider.json:\n"
            + "\n".join(f"  - {err}" for err in errors)
        )

    provider_id = str(data["id"])
    dest_dir = project_dir / "_Providers"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{provider_id}.provider.yaml"
    dest.write_text(text, encoding="utf-8")
    return dest


def read_back_provider(project_dir: pathlib.Path, provider_id: str) -> dict:
    """Load and re-validate an installed provider override. Raises
    FileNotFoundError if it was never installed (e.g. because it was
    rejected) and ProviderInstallRejected if the file on disk has since
    drifted out of schema compliance."""
    if yaml is None:
        raise RuntimeError("pyyaml is required to read back a provider file")

    path = project_dir / "_Providers" / f"{provider_id}.provider.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProviderInstallRejected(f"{path}: top-level YAML is not a mapping")

    errors = validate._validate_instance(data, "provider.json", str(path))
    if errors:
        raise ProviderInstallRejected(
            f"{path}: installed file no longer satisfies schemas/provider.json:\n"
            + "\n".join(f"  - {err}" for err in errors)
        )
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-back", action="store_true", help="Read back an installed provider instead of installing one.")
    parser.add_argument("a", help="source .provider.yaml (install) or project_dir (read-back)")
    parser.add_argument("b", help="project_dir (install) or provider_id (read-back)")
    args = parser.parse_args(argv)

    try:
        if args.read_back:
            data = read_back_provider(pathlib.Path(args.a), args.b)
            print(f"OK: read back provider {data['id']!r} ({data['kind']}, wire={data['wire']})")
        else:
            dest = install_provider(pathlib.Path(args.a), pathlib.Path(args.b))
            print(f"OK: installed {dest}")
    except (ProviderInstallRejected, FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
