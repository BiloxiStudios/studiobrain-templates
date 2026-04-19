"""
Webhook Automations Plugin — API routes.

Provides CRUD for webhook rules, test firing, and delivery log retrieval.
All data is stored as JSON files in the plugin's data/ directory.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import json
import uuid
import os
import logging
from datetime import datetime, timezone
import httpx
import hmac
import hashlib

from services.plugin_data_service import PluginDataService

router = APIRouter()
logger = logging.getLogger("plugin.webhook-automations")

data_svc = PluginDataService("webhook-automations")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RULES_FILE = os.path.join(DATA_DIR, "rules.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(path: str, default=None):
    _ensure_data_dir()
    if default is None:
        default = []
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def _save_json(path: str, data):
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _load_rules() -> list[dict]:
    return _load_json(RULES_FILE, [])


def _save_rules(rules: list[dict]):
    _save_json(RULES_FILE, rules)


def _find_rule(rule_id: str) -> tuple[list[dict], dict | None, int]:
    """Return (rules_list, matched_rule, index). Index is -1 if not found."""
    rules = _load_rules()
    for i, r in enumerate(rules):
        if r.get("id") == rule_id:
            return rules, r, i
    return rules, None, -1


def _substitute_payload(template: str, variables: dict) -> str:
    """Replace {{key}} placeholders with values from *variables*."""
    result = template
    for key, value in variables.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def _build_payload(rule: dict, event_data: dict) -> str:
    """Build the webhook payload body, either from a custom template or default."""
    variables = {
        "entity_type": event_data.get("entity_type", ""),
        "entity_id": event_data.get("entity_id", ""),
        "event_type": event_data.get("event_type", ""),
        "entity_name": event_data.get("entity_name", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    template = rule.get("payload_template")
    if template:
        return _substitute_payload(template, variables)
    # Default payload
    payload = {
        "event": variables["event_type"],
        "entity_type": variables["entity_type"],
        "entity_id": variables["entity_id"],
        "entity_name": variables["entity_name"],
        "timestamp": variables["timestamp"],
        "source": "city-of-brains",
        "plugin": "webhook-automations",
        "data": event_data.get("data", {}),
    }
    return json.dumps(payload, default=str)


def _sign_payload(payload: str, secret: str) -> str:
    """Create HMAC-SHA256 signature for the payload."""
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class RuleCreate(BaseModel):
    name: str
    event_pattern: str = Field(
        ...,
        description="One of: entity.created, entity.updated, entity.deleted, entity.*"
    )
    entity_types: list[str] = Field(
        default_factory=list,
        description="Entity types to match, e.g. ['character', 'location']. Empty means all."
    )
    webhook_url: str
    method: str = Field(default="POST", description="HTTP method: POST or PUT")
    headers: dict[str, str] = Field(default_factory=dict)
    payload_template: Optional[str] = Field(
        default=None,
        description="Custom payload with {{entity_type}}, {{entity_id}}, {{event_type}}, {{entity_name}}, {{timestamp}} placeholders"
    )
    active: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    event_pattern: Optional[str] = None
    entity_types: Optional[list[str]] = None
    webhook_url: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[dict[str, str]] = None
    payload_template: Optional[str] = None
    active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def plugin_status():
    """Status endpoint with active rule count and delivery stats."""
    rules = _load_rules()
    log_result = data_svc.list(record_type="delivery_log", limit=10000)
    logs = [r["data"] for r in log_result["records"]]
    active_count = sum(1 for r in rules if r.get("active", True))
    total_deliveries = len(logs)
    success_count = sum(1 for l in logs if l.get("success"))
    return {
        "plugin": "webhook-automations",
        "version": "1.0.0",
        "status": "ok",
        "total_rules": len(rules),
        "active_rules": active_count,
        "total_deliveries": total_deliveries,
        "successful_deliveries": success_count,
        "success_rate": round(success_count / total_deliveries * 100, 1) if total_deliveries else 0,
    }


@router.get("/rules")
async def list_rules():
    """List all webhook rules."""
    rules = _load_rules()
    return {"rules": rules, "count": len(rules)}


@router.post("/rules")
async def create_rule(body: RuleCreate):
    """Create a new webhook rule."""
    rules = _load_rules()
    rule = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "event_pattern": body.event_pattern,
        "entity_types": body.entity_types,
        "webhook_url": body.webhook_url,
        "method": body.method.upper(),
        "headers": body.headers,
        "payload_template": body.payload_template,
        "active": body.active,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    rules.append(rule)
    _save_rules(rules)
    logger.info("[webhook-automations] Rule created: %s (%s)", rule["name"], rule["id"])
    return {"rule": rule, "message": "Rule created"}


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, body: RuleUpdate):
    """Update an existing webhook rule."""
    rules, rule, idx = _find_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    update_data = body.model_dump(exclude_none=True)
    if "method" in update_data:
        update_data["method"] = update_data["method"].upper()

    rule.update(update_data)
    rule["updated_at"] = datetime.now(timezone.utc).isoformat()
    rules[idx] = rule
    _save_rules(rules)
    logger.info("[webhook-automations] Rule updated: %s", rule_id)
    return {"rule": rule, "message": "Rule updated"}


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete a webhook rule."""
    rules, rule, idx = _find_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    rules.pop(idx)
    _save_rules(rules)
    logger.info("[webhook-automations] Rule deleted: %s", rule_id)
    return {"message": "Rule deleted", "id": rule_id}


@router.post("/rules/{rule_id}/test")
async def test_rule(rule_id: str):
    """Fire a test webhook with sample data for a specific rule."""
    rules, rule, idx = _find_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    sample_event = {
        "event_type": rule["event_pattern"].replace(".*", ".created"),
        "entity_type": rule["entity_types"][0] if rule["entity_types"] else "character",
        "entity_id": "test-entity-" + str(uuid.uuid4())[:8],
        "entity_name": "Test Entity (Sample)",
        "data": {
            "name": "Test Entity (Sample)",
            "description": "This is a test webhook delivery from City of Brains.",
            "test": True,
        },
    }

    payload_body = _build_payload(rule, sample_event)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CityOfBrains-Webhooks/1.0",
        "X-Webhook-Event": sample_event["event_type"],
        "X-Webhook-Test": "true",
    }
    headers.update(rule.get("headers", {}))

    log_entry = {
        "id": str(uuid.uuid4()),
        "rule_id": rule["id"],
        "rule_name": rule["name"],
        "event_type": sample_event["event_type"],
        "entity_type": sample_event["entity_type"],
        "entity_id": sample_event["entity_id"],
        "webhook_url": rule["webhook_url"],
        "method": rule.get("method", "POST"),
        "test": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    start = datetime.now(timezone.utc)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            method = rule.get("method", "POST").upper()
            resp = await client.request(
                method,
                rule["webhook_url"],
                content=payload_body,
                headers=headers,
            )
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        log_entry.update({
            "success": 200 <= resp.status_code < 300,
            "status_code": resp.status_code,
            "response_body": resp.text[:500],
            "duration_ms": round(elapsed * 1000),
        })
    except Exception as exc:
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        log_entry.update({
            "success": False,
            "status_code": None,
            "error": str(exc),
            "duration_ms": round(elapsed * 1000),
        })

    data_svc.create(record_type="delivery_log", data=log_entry, record_id=log_entry["id"])
    return {"result": log_entry, "payload_sent": payload_body}


@router.get("/logs")
async def get_logs(
    rule_id: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    entity_type: Optional[str] = Query(None),
    test_only: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Delivery logs with optional filters."""
    result = data_svc.list(record_type="delivery_log", limit=5000)
    logs = [r["data"] for r in result["records"]]

    if rule_id:
        logs = [l for l in logs if l.get("rule_id") == rule_id]
    if success is not None:
        logs = [l for l in logs if l.get("success") == success]
    if entity_type:
        logs = [l for l in logs if l.get("entity_type") == entity_type]
    if test_only is not None:
        logs = [l for l in logs if l.get("test", False) == test_only]

    total = len(logs)
    page = logs[offset: offset + limit]
    return {"logs": page, "total": total, "limit": limit, "offset": offset}


@router.get("/logs/{rule_id}")
async def get_rule_logs(
    rule_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Delivery logs for a specific rule."""
    rules, rule, idx = _find_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    result = data_svc.list(record_type="delivery_log", limit=5000)
    logs = [r["data"] for r in result["records"] if r["data"].get("rule_id") == rule_id]
    total = len(logs)
    page = logs[offset: offset + limit]
    return {"logs": page, "total": total, "rule_name": rule["name"], "limit": limit, "offset": offset}


@router.post("/migrate-logs")
async def migrate_legacy_logs():
    """One-time migration of delivery_logs.json to database."""
    legacy_file = os.path.join(DATA_DIR, "delivery_logs.json")
    if not os.path.exists(legacy_file):
        return {"migrated": 0, "message": "No legacy data found"}
    count = data_svc.import_from_json(legacy_file)
    return {"migrated": count, "message": f"Migrated {count} records"}
