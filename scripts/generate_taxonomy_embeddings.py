#!/usr/bin/env python3
"""Precompute the SigLIP-2 text embeddings for a StudioBrain taxonomy (SBAI-7726).

Why this exists
---------------
The on-device quick tagger scores an asset against the whole taxonomy with a
**vision-only** SigLIP-2 load (``SiglipVisionModel``, ``model_file_name:
'vision_model'``). That is a 55-95 MB download instead of the 378 MB-1.07 GB
combined model -- but only because the *text* side is computed once here,
offline, and shipped as data. The device never runs the text tower.

The artifact this writes (``<taxonomy>.embeddings.json``) therefore has to
carry everything the device needs to turn a cosine similarity into the same
number the ``zero-shot-image-classification`` pipeline would have produced:

    score = sigmoid(logit_scale * dot(unit(image_embed), unit(text_embed))
                    + logit_bias)

``logit_scale`` / ``logit_bias`` are SigLIP's learned sigmoid calibration.
Without them the scores are raw cosine similarities in ~[-0.1, 0.3] and every
threshold in the product is meaningless (report-web-siglip "Sigmoid
calibration" risk). They live as scalars in the ORIGINAL checkpoint, not in
the split ONNX text/vision graphs, so we read them straight out of
``google/siglip2-base-patch16-256``'s safetensors with two HTTP range
requests (8 bytes of payload -- no 1.5 GB download). Note the checkpoint
stores ``logit_scale`` in log space; the model applies ``exp()`` to it, so the
artifact records both the raw parameter and the effective multiplier.

Not run in CI. Regenerate by hand whenever the taxonomy's ``content_hash``
moves, and commit the result -- ``scripts/validate.py`` fails the build if the
artifact's stamp no longer matches the taxonomy.

Tokenization follows the SigLIP contract exactly: ``padding='max_length'``,
``truncation=True``, ``max_length=64`` (this is what makes SigLIP different
from CLIP and what the transformers.js pipeline does for ``model_type ==
'siglip'``). Embeddings are L2-normalised and rounded to 6 decimals -- unit
vectors, so the rounding error is ~1e-6, far below any scoring threshold, and
it keeps the committed JSON small and diff-stable.

One artifact per model tier: a taxonomy embedded with the base tier (768-d)
cannot be scored against so400m image embeddings (1152-d), so each catalog
weight row names the artifact it belongs to via ``taxonomy_embeddings``.

Usage::

    pip install onnxruntime huggingface_hub transformers numpy pyyaml
    python3 scripts/generate_taxonomy_embeddings.py                 # base tier
    python3 scripts/generate_taxonomy_embeddings.py --tier so400m   # quality tier
    python3 scripts/generate_taxonomy_embeddings.py --update-hash   # after editing terms
    python3 scripts/generate_taxonomy_embeddings.py --print-labels  # no download, no model

Exit code is non-zero on any failure; the artifact is written atomically at
the end so a failed run never leaves a half-written file behind.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import struct
import sys
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAXONOMIES_DIR = ROOT / "taxonomies"

# Model tiers (spec SBAI-7726 §5). `onnx_repo` is what the DEVICE downloads
# (vision tower only); `calibration_repo` is the original checkpoint the ONNX
# was converted from and the only place logit_scale / logit_bias survive as
# named tensors.
#
# The text tower here is fp32 on purpose. On-device dtype is a size/latency
# tradeoff, but this runs offline once, so there is nothing to buy by
# quantising: measured on this taxonomy, the int8 text tower's label vectors
# sit at mean cosine 0.958 against fp32, which is pure avoidable error baked
# into every score the product will ever compute. fp32 ONNX text embeddings
# were verified cosine-1.0000 against the HF PyTorch reference.
CALIBRATION_FILE = "model.safetensors"

TIERS: dict[str, dict[str, Any]] = {
    "base": {
        "onnx_repo": "onnx-community/siglip2-base-patch16-256-ONNX",
        "text_file": "onnx/text_model.onnx",
        "text_extra_files": (),
        "dtype": "fp32",
        "calibration_repo": "google/siglip2-base-patch16-256",
        "artifact_suffix": "",
    },
    "so400m": {
        "onnx_repo": "onnx-community/siglip2-so400m-patch16-256-ONNX",
        "text_file": "onnx/text_model.onnx",
        # This repo's fp32 text graph exceeds the 2 GB protobuf limit and
        # stores its weights beside it; ORT resolves the sibling by relative
        # name, so it has to be fetched into the same snapshot directory.
        "text_extra_files": ("onnx/text_model.onnx_data",),
        "dtype": "fp32",
        "calibration_repo": "google/siglip2-so400m-patch16-256",
        "artifact_suffix": ".so400m",
    },
}

# SigLIP tokenization contract.
MAX_LENGTH = 64
PADDING = "max_length"

ARTIFACT_SCHEMA_VERSION = 1
SCORE_FORMULA = (
    "sigmoid(logit_scale * dot(l2_normalize(image_embed), l2_normalize(text_embed))"
    " + logit_bias)"
)
FLOAT_PRECISION = 6

# Selection policy shipped WITH the calibration, because the two are only
# meaningful together.
#
# SigLIP's learned sigmoid is calibrated for retrieval against SPECIFIC
# captions, not generic vocabulary terms. Measured against the HF PyTorch
# reference on the standard two-cats image: the specific caption "a photo of 2
# cats." scores cos 0.1473 -> p 0.4639, while this taxonomy's deliberately
# generic "a photo of an animal." scores cos 0.0774 -> p 0.0003 on the very
# same image -- correct ranking, tiny absolute probability. A naive 0.5 (or
# 0.3) probability cut therefore emits ZERO tags for every asset, forever.
#
# So the contract is: rank within each axis, keep the top-k, and use the floor
# only to drop an axis that matched nothing. Consumers persist the calibrated
# probability as the tag score either way -- scores stay comparable across
# assets because the calibration is fixed.
DEFAULT_TOP_K_PER_AXIS = 2
DEFAULT_THRESHOLD = 0.001
SELECTION_NOTE = (
    "SigLIP's sigmoid is calibrated for specific-caption retrieval, so generic "
    "taxonomy terms score low in absolute terms even when ranked correctly "
    "(reference check: 'a photo of 2 cats.' p=0.4639 vs 'a photo of an animal.' "
    "p=0.0003 on the same image). Select by rank within each axis "
    "(default_top_k_per_axis) and treat default_threshold as a floor that drops "
    "an axis which matched nothing -- never as a standalone accept/reject cut."
)


# ----- Taxonomy ------------------------------------------------------------------

def load_taxonomy(path: pathlib.Path) -> dict[str, Any]:
    import yaml  # noqa: PLC0415  -- optional dep, imported where it is used

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: top-level YAML is not a mapping")
    if data.get("kind") != "taxonomy":
        raise SystemExit(f"{path}: kind must be 'taxonomy', got {data.get('kind')!r}")
    return data


def canonical_axes(doc: dict[str, Any]) -> str:
    """Canonical JSON of the axes block -- the pre-image of ``content_hash``.

    Only the fields that change the embedded text are included (template +
    ordered term id/prompt pairs), so editing a ``display`` string does not
    invalidate a perfectly good artifact. Keys are sorted; term ORDER is
    preserved because the artifact stores vectors in that order.
    """
    axes = doc.get("axes")
    if not isinstance(axes, dict) or not axes:
        raise SystemExit("taxonomy has no axes")
    payload: dict[str, Any] = {}
    for axis_id, axis in axes.items():
        if not isinstance(axis, dict):
            raise SystemExit(f"axis {axis_id!r} is not a mapping")
        payload[str(axis_id)] = {
            "hypothesis_template": str(axis.get("hypothesis_template") or ""),
            "terms": [
                {"id": str(t.get("id")), "prompt": str(t.get("prompt"))}
                for t in (axis.get("terms") or [])
            ],
        }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(doc: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_axes(doc).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_labels(doc: dict[str, Any]) -> list[dict[str, str]]:
    """Flatten the taxonomy into the ordered label list the artifact stores."""
    labels: list[dict[str, str]] = []
    for axis_id, axis in doc["axes"].items():
        template = str(axis.get("hypothesis_template") or "{}")
        if "{}" not in template:
            raise SystemExit(f"axis {axis_id!r}: hypothesis_template has no '{{}}' placeholder")
        for term in axis.get("terms") or []:
            term_id = str(term["id"])
            labels.append(
                {
                    "id": f"{axis_id}/{term_id}",
                    "axis": str(axis_id),
                    "term": term_id,
                    "text": template.replace("{}", str(term["prompt"])),
                }
            )
    if not labels:
        raise SystemExit("taxonomy produced no labels")
    seen: set[str] = set()
    for label in labels:
        if label["id"] in seen:
            raise SystemExit(f"duplicate label id {label['id']!r}")
        seen.add(label["id"])
    return labels


# ----- Sigmoid calibration -------------------------------------------------------

def _range_get(url: str, start: int, end: int, timeout: int) -> bytes:
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 -- fixed https host
        return resp.read()


def fetch_calibration(repo: str, revision: str, timeout: int = 60) -> dict[str, float]:
    """Read logit_scale / logit_bias out of a safetensors file by byte range.

    safetensors layout: u64 little-endian header length, then that many bytes
    of JSON describing every tensor's dtype/shape/byte range, then the tensor
    data. Both values are single fp32 scalars, so this pulls a JSON header and
    8 bytes instead of the whole 1.5 GB checkpoint.
    """
    import math  # noqa: PLC0415

    url = f"https://huggingface.co/{repo}/resolve/{revision}/{CALIBRATION_FILE}"
    header_len = struct.unpack("<Q", _range_get(url, 0, 7, timeout))[0]
    header = json.loads(_range_get(url, 8, 8 + header_len - 1, timeout).decode("utf-8"))
    data_start = 8 + header_len

    out: dict[str, float] = {}
    for name in ("logit_scale", "logit_bias"):
        entry = header.get(name)
        if not entry:
            raise SystemExit(f"{repo}: {CALIBRATION_FILE} has no {name!r} tensor")
        if entry.get("dtype") != "F32":
            raise SystemExit(f"{repo}: {name} dtype is {entry.get('dtype')!r}, expected F32")
        lo, hi = entry["data_offsets"]
        raw = _range_get(url, data_start + lo, data_start + hi - 1, timeout)
        out[name] = float(struct.unpack("<f", raw)[0])

    # The checkpoint stores logit_scale in log space; SigLIP's forward pass
    # applies exp() before scaling the similarity matrix. Record both so no
    # consumer has to guess which convention a bare "logit_scale" follows.
    return {
        "logit_scale_raw": out["logit_scale"],
        "logit_scale": math.exp(out["logit_scale"]),
        "logit_bias": out["logit_bias"],
    }


# ----- Text embeddings -----------------------------------------------------------

def resolve_revision(repo: str, timeout: int = 60) -> str:
    with urllib.request.urlopen(  # noqa: S310 -- fixed https host
        f"https://huggingface.co/api/models/{repo}", timeout=timeout
    ) as resp:
        info = json.load(resp)
    sha = info.get("sha")
    if not sha:
        raise SystemExit(f"{repo}: model info has no commit sha")
    return str(sha)


def tokenize(texts: list[str], repo: str, revision: str):
    """Tokenize with the SigLIP contract: max_length padding, truncation, 64 tokens."""
    import numpy as np  # noqa: PLC0415

    try:
        from transformers import AutoTokenizer  # noqa: PLC0415

        tok = AutoTokenizer.from_pretrained(repo, revision=revision)
        enc = tok(
            texts,
            padding=PADDING,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="np",
        )
        return {k: np.asarray(v, dtype=np.int64) for k, v in enc.items()}
    except Exception as exc:  # noqa: BLE001 -- fall back to the raw tokenizer
        print(f"NOTE: transformers AutoTokenizer unavailable ({exc}); using tokenizers", file=sys.stderr)
        from huggingface_hub import hf_hub_download  # noqa: PLC0415
        from tokenizers import Tokenizer  # noqa: PLC0415

        tok = Tokenizer.from_file(
            hf_hub_download(repo, "tokenizer.json", revision=revision)
        )
        tok.enable_truncation(max_length=MAX_LENGTH)
        tok.enable_padding(length=MAX_LENGTH)
        encs = tok.encode_batch(texts)
        return {
            "input_ids": np.asarray([e.ids for e in encs], dtype=np.int64),
            "attention_mask": np.asarray([e.attention_mask for e in encs], dtype=np.int64),
        }


def embed_texts(
    texts: list[str],
    repo: str,
    revision: str,
    onnx_file: str,
    extra_files: tuple[str, ...] = (),
):
    import numpy as np  # noqa: PLC0415
    import onnxruntime as ort  # noqa: PLC0415
    from huggingface_hub import hf_hub_download  # noqa: PLC0415

    for extra in extra_files:
        print(f"downloading {repo}@{revision[:8]} :: {extra} (external weights)", flush=True)
        hf_hub_download(repo, extra, revision=revision)
    print(f"downloading {repo}@{revision[:8]} :: {onnx_file}", flush=True)
    model_path = hf_hub_download(repo, onnx_file, revision=revision)
    print(f"loading ONNX session: {model_path}", flush=True)
    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    wanted = {i.name for i in sess.get_inputs()}
    encoded = tokenize(texts, repo, revision)
    feeds = {name: encoded[name] for name in wanted if name in encoded}
    missing = wanted - set(feeds)
    if missing:
        raise SystemExit(f"tokenizer did not produce required ONNX inputs: {sorted(missing)}")
    print(f"ONNX inputs: {sorted(wanted)} | feeding {sorted(feeds)}", flush=True)

    out_names = [o.name for o in sess.get_outputs()]
    print(f"ONNX outputs: {out_names}", flush=True)
    if "pooler_output" not in out_names:
        raise SystemExit(
            f"{onnx_file} has no 'pooler_output' -- SigLIP text embeddings come from the "
            f"pooler head; got {out_names}"
        )

    # Batch so peak RAM stays flat on the int8 graph.
    chunks = []
    batch = 16
    for start in range(0, len(texts), batch):
        sliced = {k: v[start : start + batch] for k, v in feeds.items()}
        pooled = sess.run(["pooler_output"], sliced)[0]
        chunks.append(np.asarray(pooled, dtype=np.float32))
        print(f"  embedded {min(start + batch, len(texts))}/{len(texts)}", flush=True)
    vectors = np.concatenate(chunks, axis=0)

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if not np.all(norms > 0):
        raise SystemExit("a text embedding came back as an all-zero vector")
    return vectors / norms


# ----- Artifact ------------------------------------------------------------------

def build_artifact(
    doc: dict[str, Any],
    labels: list[dict[str, str]],
    vectors,
    calibration: dict[str, float],
    tier_name: str,
    tier: dict[str, Any],
    onnx_revision: str,
    calibration_revision: str,
) -> dict[str, Any]:
    embed_dim = int(vectors.shape[1])
    rows = []
    for label, vec in zip(labels, vectors):
        rows.append(
            {
                **label,
                "embedding": [round(float(x), FLOAT_PRECISION) for x in vec],
            }
        )
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "taxonomy": {
            "id": str(doc["id"]),
            "revision": str(doc["revision"]),
            "content_hash": content_hash(doc),
        },
        "model": {
            "id": tier["onnx_repo"],
            "tier": tier_name,
            "revision": onnx_revision,
            "file": tier["text_file"],
            "dtype": tier["dtype"],
            "embed_dim": embed_dim,
            "tower": "text",
            "tokenizer": {
                "padding": PADDING,
                "max_length": MAX_LENGTH,
                "truncation": True,
            },
        },
        "scoring": {
            "formula": SCORE_FORMULA,
            "logit_scale": calibration["logit_scale"],
            "logit_scale_raw": calibration["logit_scale_raw"],
            "logit_bias": calibration["logit_bias"],
            "calibration_source": {
                "repo": tier["calibration_repo"],
                "revision": calibration_revision,
                "file": CALIBRATION_FILE,
                "note": (
                    "logit_scale_raw is the checkpoint parameter (log space); "
                    "logit_scale is exp(logit_scale_raw), the multiplier the model "
                    "actually applies."
                ),
            },
            "embeddings_l2_normalized": True,
            "default_top_k_per_axis": DEFAULT_TOP_K_PER_AXIS,
            "default_threshold": DEFAULT_THRESHOLD,
            "selection_note": SELECTION_NOTE,
        },
        "generator": "scripts/generate_taxonomy_embeddings.py",
        "label_count": len(rows),
        "labels": rows,
    }


def render(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"


# ----- Entry point ---------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--taxonomy",
        default=str(TAXONOMIES_DIR / "asset-tags.yaml"),
        help="Taxonomy YAML to embed (default: taxonomies/asset-tags.yaml).",
    )
    parser.add_argument(
        "--tier",
        default="base",
        choices=sorted(TIERS),
        help="Model tier to embed for (default: base). One artifact per tier -- "
             "embedding dimensionality differs, so they are not interchangeable.",
    )
    parser.add_argument(
        "--out",
        help="Artifact path (default: <taxonomy stem><tier suffix>.embeddings.json "
             "next to the taxonomy).",
    )
    parser.add_argument(
        "--update-hash",
        action="store_true",
        help="Rewrite the taxonomy's content_hash line to the recomputed value, then continue.",
    )
    parser.add_argument(
        "--print-labels",
        action="store_true",
        help="Print the composed candidate texts and the content hash, then exit (no download).",
    )
    args = parser.parse_args(argv)

    taxonomy_path = pathlib.Path(args.taxonomy)
    doc = load_taxonomy(taxonomy_path)
    computed = content_hash(doc)
    declared = str(doc.get("content_hash") or "")

    if args.update_hash and declared != computed:
        text = taxonomy_path.read_text(encoding="utf-8")
        new_text, n = re.subn(
            r"^content_hash:.*$", f"content_hash: {computed}", text, count=1, flags=re.M
        )
        if n != 1:
            raise SystemExit(f"{taxonomy_path}: could not find a content_hash line to update")
        taxonomy_path.write_text(new_text, encoding="utf-8", newline="\n")
        print(f"updated content_hash: {declared or '<missing>'} -> {computed}")
        doc["content_hash"] = computed
        declared = computed

    if declared != computed:
        raise SystemExit(
            f"{taxonomy_path}: content_hash is stale\n"
            f"  declared: {declared or '<missing>'}\n"
            f"  computed: {computed}\n"
            f"  fix with: python3 scripts/generate_taxonomy_embeddings.py --update-hash"
        )

    labels = build_labels(doc)
    print(f"{taxonomy_path.name}: {len(labels)} labels, content_hash {computed}")
    if args.print_labels:
        for label in labels:
            print(f"  {label['id']:<28} {label['text']}")
        return 0

    tier = TIERS[args.tier]
    onnx_revision = resolve_revision(tier["onnx_repo"])
    calibration_revision = resolve_revision(tier["calibration_repo"])
    print(f"tier {args.tier}: {tier['onnx_repo']}@{onnx_revision}")
    print(f"calibration: {tier['calibration_repo']}@{calibration_revision}")

    calibration = fetch_calibration(tier["calibration_repo"], calibration_revision)
    print(
        "sigmoid calibration: logit_scale_raw={logit_scale_raw!r} "
        "logit_scale={logit_scale!r} logit_bias={logit_bias!r}".format(**calibration)
    )

    vectors = embed_texts(
        [label["text"] for label in labels],
        tier["onnx_repo"],
        onnx_revision,
        tier["text_file"],
        tier["text_extra_files"],
    )
    artifact = build_artifact(
        doc, labels, vectors, calibration, args.tier, tier, onnx_revision, calibration_revision
    )

    if args.out:
        out_path = pathlib.Path(args.out)
    else:
        out_path = taxonomy_path.with_name(
            f"{taxonomy_path.stem}{tier['artifact_suffix']}.embeddings.json"
        )
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(artifact))
    tmp_path.replace(out_path)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(
        f"wrote {out_path}: {artifact['label_count']} labels x "
        f"{artifact['model']['embed_dim']} dims ({size_mb:.2f} MB)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
