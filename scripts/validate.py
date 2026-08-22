#!/usr/bin/env python3
"""StudioBrain templates -- schema + compat validator.

Runs every CI-facing check from one place:

  1. Confirms every schema file in ``schemas/`` is a valid JSON Schema (Draft 2020-12).
  2. Validates every ``*.layout.json`` against ``schemas/layout.json``.
  3. Validates every ``pack.json`` against ``schemas/pack.json``.
  4. Validates leftover ``plugin.json`` files if a ``plugins/`` tree exists
     (official plugins no longer live in this repo — SBAI-7665).
  5. Validates every skill YAML frontmatter against ``schemas/skill.yaml.json``.
  6. Validates ``*.provider.yaml`` / ``*.ability.yaml`` / ``*.canvas.yaml``
     (and leftover ``*.workflow.yaml``) against ``schemas/provider.json``,
     ``schemas/ability.json``, and ``schemas/canvas.json`` (SBAI-7569 / SBAI-7651).
  6b. Validates ``taxonomies/*.yaml`` against ``schemas/taxonomy.json``,
     recomputes each ``content_hash``, and proves every
     ``taxonomies/*.embeddings.json`` still matches the taxonomy it stamps --
     label for label, in order (SBAI-7726).
  7. Validates entity markdown YAML frontmatter against ``schemas/<entity_type>.json``
     (best-effort -- skipped if pyyaml is unavailable).
  8. Enforces compat metadata: every layout / pack / plugin / skill MUST declare
     ``compat.min_core_version`` as a semver string. When ``--core-version`` is
     supplied, the script also refuses assets whose ``min_core_version`` is
     newer than the running core.
  9. Enforces ``requires`` metadata on providers / canvases: ``wire: process``
     and localhost providers must declare ``platforms: [desktop]``; ``wire:
     in-app`` providers must declare no wire-call field (base_url / endpoint /
     auth / request / response) and no money field (billing / pricing), plus a
     ``runtime`` and at least one ``weights`` row; canvases must cover the
     platforms (error) and env / models (warning) of every provider their
     steps use.
 10. Checks ``catalog-index.json`` (SBAI-7611) is in sync with the catalog
     files on disk by rebuilding the entries in-memory and comparing
     (``generated_at`` is ignored -- it pins to the commit timestamp).

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
TAXONOMIES_DIR = ROOT / "taxonomies"

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
    if not PLUGINS_DIR.is_dir():
        return errors
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


# ----- Taxonomies (SBAI-7726) ----------------------------------------------------

def _load_taxonomy_tools():
    """Import scripts/generate_taxonomy_embeddings.py.

    Same trick as _load_catalog_builder: the generator owns the canonical-form
    and label-flattening logic, and re-implementing either here would let the
    two drift and quietly stop enforcing anything. Its module level is
    stdlib-only (the heavy deps are imported inside the functions that need
    them), so this import is cheap.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "generate_taxonomy_embeddings", ROOT / "scripts" / "generate_taxonomy_embeddings.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _artifact_stamp_errors(
    label: str,
    artifact: dict[str, Any],
    doc: dict[str, Any],
    computed_hash: str,
    tools: Any,
) -> list[str]:
    """Cross-check one embeddings artifact against the taxonomy it claims."""
    errors: list[str] = []
    stamp = artifact.get("taxonomy") or {}
    if stamp.get("content_hash") != computed_hash:
        errors.append(
            f"{label}: artifact is STALE -- taxonomy content_hash is {computed_hash}, "
            f"artifact carries {stamp.get('content_hash')!r}. Regenerate with "
            "scripts/generate_taxonomy_embeddings.py"
        )
    if str(stamp.get("revision")) != str(doc.get("revision")):
        errors.append(
            f"{label}: artifact taxonomy revision {stamp.get('revision')!r} != "
            f"taxonomy revision {doc.get('revision')!r}"
        )

    scoring = artifact.get("scoring") or {}
    for field in ("formula", "logit_scale", "logit_bias"):
        if field not in scoring:
            errors.append(
                f"{label}: scoring.{field} missing -- without the learned sigmoid "
                "calibration every device-side threshold is meaningless"
            )

    model = artifact.get("model") or {}
    embed_dim = model.get("embed_dim")
    if not isinstance(embed_dim, int) or embed_dim <= 0:
        errors.append(f"{label}: model.embed_dim must be a positive integer")
        embed_dim = None
    for field in ("id", "revision", "file"):
        if not model.get(field):
            errors.append(f"{label}: model.{field} missing -- artifact has no provenance")

    try:
        expected = tools.build_labels(doc)
    except SystemExit as exc:  # noqa: PERF203 -- taxonomy already reported broken
        return errors + [f"{label}: cannot flatten taxonomy: {exc}"]

    labels = artifact.get("labels")
    if not isinstance(labels, list):
        return errors + [f"{label}: labels must be a list"]
    if len(labels) != len(expected):
        return errors + [
            f"{label}: has {len(labels)} label vectors but the taxonomy has "
            f"{len(expected)} labels"
        ]
    if artifact.get("label_count") != len(labels):
        errors.append(
            f"{label}: label_count {artifact.get('label_count')!r} != {len(labels)} vectors"
        )

    for index, (got, want) in enumerate(zip(labels, expected)):
        if not isinstance(got, dict):
            errors.append(f"{label}: labels[{index}] is not an object")
            continue
        for field in ("id", "axis", "term", "text"):
            if got.get(field) != want[field]:
                errors.append(
                    f"{label}: labels[{index}].{field} is {got.get(field)!r}, "
                    f"taxonomy order says {want[field]!r}"
                )
        vec = got.get("embedding")
        if not isinstance(vec, list):
            errors.append(f"{label}: labels[{index}].embedding is not a list")
            continue
        if embed_dim is not None and len(vec) != embed_dim:
            errors.append(
                f"{label}: labels[{index}].embedding has {len(vec)} dims, "
                f"model.embed_dim says {embed_dim}"
            )
            continue
        # Vectors are stored L2-normalised and rounded; anything materially off
        # unit length means the file was hand-edited or truncated.
        norm = sum(float(x) * float(x) for x in vec) ** 0.5
        if abs(norm - 1.0) > 1e-3:
            errors.append(
                f"{label}: labels[{index}] ({got.get('id')}) has L2 norm {norm:.6f}, "
                "expected a unit vector"
            )
    return errors


def check_taxonomies() -> list[str]:
    """Validate taxonomies/ and their precomputed embedding artifacts (SBAI-7726).

    Two things are enforced that a JSON Schema cannot express:

    - ``content_hash`` really is the hash of the axes block. It lives in the
      file it stamps, so nothing but a recompute proves it.
    - every ``*.embeddings.json`` matches the taxonomy it names, label for
      label, in order. That pairing is the ONLY staleness signal the device
      has: it downloads a vision tower and trusts these vectors blindly, so a
      taxonomy edit without a regenerated artifact would silently score assets
      against the previous vocabulary.
    """
    errors: list[str] = []
    if not TAXONOMIES_DIR.exists():
        return errors
    if not HAVE_YAML:
        _info("NOTE: pyyaml not installed -- skipping taxonomy validation.")
        return errors
    tools = _load_taxonomy_tools()

    taxonomies: dict[str, tuple[pathlib.Path, dict[str, Any], str]] = {}
    for path in sorted(TAXONOMIES_DIR.glob("*.yaml")) + sorted(TAXONOMIES_DIR.glob("*.yml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{path}: YAML parse error: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: top-level YAML is not a mapping")
            continue
        errors.extend(_validate_instance(data, "taxonomy.json", str(path)))
        try:
            computed = tools.content_hash(data)
        except SystemExit as exc:
            errors.append(f"{path}: {exc}")
            continue
        declared = str(data.get("content_hash") or "")
        if declared != computed:
            errors.append(
                f"{path}: content_hash is stale (declared {declared or '<missing>'}, "
                f"computed {computed}) -- run "
                "scripts/generate_taxonomy_embeddings.py --update-hash"
            )
        tid = str(data.get("id") or "")
        if tid:
            if tid in taxonomies:
                errors.append(f"{path}: duplicate taxonomy id {tid!r}")
            taxonomies[tid] = (path, data, computed)

    for path in sorted(TAXONOMIES_DIR.glob("*.embeddings.json")):
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: JSON parse error: {exc}")
            continue
        if artifact.get("artifact_schema_version") != 1:
            errors.append(
                f"{path}: artifact_schema_version must be 1, got "
                f"{artifact.get('artifact_schema_version')!r}"
            )
        tid = str((artifact.get("taxonomy") or {}).get("id") or "")
        if tid not in taxonomies:
            errors.append(f"{path}: names taxonomy id {tid!r}, which no taxonomies/*.yaml declares")
            continue
        _, doc, computed = taxonomies[tid]
        errors.extend(_artifact_stamp_errors(str(path), artifact, doc, computed, tools))

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
    # SBAI-7726 asset intelligence: asset-tagging = zero-shot scoring against a
    # taxonomy (SigLIP-2), asset-caption = describing an asset in prose.
    "asset-tagging", "asset-caption",
}


def check_requires() -> tuple[list[str], list[str]]:
    """Enforce ``requires`` metadata on providers and workflows (SBAI-7569).

    Returns (errors, warnings):
    - ERROR: a ``wire: process`` provider must declare requires.platforms
      containing ``desktop``.
    - ERROR: a provider with a localhost base_url must declare
      requires.platforms containing ``desktop`` (cloud workers cannot run it).
    - ERROR: a ``wire: in-app`` provider must not declare any wire-call field
      (``base_url`` / ``endpoint`` / ``auth`` / ``request`` / ``response`` --
      it never talks to a URL) nor any money field (``billing`` / ``pricing``
      -- the user's own device is free and must never debit BrainBits); it
      must declare ``runtime`` and at least one ``weights`` row with a
      non-empty, unique ``id`` and a non-empty ``source`` (SBAI-7625/7626).
    - ERROR: ``runtime`` / ``weights`` on a provider whose wire is not
      ``in-app`` -- they describe on-device execution only, and the catalog
      index badges them to the marketplace.
    - WARN: an in-app ``weights`` row whose ``source`` is not
      ``huggingface://...``.
    - WARN: an in-app ``weights`` row serving ``llm-chat`` (explicitly, or by
      omitting ``capability``) that lacks ``context_length`` or omits
      ``tools`` -- the executor would fall back to unverifiable defaults.
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

        # wire: in-app invariants (SBAI-7625/7626): the model executes inside
        # the client app via the ai-sdk on-device executor -- same doctrine as
        # wire: process, cloud workers must 501 it. It never talks to a URL,
        # so every wire-call field (base_url, endpoint, request, response) and
        # auth are meaningless; runtime + weights are how the executor knows
        # what engine and which weight rows to use. billing/pricing are
        # forbidden outright: the user's own device is free and this path must
        # never debit BrainBits (owner lock, SBAI-7625 design §1).
        is_in_app = data.get("wire") == "in-app"
        if is_in_app:
            for field in ("base_url", "endpoint", "auth", "request", "response"):
                if data.get(field):
                    errors.append(
                        f"{path}: provider '{pid}' has wire 'in-app' -- must not declare "
                        f"{field} (it never talks to a URL)"
                    )
            for field in ("billing", "pricing"):
                if data.get(field):
                    errors.append(
                        f"{path}: provider '{pid}' has wire 'in-app' -- must not declare "
                        f"{field}: execution on the user's own device is free and must "
                        "never be metered"
                    )
            if not data.get("runtime"):
                errors.append(
                    f"{path}: provider '{pid}' has wire 'in-app' -- runtime is required"
                )
            weights = data.get("weights") or []
            if not weights:
                errors.append(
                    f"{path}: provider '{pid}' has wire 'in-app' -- requires at least one weights row"
                )
            seen_rows: set[str] = set()
            for row in weights:
                if not isinstance(row, dict):
                    continue
                rid = str(row.get("id") or "")
                if rid:
                    if rid in seen_rows:
                        errors.append(
                            f"{path}: provider '{pid}' has duplicate weights row id {rid!r} "
                            "-- the executor selects rows by id, so ids must be unique"
                        )
                    seen_rows.add(rid)
                source = str(row.get("source") or "")
                if not source:
                    errors.append(
                        f"{path}: provider '{pid}' weights row {rid!r} has an "
                        "empty source -- nothing to download"
                    )
                elif not source.startswith("huggingface://"):
                    warnings.append(
                        f"{path}: provider '{pid}' weights row {row.get('id')!r} has "
                        f"source {source!r} -- expected 'huggingface://<repo-id>'"
                    )
                # Capability metadata on chat rows (SBAI-7625/7626). A row
                # with no explicit capability is a chat row by convention.
                # Without context_length the orchestrator compacts against a
                # hard-coded default that may exceed this tier's real window;
                # without an explicit tools flag the executor cannot tell
                # "emits tool calls" from "not stated" and hands tool
                # definitions to a model that may render them as prose. Both
                # are WARN, not ERROR: the fields are optional in the schema
                # and older catalogs must keep validating.
                # Zero-shot rows (SBAI-7726) are useless without the artifact
                # holding their taxonomy's precomputed text embeddings: the row
                # ships a vision tower only, so a dangling pointer means the
                # device downloads weights and then has nothing to score
                # against. Hard error -- exactly the class of "dead-ends AFTER
                # the download" failure the SBAI-7682 witness paid for once.
                artifact_rel = row.get("taxonomy_embeddings")
                if artifact_rel:
                    artifact_path = ROOT / str(artifact_rel)
                    if not artifact_path.is_file():
                        errors.append(
                            f"{path}: provider '{pid}' weights row {rid!r} points at "
                            f"taxonomy_embeddings {artifact_rel!r}, which does not exist"
                        )
                    else:
                        try:
                            artifact_doc = json.loads(
                                artifact_path.read_text(encoding="utf-8")
                            )
                        except json.JSONDecodeError as exc:
                            errors.append(f"{artifact_path}: JSON parse error: {exc}")
                            artifact_doc = {}
                        stamp = artifact_doc.get("taxonomy") or {}
                        declared_tax = row.get("taxonomy")
                        if declared_tax and stamp.get("id") != declared_tax:
                            errors.append(
                                f"{path}: provider '{pid}' weights row {rid!r} declares "
                                f"taxonomy {declared_tax!r} but {artifact_rel} holds "
                                f"{stamp.get('id')!r}"
                            )
                        # The artifact is per MODEL TIER, not per taxonomy: one
                        # taxonomy has an artifact per tier and they are NOT
                        # interchangeable (siglip2-base embeds at 768 dims,
                        # so400m at 1152). Both artifacts name the same taxonomy
                        # id, so the check above cannot separate them -- only the
                        # model the vectors were produced by can. A crossed
                        # pointer passes every other gate and then dot-products
                        # mismatched widths on the device, AFTER the download.
                        artifact_model = str((artifact_doc.get("model") or {}).get("id") or "")
                        row_repo = str(row.get("source") or "").split("://", 1)[-1]
                        if artifact_model and row_repo and artifact_model != row_repo:
                            errors.append(
                                f"{path}: provider '{pid}' weights row {rid!r} loads "
                                f"{row_repo} but {artifact_rel} was built from "
                                f"{artifact_model} -- taxonomy_embeddings is per model "
                                "tier and tiers are not interchangeable"
                            )
                elif row.get("taxonomy"):
                    warnings.append(
                        f"{path}: provider '{pid}' weights row {rid!r} names a taxonomy "
                        "but no taxonomy_embeddings artifact -- the device would have to "
                        "run the text tower it does not download"
                    )

                row_capability = row.get("capability") or "llm-chat"
                if row_capability == "llm-chat":
                    missing = [
                        field
                        for field in ("context_length", "tools")
                        if field not in row
                    ]
                    if missing:
                        warnings.append(
                            f"{path}: provider '{pid}' weights row {rid!r} serves "
                            f"'{row_capability}' but omits {', '.join(missing)} -- "
                            "the executor falls back to defaults it cannot verify"
                        )
        else:
            # runtime / weights describe on-device execution and are in-app
            # only. Left unguarded, a cloud provider could declare them and
            # build_catalog_index.py would badge it "runtime: transformers.js"
            # in the marketplace index -- telling the client it runs locally
            # when every call still leaves the device.
            for field in ("runtime", "weights"):
                if data.get(field):
                    errors.append(
                        f"{path}: provider '{pid}' declares {field} but has wire "
                        f"{data.get('wire')!r} -- {field} is 'wire: in-app' only"
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
            # "desktop-only" means the provider CANNOT run anywhere else --
            # i.e. its platform list is exactly {desktop} (WORKFLOW_RULES.md
            # "Canvases aggregate requires from their providers"). A provider
            # that also runs on web/mobile/cloud (e.g. the wire: in-app
            # on-device provider, platforms: [web, desktop, mobile]) must NOT
            # drag the whole canvas down to desktop-only -- that would make
            # cloud workers 501 it and hide it on web and mobile.
            pplatforms = set(preq.get("platforms") or [])
            if pplatforms and pplatforms <= {"desktop"} and "desktop" not in platforms:
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


# ----- Catalog index -------------------------------------------------------------

CATALOG_INDEX_PATH = ROOT / "catalog-index.json"


def _load_catalog_builder():
    """Import scripts/build_catalog_index.py (single source of truth for scanning)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_catalog_index", ROOT / "scripts" / "build_catalog_index.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def check_catalog_index() -> list[str]:
    """Check catalog-index.json is in sync with the files on disk (SBAI-7611).

    Cheap consistency check: rebuild the entries in-memory with the builder
    and compare. Catches stale/missing ids, paths, and badge drift in both
    directions. ``generated_at`` is ignored (it pins to the commit timestamp
    by design, so it legitimately differs from a local rebuild).
    """
    if not HAVE_YAML:
        _info("NOTE: pyyaml not installed -- skipping catalog index validation.")
        return []
    if not CATALOG_INDEX_PATH.exists():
        return [f"{CATALOG_INDEX_PATH}: catalog index missing -- run scripts/build_catalog_index.py"]
    try:
        index = json.loads(CATALOG_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{CATALOG_INDEX_PATH}: JSON parse error: {exc}"]
    errors: list[str] = []
    version = index.get("index_schema_version")
    if version != 1:
        errors.append(f"{CATALOG_INDEX_PATH}: index_schema_version must be 1, got {version!r}")
    expected = _load_catalog_builder().build_entries(ROOT)
    actual = index.get("entries")
    if actual != expected:
        expected_keys = {(e["kind"], e["id"]) for e in expected}
        actual_keys = {(e.get("kind"), e.get("id")) for e in actual or [] if isinstance(e, dict)}
        detail = ""
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        if missing:
            detail += f" missing entries: {missing};"
        if extra:
            detail += f" stale entries: {extra};"
        if not detail:
            detail = " entry badge fields differ;"
        errors.append(
            f"{CATALOG_INDEX_PATH}: entries out of date ({detail.strip()})"
            " -- run scripts/build_catalog_index.py"
        )
    return errors


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
    if PLUGINS_DIR.is_dir():
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

    _info("== Validating taxonomies and embedding artifacts ==")
    all_errors.extend(check_taxonomies())

    _info("== Enforcing requires metadata ==")
    requires_errors, requires_warnings = check_requires()
    for w in requires_warnings:
        _info(f"WARN: {w}")
    all_errors.extend(requires_errors)

    _info("== Validating catalog index ==")
    all_errors.extend(check_catalog_index())

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
