"""
Webhook Automations Plugin — event handlers.

Listens for entity lifecycle events on the backend event bus, matches
them against active webhook rules, and fires HTTP requests asynchronously.
Logs all delivery attempts with retry support.
"""

import json
import uuid
import os
import logging
import asyncio
import hmac
import hashlib
from datetime import datetime, timezone

import httpx

logger = logging.getLogger("plugin.webhook-automations")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RULES_FILE = os.path.join(DATA_DIR, "rules.json")
LOGS_FILE = os.path.join(DATA_DIR, "delivery_logs.json")

# Defaults — overridden by plugin settings if available
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30
TIMEOUT_SECONDS = 10


# ---------------------------------------------------------------------------
# Helpers (duplicated minimally to keep events.py self-contained)
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


def _load_logs() -> list[dict]:
    return _load_json(LOGS_FILE, [])


def _append_log(entry: dict):
    """Append a delivery log entry, capped at 5000."""
    logs = _load_logs()
    logs.insert(0, entry)
    logs = logs[:5000]
    _save_json(LOGS_FILE, logs)


def _substitute_payload(template: str, variables: dict) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def _build_payload(rule: dict, event_data: dict) -> str:
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
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def _matches_event(rule: dict, event_type: str, entity_type: str) -> bool:
    """Check if a rule matches the given event_type and entity_type."""
    pattern = rule.get("event_pattern", "")
    # Pattern matching
    if pattern == "entity.*":
        pattern_match = event_type.startswith("entity.")
    else:
        pattern_match = pattern == event_type

    if not pattern_match:
        return False

    # Entity type filtering — empty list means match all
    allowed_types = rule.get("entity_types", [])
    if allowed_types and entity_type not in allowed_types:
        return False

    return True


# ---------------------------------------------------------------------------
# Core webhook delivery
# ---------------------------------------------------------------------------

async def _fire_webhook_with_retries(
    rule: dict,
    event_data: dict,
    max_retries: int = MAX_RETRIES,
    retry_delay: int = RETRY_DELAY_SECONDS,
    timeout: float = TIMEOUT_SECONDS,
):
    """
    Fire a webhook for the given rule and event data.
    Retries up to *max_retries* times on failure with *retry_delay* between.
    Logs every attempt.
    """
    payload_body = _build_payload(rule, event_data)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CityOfBrains-Webhooks/1.0",
        "X-Webhook-Event": event_data.get("event_type", "unknown"),
        "X-Webhook-Delivery": str(uuid.uuid4()),
    }
    headers.update(rule.get("headers", {}))

    method = rule.get("method", "POST").upper()
    attempt = 0

    while attempt <= max_retries:
        log_entry = {
            "id": str(uuid.uuid4()),
            "rule_id": rule["id"],
            "rule_name": rule.get("name", ""),
            "event_type": event_data.get("event_type", ""),
            "entity_type": event_data.get("entity_type", ""),
            "entity_id": event_data.get("entity_id", ""),
            "webhook_url": rule["webhook_url"],
            "method": method,
            "attempt": attempt + 1,
            "max_attempts": max_retries + 1,
            "test": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        start = datetime.now(timezone.utc)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.request(
                    method,
                    rule["webhook_url"],
                    content=payload_body,
                    headers=headers,
                )
            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            success = 200 <= resp.status_code < 300
            log_entry.update({
                "success": success,
                "status_code": resp.status_code,
                "response_body": resp.text[:500],
                "duration_ms": round(elapsed * 1000),
            })
            _append_log(log_entry)

            if success:
                logger.info(
                    "[webhook-automations] Delivered %s -> %s (%dms)",
                    rule["name"], rule["webhook_url"], log_entry["duration_ms"],
                )
                return  # Success — stop retrying

            logger.warning(
                "[webhook-automations] Delivery failed %s -> %s (HTTP %d, attempt %d/%d)",
                rule["name"], rule["webhook_url"], resp.status_code,
                attempt + 1, max_retries + 1,
            )

        except Exception as exc:
            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            log_entry.update({
                "success": False,
                "status_code": None,
                "error": str(exc),
                "duration_ms": round(elapsed * 1000),
            })
            _append_log(log_entry)
            logger.warning(
                "[webhook-automations] Delivery error %s -> %s (%s, attempt %d/%d)",
                rule["name"], rule["webhook_url"], exc,
                attempt + 1, max_retries + 1,
            )

        attempt += 1
        if attempt <= max_retries:
            await asyncio.sleep(retry_delay)

    logger.error(
        "[webhook-automations] All %d attempts exhausted for rule %s -> %s",
        max_retries + 1, rule["name"], rule["webhook_url"],
    )


# ---------------------------------------------------------------------------
# Event bus registration
# ---------------------------------------------------------------------------

def register_handlers(event_bus):
    """
    Called by the plugin loader with the backend EventBus instance.
    Registers a wildcard listener for all entity events, then dispatches
    to matching webhook rules.
    """

    @event_bus.on("entity.*")
    async def on_entity_event(event):
        event_type = getattr(event, "event_type", None) or ""
        entity_type = getattr(event, "entity_type", None) or ""
        entity_id = getattr(event, "entity_id", None) or ""
        data = getattr(event, "data", {}) or {}

        # Derive entity name from data if available
        entity_name = ""
        if isinstance(data, dict):
            entity_name = data.get("name", "") or data.get("title", "") or ""

        event_data = {
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "data": data,
        }

        # Load active rules and find matches
        rules = _load_rules()
        matching = [
            r for r in rules
            if r.get("active", True) and _matches_event(r, event_type, entity_type)
        ]

        if not matching:
            return

        logger.info(
            "[webhook-automations] Event %s %s/%s matched %d rule(s)",
            event_type, entity_type, entity_id, len(matching),
        )

        # Fire all matching webhooks concurrently
        tasks = [
            asyncio.create_task(
                _fire_webhook_with_retries(rule, event_data)
            )
            for rule in matching
        ]
        # Do not await — let them run in the background so the event bus
        # is not blocked. Errors are caught inside _fire_webhook_with_retries.
        for task in tasks:
            task.add_done_callback(_handle_task_exception)


def _handle_task_exception(task: asyncio.Task):
    """Log unhandled exceptions from background webhook tasks."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.error(
            "[webhook-automations] Unhandled error in webhook task: %s", exc,
            exc_info=exc,
        )
