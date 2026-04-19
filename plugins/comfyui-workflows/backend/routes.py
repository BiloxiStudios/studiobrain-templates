"""
ComfyUI Workflow Manager Plugin -- backend routes.

Provides endpoints for browsing workflows, queueing executions on ComfyUI,
tracking execution history, and serving generated outputs.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiohttp
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from services.plugin_data_service import PluginDataService

logger = logging.getLogger("plugin.comfyui-workflows")

router = APIRouter()

data_svc = PluginDataService("comfyui-workflows")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
OUTPUTS_DIR = DATA_DIR / "outputs"
WORKFLOW_CACHE_FILE = DATA_DIR / "workflow_cache.json"

BACKEND_URL = "http://localhost:8201"
DEFAULT_COMFYUI_URL = "http://localhost:8188"
DEFAULT_WORKFLOWS_DIR = r"A:\Brains\Workflows"


def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------
def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("comfyui-workflows").get(key, default)


def _comfyui_url() -> str:
    return _get_setting("comfyui_url", DEFAULT_COMFYUI_URL).rstrip("/")


def _workflows_dir() -> Path:
    d = _get_setting("workflows_dir", DEFAULT_WORKFLOWS_DIR)
    return Path(d) if d else Path(DEFAULT_WORKFLOWS_DIR)


# ---------------------------------------------------------------------------
# ComfyUI workflow parser
# ---------------------------------------------------------------------------
def _parse_workflow(filepath: Path) -> dict:
    """Parse a ComfyUI workflow JSON file and extract metadata."""
    try:
        raw = json.loads(filepath.read_text(encoding="utf-8"))
    except Exception as e:
        return {
            "id": filepath.stem,
            "filename": filepath.name,
            "path": str(filepath),
            "error": str(e),
        }

    # Detect inputs: nodes whose _meta.title starts with "INPUT_"
    inputs = []
    node_types = set()
    node_count = 0

    for node_id, node_data in raw.items():
        if not isinstance(node_data, dict):
            continue
        node_count += 1
        class_type = node_data.get("class_type", "")
        node_types.add(class_type)
        meta_title = node_data.get("_meta", {}).get("title", "")

        if meta_title.startswith("INPUT_"):
            input_name = meta_title[6:]  # Strip "INPUT_" prefix
            # Determine type from class_type
            input_type = "string"
            if "Int" in class_type or "Seed" in class_type:
                input_type = "integer"
            elif "Float" in class_type:
                input_type = "float"
            elif "Bool" in class_type:
                input_type = "boolean"
            elif "Image" in class_type or "LoadImage" in class_type:
                input_type = "image"
            elif "Multiline" in class_type:
                input_type = "text"

            # Get current/default value
            default_value = node_data.get("inputs", {}).get("value", "")
            if input_type == "image":
                default_value = node_data.get("inputs", {}).get("image", "")

            inputs.append({
                "node_id": node_id,
                "name": input_name,
                "type": input_type,
                "class_type": class_type,
                "default_value": default_value,
                "meta_title": meta_title,
            })

    # Detect category from filename patterns
    fname_lower = filepath.stem.lower()
    category = "general"
    if "character" in fname_lower or "face" in fname_lower or "portrait" in fname_lower:
        category = "character"
    elif "background" in fname_lower or "bg" in fname_lower:
        category = "background"
    elif "upscale" in fname_lower:
        category = "upscale"
    elif "hand" in fname_lower:
        category = "detail"
    elif "mouth" in fname_lower or "viseme" in fname_lower:
        category = "animation"
    elif "emoji" in fname_lower or "animated" in fname_lower:
        category = "animation"
    elif "inpaint" in fname_lower or "edit" in fname_lower:
        category = "editing"
    elif "logo" in fname_lower:
        category = "design"
    elif "pose" in fname_lower:
        category = "posing"
    elif "descri" in fname_lower:
        category = "utility"

    # Detect key features from node types
    features = []
    if any("Flux" in t for t in node_types):
        features.append("Flux")
    if any("SDXL" in t for t in node_types):
        features.append("SDXL")
    if any("ControlNet" in t for t in node_types):
        features.append("ControlNet")
    if any("Lora" in t.lower() for t in node_types):
        features.append("LoRA")
    if any("IPAdapter" in t for t in node_types):
        features.append("IPAdapter")
    if any("Upscale" in t for t in node_types):
        features.append("Upscale")
    if any("VAE" in t for t in node_types):
        features.append("VAE")
    if any("CLIP" in t for t in node_types):
        features.append("CLIP")
    if any("Qwen" in t for t in node_types):
        features.append("Qwen")

    # Check for thumbnail in same directory (workflow image)
    thumbnail = None
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        thumb_path = filepath.with_suffix(ext)
        if thumb_path.exists():
            thumbnail = str(thumb_path)
            break

    # File stats
    stat = filepath.stat()

    return {
        "id": filepath.stem,
        "filename": filepath.name,
        "path": str(filepath),
        "category": category,
        "node_count": node_count,
        "inputs": inputs,
        "features": features,
        "thumbnail": thumbnail,
        "file_size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# ComfyUI communication helpers
# ---------------------------------------------------------------------------
async def _comfyui_get(path: str) -> dict:
    """GET request to ComfyUI server."""
    url = f"{_comfyui_url()}{path}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"ComfyUI returned {resp.status}"}
    except aiohttp.ClientError as e:
        return {"error": f"Cannot connect to ComfyUI: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


async def _comfyui_post(path: str, data: dict) -> dict:
    """POST request to ComfyUI server."""
    url = f"{_comfyui_url()}{path}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    return await resp.json()
                body = await resp.text()
                return {"error": f"ComfyUI returned {resp.status}: {body}"}
    except aiohttp.ClientError as e:
        return {"error": f"Cannot connect to ComfyUI: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


async def _check_comfyui_connection(url: Optional[str] = None) -> dict:
    """Check if ComfyUI is reachable.

    Args:
        url: Optional override URL to test. Defaults to the configured comfyui_url.
    """
    base_url = url.rstrip("/") if url else _comfyui_url()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/system_stats",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return {
                        "connected": False,
                        "url": base_url,
                        "error": f"ComfyUI returned HTTP {resp.status}",
                    }
                stats = await resp.json()

        # Extract version info when present
        system = stats.get("system", {})
        python_version = system.get("python_version", "")
        comfyui_version = stats.get("version") or system.get("comfyui_version", "")

        return {
            "connected": True,
            "url": base_url,
            "version": comfyui_version or None,
            "python_version": python_version or None,
            "system_stats": stats,
        }
    except aiohttp.ClientError:
        return {"connected": False, "url": base_url, "error": f"Cannot reach ComfyUI at {base_url}"}
    except Exception as exc:
        logger.exception("Unexpected error checking ComfyUI connection at %s", base_url)
        return {"connected": False, "url": base_url, "error": f"Unexpected error: {type(exc).__name__}"}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ExecuteRequest(BaseModel):
    workflow_id: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    input_overrides: Optional[dict] = None


class ImportURLRequest(BaseModel):
    url: str
    filename: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/")
async def status():
    """Plugin status and ComfyUI connection check."""
    comfyui_status = await _check_comfyui_connection()
    workflows_dir = _workflows_dir()

    workflow_count = 0
    if workflows_dir.exists():
        workflow_count = sum(1 for f in workflows_dir.glob("*.json") if f.is_file())

    hist_result = data_svc.list(record_type="execution", limit=1)

    return {
        "plugin": "comfyui-workflows",
        "version": "0.2.0",
        "status": "ok",
        "comfyui": comfyui_status,
        "comfyui_url": _comfyui_url(),
        "workflows_dir": str(workflows_dir),
        "workflow_count": workflow_count,
        "total_executions": hist_result["total"],
    }


@router.get("/connect")
async def connect(url: Optional[str] = None):
    """Test connectivity to the ComfyUI server.

    Called by the SchemaForm provider button so the user can verify their
    ComfyUI URL setting without executing a full workflow.

    Query params:
        url: Override URL to test (e.g. the value the user just typed).
             Falls back to the saved ``comfyui_url`` setting when omitted.

    Returns a JSON object with at minimum:
        connected (bool)   – whether ComfyUI responded successfully
        url       (str)    – the URL that was tested
        error     (str?)   – human-readable error message when connected=false
        version   (str?)   – ComfyUI version string when connected=true
    """
    return await _check_comfyui_connection(url=url)


@router.get("/workflows")
async def list_workflows(category: Optional[str] = None, search: Optional[str] = None):
    """List available workflows from the workflows directory."""
    workflows_dir = _workflows_dir()

    if not workflows_dir.exists():
        return {"workflows": [], "error": f"Workflows directory not found: {workflows_dir}"}

    workflows = []
    for filepath in sorted(workflows_dir.glob("*.json")):
        if not filepath.is_file():
            continue
        wf = _parse_workflow(filepath)
        if "error" in wf:
            continue

        # Filter by category
        if category and wf.get("category") != category:
            continue

        # Filter by search
        if search:
            search_lower = search.lower()
            if search_lower not in wf["id"].lower() and search_lower not in wf["filename"].lower():
                # Also search features
                if not any(search_lower in f.lower() for f in wf.get("features", [])):
                    continue

        workflows.append(wf)

    # Collect categories
    categories = sorted(set(wf["category"] for wf in workflows))

    return {
        "workflows": workflows,
        "total": len(workflows),
        "categories": categories,
        "workflows_dir": str(workflows_dir),
    }


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get detailed information about a specific workflow."""
    workflows_dir = _workflows_dir()
    filepath = workflows_dir / f"{workflow_id}.json"

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")

    wf = _parse_workflow(filepath)

    # Also load raw JSON for the full node graph
    try:
        raw = json.loads(filepath.read_text(encoding="utf-8"))
        wf["raw_workflow"] = raw
    except Exception:
        pass

    return wf


@router.post("/import")
async def import_workflow(
    url: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """Import a workflow from a URL or uploaded file."""
    workflows_dir = _workflows_dir()
    workflows_dir.mkdir(parents=True, exist_ok=True)

    if file:
        # Upload a workflow file directly
        content = await file.read()
        try:
            workflow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")

        save_name = filename or file.filename or f"imported_{uuid.uuid4().hex[:8]}.json"
        if not save_name.endswith(".json"):
            save_name += ".json"

        dest = workflows_dir / save_name
        dest.write_text(json.dumps(workflow_data, indent=2), encoding="utf-8")

        return {
            "success": True,
            "message": f"Workflow imported as {save_name}",
            "workflow_id": dest.stem,
            "path": str(dest),
        }

    elif url:
        # Download from URL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {resp.status}")
                    content = await resp.text()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {str(e)}")

        try:
            workflow_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="URL did not return valid JSON")

        # Generate filename
        if not filename:
            # Try to extract from URL
            url_path = url.split("?")[0].split("/")[-1]
            if url_path.endswith(".json"):
                filename = url_path
            else:
                filename = f"imported_{uuid.uuid4().hex[:8]}.json"
        if not filename.endswith(".json"):
            filename += ".json"

        dest = workflows_dir / filename
        dest.write_text(json.dumps(workflow_data, indent=2), encoding="utf-8")

        return {
            "success": True,
            "message": f"Workflow imported from URL as {filename}",
            "workflow_id": dest.stem,
            "path": str(dest),
            "source_url": url,
        }

    else:
        raise HTTPException(status_code=400, detail="Provide either a file upload or a URL")


@router.post("/execute")
async def execute_workflow(req: ExecuteRequest):
    """Queue a workflow execution on ComfyUI."""
    workflows_dir = _workflows_dir()
    filepath = workflows_dir / f"{req.workflow_id}.json"

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Workflow not found: {req.workflow_id}")

    # Load workflow
    try:
        workflow = json.loads(filepath.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load workflow: {str(e)}")

    # If entity is specified, fetch entity data for mapping
    entity_data = None
    if req.entity_type and req.entity_id:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BACKEND_URL}/api/entity/{req.entity_type}/{req.entity_id}",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        entity_data = await resp.json()
        except Exception as e:
            logger.warning("Failed to fetch entity data: %s", e)

    # Apply input overrides to the workflow
    if req.input_overrides:
        for node_id, node_data in workflow.items():
            if not isinstance(node_data, dict):
                continue
            meta_title = node_data.get("_meta", {}).get("title", "")
            if meta_title.startswith("INPUT_"):
                input_name = meta_title[6:]
                if input_name in req.input_overrides:
                    value = req.input_overrides[input_name]
                    class_type = node_data.get("class_type", "")
                    if "Image" in class_type or "LoadImage" in class_type:
                        node_data["inputs"]["image"] = value
                    else:
                        node_data["inputs"]["value"] = value

    # Auto-map entity data to known inputs if no explicit override
    if entity_data and req.input_overrides is None:
        for node_id, node_data in workflow.items():
            if not isinstance(node_data, dict):
                continue
            meta_title = node_data.get("_meta", {}).get("title", "")
            if meta_title == "INPUT_prompt":
                desc = entity_data.get("description") or entity_data.get("visual_description") or ""
                if desc:
                    node_data["inputs"]["value"] = desc
            elif meta_title == "INPUT_character_id":
                eid = req.entity_id or ""
                node_data["inputs"]["value"] = eid
            elif meta_title == "INPUT_Seed":
                # Randomize seed
                import random
                node_data["inputs"]["value"] = random.randint(1, 2**52)

    # Generate a client_id for tracking
    client_id = uuid.uuid4().hex

    # Queue on ComfyUI
    payload = {"prompt": workflow, "client_id": client_id}
    result = await _comfyui_post("/prompt", payload)

    if "error" in result:
        # Save failed execution to history
        history_entry = {
            "id": str(uuid.uuid4()),
            "workflow_id": req.workflow_id,
            "entity_type": req.entity_type,
            "entity_id": req.entity_id,
            "client_id": client_id,
            "status": "error",
            "error": result["error"],
            "queued_at": datetime.now(timezone.utc).isoformat(),
        }
        data_svc.create(
            record_type="execution",
            data=history_entry,
            entity_type=req.entity_type,
            entity_id=req.entity_id,
            record_id=history_entry["id"],
        )
        raise HTTPException(status_code=502, detail=result["error"])

    prompt_id = result.get("prompt_id", "unknown")

    # Save to history
    history_entry = {
        "id": str(uuid.uuid4()),
        "workflow_id": req.workflow_id,
        "workflow_name": req.workflow_id.replace("_", " "),
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "entity_name": entity_data.get("name", "") if entity_data else None,
        "client_id": client_id,
        "prompt_id": prompt_id,
        "status": "queued",
        "input_overrides": req.input_overrides,
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    data_svc.create(
        record_type="execution",
        data=history_entry,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
        record_id=history_entry["id"],
    )

    return {
        "success": True,
        "prompt_id": prompt_id,
        "client_id": client_id,
        "history_id": history_entry["id"],
        "message": f"Workflow '{req.workflow_id}' queued on ComfyUI",
    }


@router.get("/queue")
async def get_queue():
    """Get current ComfyUI execution queue."""
    result = await _comfyui_get("/queue")
    if "error" in result:
        return {"running": [], "pending": [], "error": result["error"]}

    running = result.get("queue_running", [])
    pending = result.get("queue_pending", [])

    return {
        "running": len(running),
        "pending": len(pending),
        "running_details": running,
        "pending_details": pending,
    }


@router.get("/history")
async def get_history(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    limit: int = 50,
):
    """Get execution history, optionally filtered."""
    result = data_svc.list(
        record_type="execution",
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit if not workflow_id else 5000,
    )
    items = [r["data"] for r in result["records"]]

    if workflow_id:
        items = [h for h in items if h.get("workflow_id") == workflow_id]

    return {"total": len(items), "items": items[:limit]}


@router.get("/outputs/{entity_type}/{entity_id}")
async def get_outputs(entity_type: str, entity_id: str):
    """Get generated outputs for a specific entity."""
    entity_output_dir = OUTPUTS_DIR / entity_type / entity_id
    outputs = []

    if entity_output_dir.exists():
        for f in sorted(entity_output_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                outputs.append({
                    "filename": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        f.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                })

    # Also check ComfyUI history for this entity
    hist_result = data_svc.list(
        record_type="execution",
        entity_type=entity_type,
        entity_id=entity_id,
        limit=10000,
    )
    entity_history = [r["data"] for r in hist_result["records"]]

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "outputs": outputs,
        "execution_count": len(entity_history),
    }


@router.get("/comfyui/history")
async def get_comfyui_history(limit: int = 20):
    """Get recent execution history from ComfyUI itself."""
    result = await _comfyui_get("/history")
    if "error" in result:
        return {"items": [], "error": result["error"]}

    # ComfyUI returns {prompt_id: {status, outputs, ...}, ...}
    items = []
    for prompt_id, data in list(result.items())[:limit]:
        status_data = data.get("status", {})
        outputs_data = data.get("outputs", {})

        # Collect output images
        images = []
        for node_id, node_output in outputs_data.items():
            for img in node_output.get("images", []):
                images.append({
                    "filename": img.get("filename"),
                    "subfolder": img.get("subfolder", ""),
                    "type": img.get("type", "output"),
                })

        items.append({
            "prompt_id": prompt_id,
            "status": status_data.get("status_str", "unknown"),
            "completed": status_data.get("completed", False),
            "image_count": len(images),
            "images": images,
        })

    return {"items": items}


@router.post("/migrate")
async def migrate_legacy_data():
    """One-time migration of execution_history.json to database."""
    legacy_file = DATA_DIR / "execution_history.json"
    if not legacy_file.exists():
        return {"migrated": 0, "message": "No legacy data found"}
    count = data_svc.import_from_json(str(legacy_file))
    return {"migrated": count, "message": f"Migrated {count} records"}


@router.get("/comfyui/view")
async def view_comfyui_image(filename: str, subfolder: str = "", type: str = "output"):
    """Proxy an image from ComfyUI's output directory."""
    from fastapi.responses import StreamingResponse
    import io

    url = f"{_comfyui_url()}/view?filename={filename}&subfolder={subfolder}&type={type}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=resp.status, detail="Failed to fetch image from ComfyUI")
                content = await resp.read()
                content_type = resp.headers.get("Content-Type", "image/png")
                return StreamingResponse(io.BytesIO(content), media_type=content_type)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Cannot connect to ComfyUI: {str(e)}")
