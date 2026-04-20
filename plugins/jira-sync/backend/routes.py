"""
Jira Sync Plugin -- Backend Routes.

Provides REST endpoints for two-way sync between Studio entities and Jira
issues.  All routes are mounted under ``/api/ext/jira-sync/`` by the plugin
loader.

When Jira credentials are not configured the endpoints return helpful mock
responses with setup instructions so the frontend can still render.
"""

import json
import logging

import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()
logger = logging.getLogger("plugin.jira-sync")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PLUGIN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PLUGIN_DIR / "data"
LINKS_FILE = DATA_DIR / "entity_links.json"
MAPPINGS_FILE = DATA_DIR / "field_mappings.json"

STUDIO_API = "http://localhost:8201/api"

# ---------------------------------------------------------------------------
# Helpers -- settings & persistence
# ---------------------------------------------------------------------------

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load_json(path: Path, default: Any = None) -> Any:
    _ensure_data_dir()
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}

def _save_json(path: Path, data: Any) -> None:
    _ensure_data_dir()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _load_links() -> Dict[str, Any]:
    return _load_json(LINKS_FILE, {})

def _save_links(links: Dict[str, Any]) -> None:
    _save_json(LINKS_FILE, links)

def _load_mappings() -> Dict[str, Any]:
    return _load_json(MAPPINGS_FILE, {"default": {"name": "summary", "description": "description", "production_status": "status"}})

def _save_mappings(mappings: Dict[str, Any]) -> None:
    _save_json(MAPPINGS_FILE, mappings)

def _link_key(entity_type: str, entity_id: str) -> str:
    return f"{entity_type}:{entity_id}"

# ---------------------------------------------------------------------------
# Helpers -- settings access
# ---------------------------------------------------------------------------

def _read_settings() -> Dict[str, Any]:
    """Read plugin settings from the global plugin-settings file."""
    settings_file = PLUGIN_DIR.parent / "_plugin_settings.json"
    all_settings = _load_json(settings_file, {})
    return all_settings.get("jira-sync", {})

def _jira_configured() -> bool:
    s = _read_settings()
    return bool(s.get("jira_instance_url") and s.get("jira_api_token"))

def _jira_headers() -> Dict[str, str]:
    s = _read_settings()
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _jira_auth() -> Optional[tuple]:
    s = _read_settings()
    email = s.get("jira_email", "")
    token = s.get("jira_api_token", "")
    if email and token:
        return (email, token)
    return None

def _jira_base_url() -> str:
    s = _read_settings()
    url = s.get("jira_instance_url", "").rstrip("/")
    return url

def _entity_type_to_issue_type(entity_type: str) -> str:
    s = _read_settings()
    mapping_raw = s.get("entity_type_mapping", '{"character":"Story","location":"Story","item":"Task","quest":"Epic","campaign":"Epic"}')
    try:
        mapping = json.loads(mapping_raw) if isinstance(mapping_raw, str) else mapping_raw
    except Exception:
        mapping = {}
    return mapping.get(entity_type, "Task")

def _status_mapping() -> Dict[str, str]:
    s = _read_settings()
    mapping_raw = s.get("status_field_mapping", '{"draft":"To Do","in_progress":"In Progress","review":"In Review","complete":"Done"}')
    try:
        return json.loads(mapping_raw) if isinstance(mapping_raw, str) else mapping_raw
    except Exception:
        return {}

def _default_labels() -> list:
    s = _read_settings()
    raw = s.get("labels", "city-of-brains,auto-created")
    return [l.strip() for l in raw.split(",") if l.strip()]

def _project_key() -> str:
    s = _read_settings()
    return s.get("default_project_key", "PROJ")

# ---------------------------------------------------------------------------
# Helpers -- Jira REST calls
# ---------------------------------------------------------------------------

async def _jira_request(method: str, path: str, **kwargs) -> httpx.Response:
    """Make an authenticated request to the Jira REST API."""
    url = f"{_jira_base_url()}/rest/api/3{path}"
    auth = _jira_auth()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method, url, headers=_jira_headers(), auth=auth, **kwargs
        )
    return resp

async def _fetch_entity(entity_type: str, entity_id: str) -> Dict[str, Any]:
    """Fetch an entity from the Studio backend."""
    url = f"{STUDIO_API}/entity/{entity_type}/{entity_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Entity {entity_type}/{entity_id} not found")
    return resp.json()

async def _create_jira_issue(entity: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
    """Create a Jira issue from a Studio entity."""
    issue_type = _entity_type_to_issue_type(entity_type)
    labels = _default_labels()
    s = _read_settings()

    fields: Dict[str, Any] = {
        "project": {"key": _project_key()},
        "summary": entity.get("name", entity.get("title", f"Untitled {entity_type}")),
        "issuetype": {"name": issue_type},
        "labels": labels + [f"entity:{entity_type}"],
    }

    if s.get("sync_description", False) and entity.get("description"):
        fields["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": entity.get("description", "")}],
                }
            ],
        }

    resp = await _jira_request("POST", "/issue", json={"fields": fields})
    if resp.status_code not in (200, 201):
        logger.error("Jira create failed: %s %s", resp.status_code, resp.text)
        raise HTTPException(status_code=502, detail=f"Jira API error: {resp.status_code} - {resp.text[:300]}")

    return resp.json()

async def _get_jira_issue(issue_key: str) -> Dict[str, Any]:
    """Fetch a Jira issue by key."""
    resp = await _jira_request("GET", f"/issue/{issue_key}")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Jira issue {issue_key} not found")
    return resp.json()

async def _transition_jira_issue(issue_key: str, target_status: str) -> bool:
    """Attempt to transition a Jira issue to the given status name."""
    # Get available transitions
    resp = await _jira_request("GET", f"/issue/{issue_key}/transitions")
    if resp.status_code != 200:
        return False

    transitions = resp.json().get("transitions", [])
    target = target_status.lower()
    match = None
    for t in transitions:
        if t.get("name", "").lower() == target or t.get("to", {}).get("name", "").lower() == target:
            match = t
            break

    if not match:
        logger.warning("No matching transition for status '%s' on %s", target_status, issue_key)
        return False

    resp = await _jira_request(
        "POST",
        f"/issue/{issue_key}/transitions",
        json={"transition": {"id": match["id"]}},
    )
    return resp.status_code == 204

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def root():
    """Plugin status + Jira connection check."""
    configured = _jira_configured()
    info: Dict[str, Any] = {
        "plugin": "jira-sync",
        "version": "0.1.0",
        "jira_configured": configured,
        "jira_url": _jira_base_url() if configured else None,
        "project_key": _project_key() if configured else None,
    }

    if configured:
        try:
            resp = await _jira_request("GET", "/myself")
            if resp.status_code == 200:
                user = resp.json()
                info["jira_connected"] = True
                info["jira_user"] = user.get("displayName", user.get("emailAddress", "unknown"))
            else:
                info["jira_connected"] = False
                info["jira_error"] = f"HTTP {resp.status_code}"
        except Exception as exc:
            info["jira_connected"] = False
            info["jira_error"] = str(exc)
    else:
        info["jira_connected"] = False
        info["setup_instructions"] = {
            "steps": [
                "Go to Settings > Plugins > Jira Sync",
                "Enter your Atlassian Cloud URL (e.g. https://yourstudio.atlassian.net)",
                "Enter your Jira account email",
                "Generate an API token at https://id.atlassian.com/manage-profile/security/api-tokens",
                "Enter the API token",
                "Set your default Jira project key",
            ]
        }

    return info

@router.get("/status")
async def sync_status():
    """Sync overview: counts of linked entities, sync errors, etc."""
    links = _load_links()
    settings = _read_settings()

    total_linked = len(links)
    by_type: Dict[str, int] = {}
    last_synced_ts = 0
    error_count = 0

    for key, data in links.items():
        etype = key.split(":")[0] if ":" in key else "unknown"
        by_type[etype] = by_type.get(etype, 0) + 1
        ts = data.get("last_synced", 0)
        if ts > last_synced_ts:
            last_synced_ts = ts
        if data.get("sync_error"):
            error_count += 1

    return {
        "total_linked": total_linked,
        "by_type": by_type,
        "last_synced": last_synced_ts if last_synced_ts > 0 else None,
        "error_count": error_count,
        "auto_create": settings.get("auto_create_on_entity", False),
        "auto_transition": settings.get("auto_transition_on_status", True),
        "jira_configured": _jira_configured(),
    }

# ---------------------------------------------------------------------------
# Sync entity <-> Jira
# ---------------------------------------------------------------------------

@router.post("/sync/{entity_type}/{entity_id}")
async def sync_entity(entity_type: str, entity_id: str):
    """Sync a single entity to Jira.  Creates issue if not yet linked, updates otherwise."""
    links = _load_links()
    key = _link_key(entity_type, entity_id)

    if not _jira_configured():
        return {
            "status": "not_configured",
            "message": "Jira credentials are not configured. Go to Settings > Plugins > Jira Sync to set up.",
            "mock": True,
            "issue_key": "DEMO-42",
            "issue_url": "https://yourstudio.atlassian.net/browse/DEMO-42",
        }

    # Fetch entity from Studio
    entity = await _fetch_entity(entity_type, entity_id)

    existing = links.get(key)
    if existing and existing.get("issue_key"):
        # Update existing issue
        issue_key = existing["issue_key"]
        try:
            update_fields: Dict[str, Any] = {
                "summary": entity.get("name", entity.get("title", "")),
            }
            settings = _read_settings()
            if settings.get("sync_description", False) and entity.get("description"):
                update_fields["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": entity.get("description", "")}]}
                    ],
                }

            resp = await _jira_request("PUT", f"/issue/{issue_key}", json={"fields": update_fields})
            if resp.status_code not in (200, 204):
                links[key]["sync_error"] = f"Update failed: HTTP {resp.status_code}"
                _save_links(links)
                raise HTTPException(status_code=502, detail=f"Jira update failed: {resp.status_code}")

            # Handle status transition
            if settings.get("auto_transition_on_status", True):
                prod_status = entity.get("production_status", "")
                sm = _status_mapping()
                if prod_status and prod_status in sm:
                    await _transition_jira_issue(issue_key, sm[prod_status])

            links[key]["last_synced"] = time.time()
            links[key].pop("sync_error", None)
            _save_links(links)

            return {
                "status": "updated",
                "issue_key": issue_key,
                "issue_url": f"{_jira_base_url()}/browse/{issue_key}",
                "last_synced": links[key]["last_synced"],
            }
        except HTTPException:
            raise
        except Exception as exc:
            links[key]["sync_error"] = str(exc)
            _save_links(links)
            raise HTTPException(status_code=502, detail=str(exc))
    else:
        # Create new issue
        try:
            result = await _create_jira_issue(entity, entity_type)
            issue_key = result.get("key", "")
            issue_id = result.get("id", "")
            links[key] = {
                "issue_key": issue_key,
                "issue_id": issue_id,
                "last_synced": time.time(),
                "created_at": time.time(),
            }
            _save_links(links)
            return {
                "status": "created",
                "issue_key": issue_key,
                "issue_id": issue_id,
                "issue_url": f"{_jira_base_url()}/browse/{issue_key}",
                "last_synced": links[key]["last_synced"],
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc))

# ---------------------------------------------------------------------------
# Link management
# ---------------------------------------------------------------------------

@router.get("/link/{entity_type}/{entity_id}")
async def get_link(entity_type: str, entity_id: str):
    """Get linked Jira issue info for an entity."""
    links = _load_links()
    key = _link_key(entity_type, entity_id)
    link = links.get(key)

    if not link:
        return {"linked": False, "entity_type": entity_type, "entity_id": entity_id}

    result: Dict[str, Any] = {
        "linked": True,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "issue_key": link.get("issue_key"),
        "issue_id": link.get("issue_id"),
        "last_synced": link.get("last_synced"),
        "created_at": link.get("created_at"),
        "sync_error": link.get("sync_error"),
        "issue_url": f"{_jira_base_url()}/browse/{link.get('issue_key')}" if _jira_configured() else None,
    }

    # Try to get fresh Jira data if configured
    if _jira_configured() and link.get("issue_key"):
        try:
            issue = await _get_jira_issue(link["issue_key"])
            fields = issue.get("fields", {})
            result["jira"] = {
                "summary": fields.get("summary", ""),
                "status": fields.get("status", {}).get("name", "Unknown"),
                "status_category": fields.get("status", {}).get("statusCategory", {}).get("key", ""),
                "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                "priority": fields.get("priority", {}).get("name", "None") if fields.get("priority") else "None",
                "issue_type": fields.get("issuetype", {}).get("name", ""),
                "labels": fields.get("labels", []),
                "created": fields.get("created", ""),
                "updated": fields.get("updated", ""),
            }
        except Exception as exc:
            result["jira_fetch_error"] = str(exc)

    return result

@router.post("/link/{entity_type}/{entity_id}")
async def create_link(entity_type: str, entity_id: str, body: dict = Body(...)):
    """Manually link an entity to an existing Jira issue."""
    issue_key = body.get("issue_key", "").strip().upper()
    if not issue_key:
        raise HTTPException(status_code=400, detail="issue_key is required")

    links = _load_links()
    key = _link_key(entity_type, entity_id)

    # Verify the issue exists if Jira is configured
    issue_id = ""
    if _jira_configured():
        try:
            issue = await _get_jira_issue(issue_key)
            issue_id = issue.get("id", "")
        except Exception:
            raise HTTPException(status_code=404, detail=f"Jira issue {issue_key} not found or not accessible")

    links[key] = {
        "issue_key": issue_key,
        "issue_id": issue_id,
        "last_synced": time.time(),
        "created_at": time.time(),
        "manual_link": True,
    }
    _save_links(links)

    return {
        "status": "linked",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "issue_key": issue_key,
        "issue_url": f"{_jira_base_url()}/browse/{issue_key}" if _jira_configured() else None,
    }

@router.delete("/link/{entity_type}/{entity_id}")
async def delete_link(entity_type: str, entity_id: str):
    """Unlink an entity from its Jira issue."""
    links = _load_links()
    key = _link_key(entity_type, entity_id)

    if key not in links:
        raise HTTPException(status_code=404, detail="No link found for this entity")

    removed = links.pop(key)
    _save_links(links)

    return {
        "status": "unlinked",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "removed_issue_key": removed.get("issue_key"),
    }

# ---------------------------------------------------------------------------
# Bulk sync
# ---------------------------------------------------------------------------

@router.post("/sync-all/{entity_type}")
async def sync_all(entity_type: str):
    """Bulk-sync all entities of a given type to Jira."""
    if not _jira_configured():
        return {
            "status": "not_configured",
            "message": "Jira is not configured. Set up credentials in Settings > Plugins > Jira Sync.",
            "mock": True,
        }

    # Fetch all entities of this type
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{STUDIO_API}/{entity_type}s")
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to fetch {entity_type}s from Studio API")
        entities = resp.json()
        if isinstance(entities, dict):
            entities = entities.get("items", entities.get("data", []))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Studio API error: {exc}")

    links = _load_links()
    results = {"created": 0, "updated": 0, "errors": 0, "total": len(entities), "details": []}

    for entity in entities:
        eid = entity.get("id", entity.get("_id", ""))
        if not eid:
            continue
        key = _link_key(entity_type, eid)
        try:
            if key in links and links[key].get("issue_key"):
                # Update existing
                issue_key = links[key]["issue_key"]
                update_fields = {"summary": entity.get("name", entity.get("title", ""))}
                resp = await _jira_request("PUT", f"/issue/{issue_key}", json={"fields": update_fields})
                if resp.status_code in (200, 204):
                    links[key]["last_synced"] = time.time()
                    links[key].pop("sync_error", None)
                    results["updated"] += 1
                    results["details"].append({"entity_id": eid, "action": "updated", "issue_key": issue_key})
                else:
                    links[key]["sync_error"] = f"HTTP {resp.status_code}"
                    results["errors"] += 1
                    results["details"].append({"entity_id": eid, "action": "error", "error": f"HTTP {resp.status_code}"})
            else:
                # Create new
                result = await _create_jira_issue(entity, entity_type)
                issue_key = result.get("key", "")
                links[key] = {
                    "issue_key": issue_key,
                    "issue_id": result.get("id", ""),
                    "last_synced": time.time(),
                    "created_at": time.time(),
                }
                results["created"] += 1
                results["details"].append({"entity_id": eid, "action": "created", "issue_key": issue_key})
        except Exception as exc:
            results["errors"] += 1
            results["details"].append({"entity_id": eid, "action": "error", "error": str(exc)})

    _save_links(links)
    return results

# ---------------------------------------------------------------------------
# Field mappings
# ---------------------------------------------------------------------------

@router.get("/mappings")
async def get_mappings():
    """Get entity-to-Jira field mappings."""
    return _load_mappings()

@router.put("/mappings")
async def update_mappings(body: dict = Body(...)):
    """Update entity-to-Jira field mappings."""
    _save_mappings(body)
    return {"status": "saved", "mappings": body}

# ---------------------------------------------------------------------------
# Webhook receiver (for bidirectional sync)
# ---------------------------------------------------------------------------

@router.post("/webhook")
async def jira_webhook(body: dict = Body(...)):
    """Receive Jira webhook events for bidirectional sync."""
    settings = _read_settings()
    if not settings.get("bidirectional_sync", False):
        return {"status": "ignored", "reason": "Bidirectional sync is disabled"}

    event_type = body.get("webhookEvent", "")
    issue = body.get("issue", {})
    issue_key = issue.get("key", "")

    if not issue_key:
        return {"status": "ignored", "reason": "No issue key in payload"}

    # Find the linked entity
    links = _load_links()
    entity_key = None
    for k, v in links.items():
        if v.get("issue_key") == issue_key:
            entity_key = k
            break

    if not entity_key:
        return {"status": "ignored", "reason": f"No linked entity for {issue_key}"}

    parts = entity_key.split(":", 1)
    if len(parts) != 2:
        return {"status": "ignored", "reason": "Malformed entity key"}

    entity_type, entity_id = parts

    if event_type in ("jira:issue_updated", "jira:issue_created"):
        # Update the entity in Studio
        fields = issue.get("fields", {})
        update_data = {}

        jira_status = fields.get("status", {}).get("name", "")
        if jira_status:
            # Reverse map status
            sm = _status_mapping()
            reverse_map = {v.lower(): k for k, v in sm.items()}
            studio_status = reverse_map.get(jira_status.lower())
            if studio_status:
                update_data["production_status"] = studio_status

        summary = fields.get("summary", "")
        if summary:
            update_data["name"] = summary

        if update_data:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.patch(
                        f"{STUDIO_API}/entity/{entity_type}/{entity_id}",
                        json=update_data,
                    )
                links[entity_key]["last_synced"] = time.time()
                _save_links(links)
                return {"status": "synced", "entity_type": entity_type, "entity_id": entity_id, "updates": update_data}
            except Exception as exc:
                return {"status": "error", "error": str(exc)}

    return {"status": "ignored", "reason": f"Unhandled event: {event_type}"}
