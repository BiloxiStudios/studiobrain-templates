"""
LoRA Training Manager Plugin -- backend routes.

Provides API endpoints for managing LoRA training datasets, queuing
training jobs, tracking progress, and browsing completed LoRA files
linked to character entities.
"""

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("plugin.lora-trainer")

router = APIRouter()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BRAINS_ROOT = Path("A:/Brains")
PLUGIN_DIR = Path(__file__).resolve().parent.parent
PLUGIN_DATA = PLUGIN_DIR / "data"
JOBS_FILE = PLUGIN_DATA / "training_jobs.json"
LORA_INDEX_FILE = PLUGIN_DATA / "lora_index.json"
CAPTIONS_DIR = PLUGIN_DATA / "captions"

PLUGIN_DATA.mkdir(parents=True, exist_ok=True)
CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)

BACKEND_URL = "http://localhost:8201"

# Supported training image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------
def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("lora-trainer").get(key, default)


def _output_dir() -> Path:
    """Return the configured LoRA output directory, creating it if needed."""
    p = Path(_get_setting("output_dir", "A:/Brains/_Generated/loras"))
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------------------
# Entity helpers
# ---------------------------------------------------------------------------

def _entity_dir(entity_type: str, entity_id: str) -> Path:
    """Return the root directory for an entity."""
    type_folder = entity_type.rstrip("s") + "s"
    type_folder = type_folder[0].upper() + type_folder[1:]
    return BRAINS_ROOT / type_folder / entity_id


def _entity_assets_dir(entity_type: str, entity_id: str) -> Path:
    """Return the assets directory for an entity."""
    return _entity_dir(entity_type, entity_id) / "assets"


def _parse_frontmatter(filepath: Path) -> dict:
    """Read a markdown file and extract YAML frontmatter as a dict."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    try:
        import yaml
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        data = {}
        for line in match.group(1).split("\n"):
            if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                key, _, val = line.partition(":")
                data[key.strip()] = val.strip().strip("'\"")
        return data


def _get_entity_metadata(entity_type: str, entity_id: str) -> dict:
    """Try to load entity metadata from its markdown file."""
    edir = _entity_dir(entity_type, entity_id)
    if not edir.is_dir():
        return {}

    type_prefix_map = {
        "character": "CH",
        "location": "LOC",
        "item": "ITEM",
        "faction": "FAC",
        "brand": "BR",
        "district": "DIST",
        "job": "JOB",
    }
    prefix = type_prefix_map.get(entity_type, entity_type.upper())
    md_file = edir / f"{prefix}_{entity_id}.md"
    if md_file.is_file():
        return _parse_frontmatter(md_file)

    # Fallback: look for any .md file
    for f in edir.glob("*.md"):
        fm = _parse_frontmatter(f)
        if fm:
            return fm
    return {}


# ---------------------------------------------------------------------------
# Job persistence
# ---------------------------------------------------------------------------

def _load_jobs() -> list[dict]:
    try:
        if JOBS_FILE.exists():
            return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_jobs(jobs: list[dict]):
    PLUGIN_DATA.mkdir(parents=True, exist_ok=True)
    JOBS_FILE.write_text(json.dumps(jobs, indent=2, default=str), encoding="utf-8")


def _find_job(job_id: str) -> Optional[dict]:
    jobs = _load_jobs()
    for j in jobs:
        if j["id"] == job_id:
            return j
    return None


def _update_job(job_id: str, updates: dict):
    jobs = _load_jobs()
    for j in jobs:
        if j["id"] == job_id:
            j.update(updates)
            break
    _save_jobs(jobs)


# ---------------------------------------------------------------------------
# LoRA index persistence
# ---------------------------------------------------------------------------

def _load_lora_index() -> list[dict]:
    try:
        if LORA_INDEX_FILE.exists():
            return json.loads(LORA_INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_lora_index(index: list[dict]):
    LORA_INDEX_FILE.write_text(json.dumps(index, indent=2, default=str), encoding="utf-8")


def _scan_lora_files() -> list[dict]:
    """Scan the output directory for .safetensors files and merge with index."""
    output = _output_dir()
    existing_index = {e["filename"]: e for e in _load_lora_index()}
    found = []

    if output.is_dir():
        for f in output.rglob("*.safetensors"):
            stat = f.stat()
            entry = existing_index.get(f.name, {})
            found.append({
                "filename": f.name,
                "filepath": str(f),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 1),
                "created": entry.get("created", datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()),
                "entity_type": entry.get("entity_type", ""),
                "entity_id": entry.get("entity_id", ""),
                "entity_name": entry.get("entity_name", ""),
                "job_id": entry.get("job_id", ""),
                "steps": entry.get("steps", 0),
                "rank": entry.get("rank", 0),
                "trigger_word": entry.get("trigger_word", ""),
            })

    found.sort(key=lambda x: x.get("created", ""), reverse=True)
    return found


# ---------------------------------------------------------------------------
# Caption helpers
# ---------------------------------------------------------------------------

def _caption_file_for(entity_type: str, entity_id: str, image_name: str) -> Path:
    """Return the path for a caption file associated with a training image."""
    safe_dir = CAPTIONS_DIR / f"{entity_type}_{entity_id}"
    safe_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(image_name).stem
    return safe_dir / f"{stem}.txt"


def _get_caption(entity_type: str, entity_id: str, image_name: str) -> str:
    """Load caption for an image, or return empty string."""
    cf = _caption_file_for(entity_type, entity_id, image_name)
    if cf.exists():
        return cf.read_text(encoding="utf-8").strip()
    return ""


def _set_caption(entity_type: str, entity_id: str, image_name: str, caption: str):
    """Save caption for an image."""
    cf = _caption_file_for(entity_type, entity_id, image_name)
    cf.write_text(caption.strip(), encoding="utf-8")


def _generate_caption_from_metadata(metadata: dict, entity_type: str, entity_id: str) -> str:
    """Build a training caption string from entity metadata."""
    parts = []

    # Trigger word
    trigger = entity_id.replace("_", " ").replace("-", " ")
    name = metadata.get("name") or metadata.get("character_name") or trigger
    parts.append(name)

    # Descriptive fields
    desc_fields = [
        "race", "gender", "age", "hair_color", "eye_color",
        "body_type", "skin_tone", "distinguishing_features",
        "clothing_style", "aesthetic", "archetype",
    ]
    for field in desc_fields:
        val = metadata.get(field)
        if val and isinstance(val, str) and val.strip():
            parts.append(val.strip())

    # Short description
    desc = metadata.get("appearance") or metadata.get("physical_description") or metadata.get("description")
    if desc and isinstance(desc, str):
        # Take first sentence or first 200 chars
        first_sentence = desc.split(".")[0].strip()
        if len(first_sentence) > 200:
            first_sentence = first_sentence[:197] + "..."
        if first_sentence:
            parts.append(first_sentence)

    # Tags
    tags = metadata.get("tags") or metadata.get("visual_tags")
    if isinstance(tags, list):
        parts.extend([t.strip() for t in tags if isinstance(t, str)])
    elif isinstance(tags, str):
        parts.extend([t.strip() for t in tags.split(",") if t.strip()])

    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TrainRequest(BaseModel):
    entity_type: str = "character"
    entity_id: str
    config: dict = Field(default_factory=lambda: {})


class CaptionUpdate(BaseModel):
    image_name: str
    caption: str


class CaptionBulkUpdate(BaseModel):
    captions: list[CaptionUpdate]


# ---------------------------------------------------------------------------
# Mock training progress simulation
# ---------------------------------------------------------------------------

def _simulate_progress(job: dict) -> dict:
    """
    Simulate training progress based on elapsed time since job was queued.
    In production this would read from the actual training process.
    """
    if job["status"] in ("completed", "failed", "cancelled"):
        return job

    created_ts = job.get("created_ts", time.time())
    elapsed = time.time() - created_ts
    total_steps = job.get("config", {}).get("steps", 1500)

    # Simulate roughly 2 steps/second for mock progress
    steps_per_sec = 2.0
    simulated_steps = int(elapsed * steps_per_sec)

    if job["status"] == "pending":
        # Move to training after 5 seconds
        if elapsed > 5:
            job["status"] = "training"
            job["started_at"] = datetime.fromtimestamp(created_ts + 5, tz=timezone.utc).isoformat()
        return job

    if job["status"] == "training":
        current_step = min(simulated_steps, total_steps)
        progress = round((current_step / total_steps) * 100, 1)
        job["current_step"] = current_step
        job["progress"] = progress

        # Estimate remaining time
        if current_step > 0:
            elapsed_training = elapsed - 5  # subtract pending time
            rate = current_step / max(elapsed_training, 1)
            remaining_steps = total_steps - current_step
            eta_seconds = int(remaining_steps / max(rate, 0.01))
            job["eta_seconds"] = eta_seconds
            job["steps_per_sec"] = round(rate, 1)

        # Complete after all steps done
        if current_step >= total_steps:
            job["status"] = "completed"
            job["progress"] = 100.0
            job["current_step"] = total_steps
            job["completed_at"] = datetime.now(timezone.utc).isoformat()
            job["eta_seconds"] = 0

            # Register the mock output LoRA
            output_name = f"lora_{job['entity_id']}_{job['id'][:8]}.safetensors"
            job["output_file"] = output_name

    return job


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def plugin_status():
    """Plugin health check with training queue summary."""
    jobs = _load_jobs()
    loras = _scan_lora_files()

    pending = sum(1 for j in jobs if j["status"] == "pending")
    training = sum(1 for j in jobs if j["status"] == "training")
    completed = sum(1 for j in jobs if j["status"] == "completed")
    failed = sum(1 for j in jobs if j["status"] == "failed")

    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("lora-trainer")
    return {
        "plugin": "lora-trainer",
        "version": "0.2.0",
        "status": "ok",
        "kohya_configured": bool(settings.get("kohya_path")),
        "output_dir": str(_output_dir()),
        "queue": {
            "pending": pending,
            "training": training,
            "completed": completed,
            "failed": failed,
            "total": len(jobs),
        },
        "loras_available": len(loras),
        "gpu_id": settings.get("gpu_id", 0),
    }


@router.get("/datasets/{entity_type}/{entity_id}")
async def list_dataset_images(entity_type: str, entity_id: str):
    """List images in entity assets directory suitable for LoRA training."""
    assets_dir = _entity_assets_dir(entity_type, entity_id)

    if not assets_dir.is_dir():
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "images": [],
            "total": 0,
            "message": "Assets directory not found",
        }

    images = []
    for f in sorted(assets_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            stat = f.stat()
            caption = _get_caption(entity_type, entity_id, f.name)

            # Build accessible URL
            type_folder = entity_type.rstrip("s") + "s"
            type_folder = type_folder[0].upper() + type_folder[1:]

            images.append({
                "filename": f.name,
                "url": f"{BACKEND_URL}/files/{type_folder}/{entity_id}/assets/{f.name}",
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "caption": caption,
                "has_caption": bool(caption),
            })

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "assets_dir": str(assets_dir),
        "images": images,
        "total": len(images),
        "captioned": sum(1 for img in images if img["has_caption"]),
    }


@router.post("/datasets/{entity_type}/{entity_id}/prepare")
async def prepare_dataset(entity_type: str, entity_id: str):
    """
    Prepare training dataset by auto-generating captions from entity metadata.
    Creates .txt caption files alongside the training images.
    """
    assets_dir = _entity_assets_dir(entity_type, entity_id)
    if not assets_dir.is_dir():
        raise HTTPException(status_code=404, detail="Assets directory not found for this entity")

    # Load entity metadata
    metadata = _get_entity_metadata(entity_type, entity_id)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Could not load entity metadata. Ensure the entity markdown file exists.",
        )

    # Generate base caption from metadata
    base_caption = _generate_caption_from_metadata(metadata, entity_type, entity_id)

    # Apply caption to all images that don't already have one
    captioned = 0
    skipped = 0
    image_files = [
        f for f in sorted(assets_dir.iterdir())
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    for img_file in image_files:
        existing = _get_caption(entity_type, entity_id, img_file.name)
        if existing:
            skipped += 1
            continue
        _set_caption(entity_type, entity_id, img_file.name, base_caption)
        captioned += 1

    entity_name = (
        metadata.get("name")
        or metadata.get("character_name")
        or entity_id.replace("_", " ").title()
    )

    return {
        "success": True,
        "entity_name": entity_name,
        "base_caption": base_caption,
        "images_found": len(image_files),
        "captioned": captioned,
        "skipped_existing": skipped,
        "trigger_word": entity_id.replace("_", " ").replace("-", " "),
    }


@router.post("/datasets/{entity_type}/{entity_id}/captions")
async def update_captions(entity_type: str, entity_id: str, body: CaptionBulkUpdate):
    """Update captions for multiple images at once."""
    updated = 0
    for item in body.captions:
        _set_caption(entity_type, entity_id, item.image_name, item.caption)
        updated += 1

    return {"success": True, "updated": updated}


@router.post("/train")
async def queue_training(req: TrainRequest):
    """Queue a new LoRA training job."""
    # Validate entity assets exist
    assets_dir = _entity_assets_dir(req.entity_type, req.entity_id)
    if not assets_dir.is_dir():
        raise HTTPException(status_code=404, detail="Entity assets directory not found")

    # Count trainable images
    image_count = sum(
        1 for f in assets_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )
    if image_count == 0:
        raise HTTPException(status_code=400, detail="No training images found in entity assets")

    # Merge config with defaults
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("lora-trainer")
    config = {
        "steps": req.config.get("steps", settings.get("default_steps", 1500)),
        "lr": req.config.get("lr", settings.get("default_lr", "1e-4")),
        "rank": req.config.get("rank", settings.get("default_rank", 32)),
        "resolution": req.config.get("resolution", 512),
        "batch_size": req.config.get("batch_size", 1),
        "network_alpha": req.config.get("network_alpha", req.config.get("rank", settings.get("default_rank", 32)) // 2),
        "optimizer": req.config.get("optimizer", "AdamW8bit"),
        "scheduler": req.config.get("scheduler", "cosine"),
        "gpu_id": settings.get("gpu_id", 0),
    }

    # Get entity name for display
    metadata = _get_entity_metadata(req.entity_type, req.entity_id)
    entity_name = (
        metadata.get("name")
        or metadata.get("character_name")
        or req.entity_id.replace("_", " ").title()
    )

    trigger_word = req.entity_id.replace("_", " ").replace("-", " ")

    now = datetime.now(timezone.utc)
    job = {
        "id": str(uuid.uuid4()),
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "entity_name": entity_name,
        "trigger_word": trigger_word,
        "config": config,
        "image_count": image_count,
        "status": "pending",
        "progress": 0.0,
        "current_step": 0,
        "eta_seconds": None,
        "steps_per_sec": None,
        "output_file": None,
        "error": None,
        "created_at": now.isoformat(),
        "created_ts": time.time(),
        "started_at": None,
        "completed_at": None,
    }

    jobs = _load_jobs()
    jobs.insert(0, job)
    _save_jobs(jobs)

    logger.info(
        "Queued LoRA training job %s for %s/%s (%d images, %d steps)",
        job["id"], req.entity_type, req.entity_id, image_count, config["steps"],
    )

    return {
        "success": True,
        "job_id": job["id"],
        "message": f"Training job queued for {entity_name}",
        "config": config,
        "image_count": image_count,
    }


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    """List all training jobs with simulated progress."""
    jobs = _load_jobs()

    # Simulate progress for active jobs
    for j in jobs:
        if j["status"] in ("pending", "training"):
            _simulate_progress(j)
    _save_jobs(jobs)

    # Apply filters
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    if entity_id:
        jobs = [j for j in jobs if j.get("entity_id") == entity_id]

    return {
        "jobs": jobs[:limit],
        "total": len(jobs),
    }


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get details and progress for a specific training job."""
    job = _find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")

    # Simulate progress
    if job["status"] in ("pending", "training"):
        job = _simulate_progress(job)
        _update_job(job_id, job)

    return job


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending or training job."""
    job = _find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")

    if job["status"] in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status: {job['status']}")

    _update_job(job_id, {
        "status": "cancelled",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "error": "Cancelled by user",
    })

    logger.info("Cancelled training job %s", job_id)
    return {"success": True, "message": "Training job cancelled"}


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Remove a job from the queue history."""
    jobs = _load_jobs()
    original_count = len(jobs)
    jobs = [j for j in jobs if j["id"] != job_id]

    if len(jobs) == original_count:
        raise HTTPException(status_code=404, detail="Training job not found")

    _save_jobs(jobs)
    logger.info("Deleted training job %s", job_id)
    return {"success": True, "message": "Training job removed from history"}


@router.get("/loras")
async def list_loras():
    """List all completed LoRA files in the output directory."""
    loras = _scan_lora_files()
    return {
        "loras": loras,
        "total": len(loras),
        "output_dir": str(_output_dir()),
    }


@router.get("/loras/{entity_type}/{entity_id}")
async def get_entity_loras(entity_type: str, entity_id: str):
    """List LoRA files linked to a specific entity."""
    all_loras = _scan_lora_files()
    entity_loras = [l for l in all_loras if l.get("entity_id") == entity_id]

    # Also check completed jobs for this entity
    jobs = _load_jobs()
    completed_jobs = [
        j for j in jobs
        if j.get("entity_id") == entity_id and j["status"] == "completed"
    ]
    active_jobs = [
        j for j in jobs
        if j.get("entity_id") == entity_id and j["status"] in ("pending", "training")
    ]

    # Simulate progress on active jobs
    for j in active_jobs:
        _simulate_progress(j)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "loras": entity_loras,
        "completed_jobs": len(completed_jobs),
        "active_jobs": active_jobs,
        "has_lora": len(entity_loras) > 0 or len(completed_jobs) > 0,
    }


@router.get("/gpu-status")
async def gpu_status():
    """
    Return GPU status info. In production this would query nvidia-smi.
    Returns mock data for UI development.
    """
    gpu_id = _get_setting("gpu_id", 0)

    # Check if any jobs are currently training
    jobs = _load_jobs()
    active_job = None
    for j in jobs:
        if j["status"] == "training":
            active_job = _simulate_progress(j)
            break

    return {
        "gpu_id": gpu_id,
        "gpu_name": "NVIDIA RTX 4090",
        "vram_total_gb": 24.0,
        "vram_used_gb": 8.2 if active_job else 1.1,
        "vram_free_gb": 15.8 if active_job else 22.9,
        "utilization_pct": 85 if active_job else 3,
        "temperature_c": 72 if active_job else 38,
        "active_job": {
            "id": active_job["id"],
            "entity_name": active_job.get("entity_name", ""),
            "progress": active_job.get("progress", 0),
        } if active_job else None,
    }
