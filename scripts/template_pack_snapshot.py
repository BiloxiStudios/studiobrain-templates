"""Build official template-pack snapshots from one immutable Git commit.

The v1 snapshot preserves the indexed pack list and original UTF-8 file bytes
(including line endings) under their repository-relative paths. Pack manifests
retain references to separately distributed plugins, providers and named graphs.
Consumers pin a single snapshot SHA across one listing or installation.

The protected publisher supplies its monotonically increasing workflow run number.
A retry uses the same number. A successful immutable object readback precedes
the conditional update of current.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import posixpath
import re
import subprocess
import tempfile

PACKS = "templates/Packs"
INDEX = f"{PACKS}/index.json"
PUBLIC_PREFIX = "catalog/template-packs/v1"
POINTER = f"{PUBLIC_PREFIX}/current.json"
PACK_ID = re.compile(r"[a-z][a-z0-9_-]*")
CATALOG_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
REVISION = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
MEMBER_TYPES = {
    "templates": (".md",),
    "rules": (".md", ".yaml", ".yml"),
    "layouts": (".json",),
    "examples": (".md",),
    "canvas": (".yaml", ".yml"),
    "skills": (".yaml", ".yml"),
    "workflows": (".yaml", ".yml", ".json"),
}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def names(manifest, field):
    values = manifest.get(field, [])
    if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
        raise ValueError(f"{manifest.get('id')}: invalid {field}")
    return values


def collect(index, paths, read):
    if not isinstance(index, list) or not index:
        raise ValueError("The official pack index must contain at least one pack.")
    files, included, ids = {}, {}, set()

    def add(path):
        if path not in files:
            text = read(path)
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Missing or empty pack file: {path}")
            if path.endswith(".json"):
                try:
                    json.loads(text)
                except json.JSONDecodeError as err:
                    raise ValueError(f"Invalid JSON in pack file: {path}") from err
            files[path] = text
        return files[path]

    for entry in index:
        pack_id = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(pack_id, str) or not PACK_ID.fullmatch(pack_id) or pack_id in ids:
            raise ValueError(f"Invalid or duplicate pack ID: {pack_id!r}")
        ids.add(pack_id)
        root = f"{PACKS}/{pack_id}"
        if entry.get("path", root) != root:
            raise ValueError(f"{pack_id}: index path must match the pack directory")
        manifest = json.loads(add(f"{root}/pack.json"))
        if not isinstance(manifest, dict) or manifest.get("id") != pack_id:
            raise ValueError(f"{root}/pack.json does not identify its indexed pack")
        if not all(isinstance(manifest.get(k), str) and manifest[k].strip() for k in ("name", "version")):
            raise ValueError(f"{pack_id}: missing name or version")
        included[pack_id] = names(manifest, "includes")
        # Existing install compares untracked system rules with the stock copy
        # from the same source revision. Optional stock must remain distinguishable
        # from a pack's own rules/NAME_RULES.md, even when both have the same name.
        stock_names = {kind.upper() + "_RULES.md" for kind in names(manifest, "entity_types")
                       if re.fullmatch(r"[a-z0-9_-]+", kind)}
        stock_names.update(ref.split("/", 1)[1] for ref in names(manifest, "rules")
                           if re.fullmatch(r"rules/[A-Z][A-Z0-9_-]*_RULES\.md", ref))
        for name in stock_names:
            path = f"rules/{name}"
            if path in paths:
                add(path)
        for field, suffixes in MEMBER_TYPES.items():
            for ref in names(manifest, field):
                # Workflow IDs name independently published graphs, just as provider
                # and plugin IDs name their catalogs. Only path members bundle bytes.
                if field == "workflows" and CATALOG_ID.fullmatch(ref):
                    continue
                path = posixpath.normpath(posixpath.join(root, ref))
                if (ref.startswith("/") or "\\" in ref or
                        not path.startswith(("templates/", "rules/", "presets/")) or
                        not path.lower().endswith(suffixes)):
                    raise ValueError(f"{pack_id}: invalid {field} member {ref!r}")
                add(path)
            # Normal install also discovers undeclared text files in these subdirectories.
            # Examples are opt-in manifest entries, never inferred from examples/.
            if field != "examples":
                prefix = f"{root}/{field}/"
                for path in paths:
                    if path.startswith(prefix) and "/" not in path[len(prefix):] and path.lower().endswith(suffixes):
                        add(path)
        for field, directory, suffix in (("rulesets", "rules", ".md"), ("presets", "presets", ".preset.json")):
            for item in names(manifest, field):
                if not CATALOG_ID.fullmatch(item):
                    raise ValueError(f"{pack_id}: invalid {field} ID {item!r}")
                add(f"{directory}/{item}{suffix}")

    for pack_id, members in included.items():
        unknown = set(members) - ids
        if unknown:
            raise ValueError(f"{pack_id}: included packs missing from index: {sorted(unknown)}")
    return files


def build(root, revision):
    if not isinstance(revision, str) or not REVISION.fullmatch(revision):
        raise ValueError("A full Git source commit is required.")
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)
    if git("cat-file", "-t", revision).strip() != b"commit":
        raise ValueError("The source revision must be a commit.")
    objects = {}
    for row in git("ls-tree", "-rz", revision, "--", "templates", "rules", "presets").split(b"\0"):
        if row:
            meta, path = row.split(b"\t", 1)
            mode, _, oid = meta.split()
            objects[path.decode("utf-8")] = (mode, oid.decode("ascii"))

    def read(path):
        entry = objects.get(path)
        if entry is None or entry[0] not in (b"100644", b"100755"):
            raise ValueError(f"Missing regular file in {revision}: {path}")
        # Git blob bytes preserve the original line endings regardless of checkout settings.
        return git("cat-file", "blob", entry[1]).decode("utf-8")
    index = json.loads(read(INDEX))
    return encode({"schema_version": 1, "revision": revision, "index": index,
                   "files": collect(index, objects.keys(), read)})


def write_snapshot(root, revision, path):
    body = build(root, revision)
    path = pathlib.Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
        tmp = pathlib.Path(out.name)
        try:
            out.write(body)
            out.close()
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)


def stage_and_promote(client, bucket, body, revision, generation):
    """Caller supplies a verified snapshot built from revision. R2 applies the ETag condition atomically."""
    if not isinstance(generation, int) or generation < 1:
        raise ValueError("Publication requires a positive workflow generation.")
    digest = hashlib.sha256(body).hexdigest()
    key = f"{PUBLIC_PREFIX}/snapshots/{digest}.json"

    def status(error):
        return getattr(error, "response", {}).get("ResponseMetadata", {}).get("HTTPStatusCode")

    try:
        client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json",
                          CacheControl="public, max-age=31536000, immutable", IfNoneMatch="*")
    except Exception as error:
        if status(error) != 412:
            raise
    if client.get_object(Bucket=bucket, Key=key)["Body"].read() != body:
        raise ValueError("Stored pack snapshot did not match the source bytes.")

    for _ in range(3):
        try:
            obj = client.get_object(Bucket=bucket, Key=POINTER)
        except Exception as error:
            if status(error) != 404:
                raise
            condition = {"IfNoneMatch": "*"}
        else:
            old = json.loads(obj["Body"].read())
            sequence = old.get("generation")
            if (old.get("schema_version") != 1 or type(sequence) is not int or sequence < 1 or
                    not DIGEST.fullmatch(str(old.get("sha256", ""))) or
                    not REVISION.fullmatch(str(old.get("revision", "")))):
                raise ValueError("Cannot replace an unrecognized published pack pointer.")
            if sequence > generation:
                return "superseded"
            if sequence == generation:
                if old["sha256"] == digest and old["revision"] == revision:
                    return "unchanged"
                raise ValueError("This publication generation already identifies another snapshot.")
            condition = {"IfMatch": obj["ETag"]}
        pointer = {"schema_version": 1, "generation": generation, "sha256": digest, "revision": revision}
        try:
            client.put_object(Bucket=bucket, Key=POINTER, Body=encode(pointer), ContentType="application/json",
                              CacheControl="no-cache", **condition)
        except Exception as error:
            if status(error) != 412:
                raise
        else:
            return "published"
    raise RuntimeError("The published pack pointer changed during promotion. Retry this generation.")
