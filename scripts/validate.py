#!/usr/bin/env python3
"""StudioBrain templates -- schema + compat validator.

Runs every CI-facing check from one place:

  1. Confirms every schema file in ``schemas/`` is a valid JSON Schema (Draft 2020-12).
  2. Validates every ``*.layout.json`` against ``schemas/layout.json``.
  3. Validates every ``pack.json`` against ``schemas/pack.json``.
  4. Validates every ``plugin.json`` against ``schemas/plugin.json``.
  5. Validates every skill YAML frontmatter against ``schemas/skill.yaml.json``.
  6. Validates ``*.provider.yaml`` / ``*.ability.yaml`` / ``*.canvas.yaml``
     (and leftover ``*.workflow.yaml``) against ``schemas/provider.json``,
     ``schemas/ability.json``, and ``schemas/canvas.json`` (SBAI-7569 / SBAI-7651).
  7. Validates entity markdown YAML frontmatter against ``schemas/<entity_type>.json``
     (best-effort -- skipped if pyyaml is unavailable).
  8. Enforces compat metadata: every layout / pack / plugin / skill MUST declare
     ``compat.min_core_version`` as a semver string. When ``--core-version`` is
     supplied, the script also refuses assets whose ``min_core_version`` is
     newer than the running core.
  9. Enforces ``requires`` metadata on providers / canvases: ``wire: process``
     and localhost providers must declare ``platforms: [desktop]``; canvases
     must cover the platforms (error) and env / models (warning) of every
     provider their steps use.

Intended for both local development and CI:

    python3 scripts/validate.py                  # full validation pass
    python3 scripts/validate.py --core-version 0.5.0
    python3 scripts/validate.py --no-entity-yaml # skip entity frontmatter checks

Exit code is non-zero if any validation fails.

This script deliberately has zero runtime dependencies beyond the Python
standard library when ``--no-entity-yaml`` is set, so it can run in a
minimal CI image. When ``jsonschema`` and ``pyyaml`` are available they
are used; otherwise checks depending on them degrade gracefully.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import pathlib
from typing import Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"
TEMPLATES_DIR = ROOT / "templates"
PLUGINS_DIR = ROOT / "plugins"
SKILLS_DIR = ROOT / "skills"

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(msg)


def _parse_semver(value: str) -> tuple[int, int, int]:
    """Parse a semver string into a (major, minor, patch) tuple for ordering.

    Pre-release/build metadata are stripped -- compat ordering is purely on the
    release triple.
    """
    match = SEMVER_RE.match(value)
    if not match:
        raise ValueError(f"not a semver string: {value!r}")
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _semver_le(a: str, b: str) -> bool:
    """Return True if ``a <= b`` in semver ordering (pre-release stripped)."""
    return _parse_semver(a) <= _parse_semver(b)


# ----- Optional-dependency shims -------------------------------------------------

try:
    import yaml  # type: ignore
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

try:
    from jsonschema import Draft202012Validator  # type: ignore
    HAVE_JSONSCHEMA = True
    # RefResolver is deprecated in jsonschema >= 4.18 in favor of the `referencing`
    # library. We only need it as a fallback for very old jsonschema versions, so
    # import it lazily and silence the deprecation warning.
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", DeprecationWarning)
        try:
            from jsonschema import RefResolver  # type: ignore  # noqa: F401
        except ImportError:  # pragma: no cover
            RefResolver = None  # type: ignore
except ImportError:
    HAVE_JSONSCHEMA = False


# ----- Schema loading ------------------------------------------------------------

_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


def load_schema(name: str) -> dict[str, Any]:
    """Load a schema by file name (e.g. 'layout.json') from schemas/."""
    if name not in _SCHEMA_CACHE:
        path = SCHEMAS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"schema not found: {path}")
        with path.open(encoding="utf-8") as fh:
            _SCHEMA_CACHE[name] = json.load(fh)
    return _SCHEMA_CACHE[name]


def make_validator(schema_name: str):
    """Build a Draft202012Validator with local $ref resolution."""
    schema = load_schema(schema_name)
    if HAVE_JSONSCHEMA:
        # Newer jsonschema versions deprecate RefResolver but still ship it.
        # We use a referencing-based registry when available, falling back to
        # RefResolver for older versions.
        try:
            from referencing import Registry, Resource  # type: ignore
            resources = []
            for schema_file in SCHEMAS_DIR.glob("*.json"):
                try:
                    data = json.loads(schema_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                # Resource key is the $id URL.
                rid = data.get("$id") or schema_file.name
                resources.append((rid, Resource.from_contents(data)))
            registry = Registry().with_resources(resources)
            return Draft202012Validator(schema, registry=registry)
        except ImportError:
            if RefResolver is not None:
                base_uri = schema.get("$id", "")
                resolver = RefResolver(base_uri=base_uri, referrer=schema)
                return Draft202012Validator(schema, resolver=resolver)
            return Draft202012Validator(schema)
    return None


# ----- Check helpers -------------------------------------------------------------

def check_schemas_are_valid() -> list[str]:
    """Ensure every file in schemas/ is itself a valid JSON Schema."""
    errors: list[str] = []
    for schema_file in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            schema = json.loads(schema_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{schema_file}: JSON parse error: {exc}")
            continue
        if HAVE_JSONSCHEMA:
            try:
                Draft202012Validator.check_schema(schema)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{schema_file}: invalid JSON Schema: {exc}")
        else:
            # Without jsonschema we can still confirm shape basics.
            if not isinstance(schema, dict):
                errors.append(f"{schema_file}: schema is not an object")
            elif "$schema" not in schema:
                errors.append(f"{schema_file}: missing $schema keyword")
    return errors


def _validate_instance(instance: Any, schema_name: str, label: str) -> list[str]:
    if not HAVE_JSONSCHEMA:
        return []  # graceful skip
    validator = make_validator(schema_name)
    if validator is None:
        return []
    errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    return [
        f"{label}: {err.message} (at /{'/'.join(str(p) for p in err.path) or '<root>'})"
        for err in errs
    ]


def check_layouts() -> list[str]:
    errors: list[str] = []
    layout_dir = TEMPLATES_DIR / "Layouts"
    if not layout_dir.exists():
        return errors
    for layout_file in sorted(layout_dir.glob("*.layout.json")):
        try:
            data = json.loads(layout_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{layout_file}: JSON parse error: {exc}")
            continue
        errors.extend(_validate_instance(data, "layout.json", str(layout_file)))
    return errors


def check_packs() -> list[str]:
    errors: list[str] = []
    packs_dir = TEMPLATES_DIR / "Packs"
    if not packs_dir.exists():
        return errors
    for pack_file in sorted(packs_dir.glob("*/pack.json")):
        try:
            data = json.loads(pack_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{pack_file}: JSON parse error: {exc}")
            continue
        errors.extend(_validate_instance(data, "pack.json", str(pack_file)))
    return errors


def check_plugins() -> list[str]:
    errors: list[str] = []
    for manifest in sorted(PLUGINS_DIR.glob("*/plugin.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{manifest}: JSON parse error: {exc}")
            continue
        errors.extend(_validate_instance(data, "plugin.json", str(manifest)))
    return errors


def check_skills() -> list[str]:
    errors: list[str] = []
    if not HAVE_YAML:
        _info("NOTE: pyyaml not installed -- skipping skill YAML frontmatter validation.")
        return errors
    for skill_dir in [SKILLS_DIR / "Standard", SKILLS_DIR / "User"]:
        if not skill_dir.exists():
            continue
        for skill_file in sorted(skill_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(skill_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"{skill_file}: YAML parse error: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{skill_file}: top-level YAML is not a mapping")
                continue
            errors.extend(_validate_instance(data, "skill.yaml.json", str(skill_file)))
    return errors


def check_providers_and_abilities() -> list[str]:
    """Validate drop-in generation files (SBAI-7569)."""
    errors: list[str] = []
    if not HAVE_YAML:
        _info("NOTE: pyyaml not installed -- skipping provider/ability YAML validation.")
        return errors
    search_roots = [TEMPLATES_DIR, ROOT / "Providers", ROOT / "Abilities"]
    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.provider.yaml")) + sorted(root.rglob("*.provider.yml")):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"{path}: YAML parse error: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{path}: top-level YAML is not a mapping")
                continue
            errors.extend(_validate_instance(data, "provider.json", str(path)))
        for path in sorted(root.rglob("*.ability.yaml")) + sorted(root.rglob("*.ability.yml")):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"{path}: YAML parse error: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{path}: top-level YAML is not a mapping")
                continue
            errors.extend(_validate_instance(data, "ability.json", str(path)))
        canvas_paths = (
            sorted(root.rglob("*.canvas.yaml"))
            + sorted(root.rglob("*.canvas.yml"))
            + sorted(root.rglob("*.workflow.yaml"))
            + sorted(root.rglob("*.workflow.yml"))
        )
        for path in canvas_paths:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"{path}: YAML parse error: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{path}: top-level YAML is not a mapping")
                continue
            errors.extend(_validate_instance(data, "canvas.json", str(path)))
    return errors


def check_entity_frontmatter() -> list[str]:
    if not HAVE_YAML or not HAVE_JSONSCHEMA:
        _info("NOTE: pyyaml or jsonschema not installed -- skipping entity YAML frontmatter validation.")
        return []
    errors: list[str] = []
    skip_files = {"README.md"}
    # Template / example files use placeholder values ([snake_case_name], YYYY-MM-DD)
    # by design -- they are not real entity instances and must not be schema-validated.
    skip_suffixes = ("_TEMPLATE.md",)
    skip_path_parts = {"templates", "examples"}
    for md in sorted(TEMPLATES_DIR.rglob("*.md")):
        if md.name in skip_files:
            continue
        if any(md.name.endswith(suffix) for suffix in skip_suffixes):
            continue
        # Skip files inside a pack's templates/ or examples/ directory.
        if skip_path_parts & set(md.parts):
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"{md}: missing YAML frontmatter delimiter")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{md}: malformed frontmatter (no closing ---)")
            continue
        try:
            data = yaml.safe_load(parts[1])
        except yaml.YAMLError as exc:
            errors.append(f"{md}: YAML parse error: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{md}: frontmatter is not a YAML mapping")
            continue
        entity_type = data.get("entity_type")
        if not entity_type:
            continue
        schema_file = SCHEMAS_DIR / f"{entity_type}.json"
        if not schema_file.exists():
            errors.append(f"{md}: no schema for entity_type={entity_type!r}")
            continue
        errors.extend(_validate_instance(data, f"{entity_type}.json", str(md)))
    return errors


# ----- Requires enforcement ------------------------------------------------------

_LOCALHOST_RE = re.compile(r"^(https?://)?(localhost|127\.0\.0\.1|\[?::1\]?)([:/]|$)")

# Known capability tags for provider `provides` (SBAI-7610). Consumed by
# capability matching + marketplace filtering; unknown tags only WARN so new
# capabilities can ship ahead of the validator.
_KNOWN_PROVIDES = {
    "llm-chat", "tts", "voice-clone", "image-gen", "video-gen",
    "music-gen", "3d-gen", "3d-render", "audio-stems", "media-convert",
    "embeddings",
}


def check_requires() -> tuple[list[str], list[str]]:
    """Enforce ``requires`` metadata on providers and workflows (SBAI-7569).

    Returns (errors, warnings):
    - ERROR: a ``wire: process`` provider must declare requires.platforms
      containing ``desktop``.
    - ERROR: a provider with a localhost base_url must declare
      requires.platforms containing ``desktop`` (cloud workers cannot run it).
    - WARN (migration period): ``auth.env`` not mirrored in ``requires.env``.
    - WARN: ``billing: [brainbits]`` without ``auth.env`` (nothing to meter
      against), and unknown ``provides`` capability tags (SBAI-7610).
    - ERROR: a workflow step that uses a desktop-only provider forces the
      workflow to declare requires.platforms containing ``desktop``;
      WARN on uncovered env / models.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not HAVE_YAML:
        return errors, warnings

    providers: dict[str, tuple[pathlib.Path, dict[str, Any]]] = {}
    workflows: list[tuple[pathlib.Path, dict[str, Any]]] = []
    search_roots = [TEMPLATES_DIR, ROOT / "Providers", ROOT / "Abilities"]
    for root in search_roots:
        if not root.exists():
            continue
        for pattern, sink in (
            ("*.provider.yaml", "provider"),
            ("*.canvas.yaml", "canvas"),
            ("*.workflow.yaml", "canvas"),
        ):
            for path in sorted(root.rglob(pattern)):
                try:
                    data = yaml.safe_load(path.read_text(encoding="utf-8"))
                except yaml.YAMLError:
                    continue  # parse errors are reported by check_providers_and_abilities
                if not isinstance(data, dict):
                    continue
                if sink == "provider":
                    if data.get("id"):
                        providers[str(data["id"])] = (path, data)
                else:
                    workflows.append((path, data))

    for pid, (path, data) in sorted(providers.items()):
        requires = data.get("requires") or {}
        platforms = requires.get("platforms") or []
        env = requires.get("env") or []
        if data.get("wire") == "process" and "desktop" not in platforms:
            errors.append(
                f"{path}: provider '{pid}' has wire 'process' -- "
                "requires.platforms must contain 'desktop'"
            )
        base_url = str(data.get("base_url") or "")
        if _LOCALHOST_RE.match(base_url) and "desktop" not in platforms:
            errors.append(
                f"{path}: provider '{pid}' has a localhost base_url -- "
                "requires.platforms must contain 'desktop'"
            )
        auth = data.get("auth") or {}
        auth_env = auth.get("env")
        if auth_env and auth_env not in env:
            warnings.append(
                f"{path}: provider '{pid}' auth.env={auth_env!r} is not listed in requires.env"
            )
        billing = data.get("billing") or []
        if "brainbits" in billing and not auth_env:
            warnings.append(
                f"{path}: provider '{pid}' declares billing 'brainbits' but has no "
                "auth.env -- nothing to meter against"
            )
        for tag in data.get("provides") or []:
            if tag not in _KNOWN_PROVIDES:
                warnings.append(
                    f"{path}: provider '{pid}' has unknown provides tag {tag!r} "
                    f"(known: {', '.join(sorted(_KNOWN_PROVIDES))})"
                )

    for path, data in workflows:
        requires = data.get("requires") or {}
        platforms = requires.get("platforms") or []
        env = requires.get("env") or []
        models = requires.get("models") or []
        wid = data.get("id", path.name)
        seen: set[str] = set()
        for step in data.get("steps") or []:
            if not isinstance(step, dict):
                continue
            pid = step.get("provider")
            if not pid or pid not in providers:
                continue
            preq = providers[pid][1].get("requires") or {}
            if "desktop" in (preq.get("platforms") or []) and "desktop" not in platforms:
                errors.append(
                    f"{path}: workflow '{wid}' step '{step.get('id')}' uses desktop-only "
                    f"provider '{pid}' -- requires.platforms must contain 'desktop'"
                )
            for need in preq.get("env") or []:
                if need not in env and ("env", need) not in seen:
                    seen.add(("env", need))
                    warnings.append(
                        f"{path}: workflow '{wid}' uses provider '{pid}' requiring env "
                        f"{need!r} -- not listed in requires.env"
                    )
            for need in preq.get("models") or []:
                if need not in models and ("models", need) not in seen:
                    seen.add(("models", need))
                    warnings.append(
                        f"{path}: workflow '{wid}' uses provider '{pid}' requiring model "
                        f"{need!r} -- not listed in requires.models"
                    )
    return errors, warnings


# ----- Compat enforcement --------------------------------------------------------

def _walk_compat_objects() -> Iterable[tuple[pathlib.Path, dict[str, Any], str]]:
    """Yield (path, parsed_dict, kind) for every asset that should carry compat metadata."""
    layout_dir = TEMPLATES_DIR / "Layouts"
    if layout_dir.exists():
        for f in layout_dir.glob("*.layout.json"):
            try:
                yield f, json.loads(f.read_text(encoding="utf-8")), "layout"
            except json.JSONDecodeError:
                continue
    packs_dir = TEMPLATES_DIR / "Packs"
    if packs_dir.exists():
        for f in packs_dir.glob("*/pack.json"):
            try:
                yield f, json.loads(f.read_text(encoding="utf-8")), "pack"
            except json.JSONDecodeError:
                continue
    for f in PLUGINS_DIR.glob("*/plugin.json"):
        try:
            yield f, json.loads(f.read_text(encoding="utf-8")), "plugin"
        except json.JSONDecodeError:
            continue
    if HAVE_YAML:
        for skill_dir in [SKILLS_DIR / "Standard", SKILLS_DIR / "User"]:
            if not skill_dir.exists():
                continue
            for f in skill_dir.glob("*.yaml"):
                try:
                    data = yaml.safe_load(f.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        yield f, data, "skill"
                except yaml.YAMLError:
                    continue


def check_compat(core_version: str | None) -> list[str]:
    """Enforce compat.min_core_version semantics across all relevant assets.

    - Every layout / pack / plugin / skill must declare ``compat.min_core_version``
      as a valid semver string. (Existing files added before this ticket are
      grandfathered via ``--allow-missing-compat``; default is strict.)
    - When ``core_version`` is provided, refuse any asset whose
      ``min_core_version`` is newer than the running core.
    """
    errors: list[str] = []
    for path, data, kind in _walk_compat_objects():
        compat = data.get("compat")
        if not isinstance(compat, dict):
            errors.append(
                f"{path}: missing 'compat' object (expected compat.min_core_version for {kind})"
            )
            continue
        min_core = compat.get("min_core_version")
        if not min_core:
            errors.append(f"{path}: compat.min_core_version missing")
            continue
        if not SEMVER_RE.match(str(min_core)):
            errors.append(
                f"{path}: compat.min_core_version={min_core!r} is not a valid semver string"
            )
            continue
        if core_version is not None:
            try:
                running = _parse_semver(core_version)
            except ValueError:
                errors.append(
                    f"--core-version={core_version!r} is not a valid semver string"
                )
                return errors
            if not _semver_le(str(min_core), core_version):
                errors.append(
                    f"{path}: requires core >={min_core} but running core is "
                    f"{running[0]}.{running[1]}.{running[2]}"
                )
        max_core = compat.get("max_core_version")
        if max_core and not SEMVER_RE.match(str(max_core)):
            errors.append(
                f"{path}: compat.max_core_version={max_core!r} is not a valid semver string"
            )
    return errors


# ----- Fixture validation --------------------------------------------------------

FIXTURES_DIR = SCHEMAS_DIR / "fixtures"


def check_fixtures() -> list[str]:
    """Validate fixture files against their schemas.

    Expects fixtures in schemas/fixtures/:
    - valid_v2_*.json -- should pass validation
    - invalid_v2_*.json -- should fail validation (we confirm errors are raised)
    - valid_v1_*.json -- legacy v1 manifests that should pass
    - invalid_v1_*.json -- legacy v1 manifests that should fail
    """
    errors: list[str] = []
    if not FIXTURES_DIR.exists():
        return errors  # fixtures are optional

    valid_fixtures = list(FIXTURES_DIR.glob("valid_*.json"))
    invalid_fixtures = list(FIXTURES_DIR.glob("invalid_*.json"))

    # Validate that valid fixtures pass
    for fixture in sorted(valid_fixtures):
        try:
            data = json.loads(fixture.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{fixture}: JSON parse error: {exc}")
            continue

        # Determine which schema to use based on manifest structure
        schema_name = "plugin.json" if "v1_" in fixture.name or "v2_" in fixture.name else "plugin.json"
        fixture_errors = _validate_instance(data, schema_name, str(fixture))
        if fixture_errors:
            errors.append(f"{fixture}: expected VALID but got errors:")
            for err in fixture_errors:
                errors.append(f"    {err}")

    # Validate that invalid fixtures fail (we expect errors)
    for fixture in sorted(invalid_fixtures):
        try:
            data = json.loads(fixture.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{fixture}: JSON parse error: {exc}")
            continue

        schema_name = "plugin.json"
        fixture_errors = _validate_instance(data, schema_name, str(fixture))
        if not fixture_errors:
            errors.append(f"{fixture}: expected INVALID but passed validation (missing error detection)")

    return errors


# ----- Entry point ---------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate StudioBrain template assets.")
    parser.add_argument(
        "--core-version",
        help="Running core version (semver). When set, assets whose min_core_version "
             "is newer than this are rejected.",
    )
    parser.add_argument(
        "--allow-missing-compat",
        action="store_true",
        help="Do not require assets to declare compat.min_core_version. Useful while "
             "migrating existing content; default is strict.",
    )
    parser.add_argument(
        "--no-entity-yaml",
        action="store_true",
        help="Skip entity markdown frontmatter validation (faster local pass).",
    )
    parser.add_argument(
        "--no-compat",
        action="store_true",
        help="Skip compat (min_core_version) enforcement entirely.",
    )
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Validate fixture files in schemas/fixtures/ (valid_* should pass, invalid_* should fail).",
    )
    args = parser.parse_args(argv)

    if not HAVE_JSONSCHEMA:
        _info("WARNING: jsonschema not installed -- schema-shape checks will be skipped.")
    if not HAVE_YAML:
        _info("WARNING: pyyaml not installed -- YAML-dependent checks will be skipped.")

    all_errors: list[str] = []

    _info("== Checking schemas themselves ==")
    all_errors.extend(check_schemas_are_valid())

    _info("== Validating layouts ==")
    all_errors.extend(check_layouts())

    _info("== Validating packs ==")
    all_errors.extend(check_packs())

    _info("== Validating plugins ==")
    all_errors.extend(check_plugins())

    _info("== Validating skills ==")
    all_errors.extend(check_skills())

    _info("== Validating provider, ability, and workflow files ==")
    all_errors.extend(check_providers_and_abilities())

    _info("== Enforcing requires metadata ==")
    requires_errors, requires_warnings = check_requires()
    for w in requires_warnings:
        _info(f"WARN: {w}")
    all_errors.extend(requires_errors)

    if not args.no_entity_yaml:
        _info("== Validating entity markdown frontmatter ==")
        all_errors.extend(check_entity_frontmatter())

    if not args.no_compat:
        _info("== Enforcing compat metadata ==")
        compat_errors = check_compat(args.core_version)
        if args.allow_missing_compat:
            compat_errors = [
                e for e in compat_errors
                if "missing 'compat' object" not in e
                and "compat.min_core_version missing" not in e
            ]
        all_errors.extend(compat_errors)

    if args.fixtures:
        _info("== Validating fixtures ==")
        all_errors.extend(check_fixtures())

    if all_errors:
        _info("")
        for e in all_errors:
            _err(e)
        _info(f"\nFAILED: {len(all_errors)} error(s).")
        return 1

    _info("\nOK: all validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
