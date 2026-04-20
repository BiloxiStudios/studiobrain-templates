"""
Discord Poster Plugin — backend routes.

Provides endpoints for posting entity data to Discord via webhooks,
managing webhook configurations, and tracking post history.
"""

import json
import logging

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("plugin.discord-poster")

router = APIRouter()

# ---------------------------------------------------------------------------
# Data directory for persistent storage
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

BACKEND_URL = "http://localhost:8201"

from services.plugin_data_service import PluginDataService

data_svc = PluginDataService("discord-poster")

# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------
def _get_webhooks() -> list[dict]:
    """Return list of configured webhooks [{name, url}, ...]."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("discord-poster")
    webhooks = []

    # Default webhook
    default_url = settings.get("default_webhook_url", "")
    if default_url:
        webhooks.append({"name": "Default", "url": default_url})

    # Additional webhooks from JSON string
    extra_raw = settings.get("webhook_urls", "[]")
    try:
        extra = json.loads(extra_raw) if isinstance(extra_raw, str) else extra_raw
        if isinstance(extra, list):
            for wh in extra:
                if isinstance(wh, dict) and wh.get("url"):
                    webhooks.append({
                        "name": wh.get("name", "Unnamed"),
                        "url": wh["url"],
                    })
    except Exception:
        pass

    return webhooks

def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("discord-poster").get(key, default)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class PostRequest(BaseModel):
    entity_type: str
    entity_id: str
    webhook_url: Optional[str] = None
    message: Optional[str] = None
    include_image: bool = True

class TestWebhookRequest(BaseModel):
    webhook_url: str

# ---------------------------------------------------------------------------
# Discord embed builder
# ---------------------------------------------------------------------------
def _hex_to_int(hex_color: str) -> int:
    """Convert hex color like #5865F2 to integer."""
    hex_color = hex_color.lstrip("#")
    try:
        return int(hex_color, 16)
    except ValueError:
        return 0x5865F2  # Discord blurple fallback

async def _fetch_entity(entity_type: str, entity_id: str) -> dict:
    """Fetch entity data from the backend API."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND_URL}/api/entity/{entity_type}/{entity_id}")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch entity {entity_type}/{entity_id}",
            )
        return resp.json()

def _build_embed(entity: dict, entity_type: str, entity_id: str,
                 message: str | None = None, include_image: bool = True) -> dict:
    """Build a Discord embed from entity data."""
    color_hex = _get_setting("embed_color", "#5865F2")
    color_int = _hex_to_int(color_hex)

    name = entity.get("name") or entity.get("title") or entity.get("label") or "Unnamed Entity"
    description = entity.get("description") or entity.get("summary") or ""

    # Truncate description for Discord (max 4096 chars)
    if len(description) > 400:
        description = description[:397] + "..."

    if message:
        description = f"{message}\n\n{description}"

    embed = {
        "title": name,
        "description": description,
        "color": color_int,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": f"City of Brains \u2022 {entity_type.capitalize()}",
        },
        "fields": [],
    }

    # Add metadata fields
    type_display = entity_type.replace("_", " ").title()
    embed["fields"].append({
        "name": "Type",
        "value": type_display,
        "inline": True,
    })

    # Add common entity fields as embed fields
    field_map = {
        "race": "Race",
        "class_name": "Class",
        "role": "Role",
        "location": "Location",
        "faction": "Faction",
        "status": "Status",
        "rarity": "Rarity",
        "biome": "Biome",
        "region": "Region",
    }
    for key, label in field_map.items():
        val = entity.get(key)
        if val and isinstance(val, str) and val.strip():
            embed["fields"].append({
                "name": label,
                "value": val.strip(),
                "inline": True,
            })

    # Add image if available
    if include_image:
        # Check for primary_image or image field
        image_file = entity.get("primary_image") or entity.get("image") or entity.get("portrait")
        if image_file:
            # Pluralize entity type for file path (Character -> Characters)
            type_plural = entity_type.rstrip("s") + "s" if not entity_type.endswith("s") else entity_type
            image_url = f"{BACKEND_URL}/files/{type_plural}/{entity_id}/assets/{image_file}"
            embed["image"] = {"url": image_url}

        # Also check for thumbnail
        thumbnail = entity.get("thumbnail") or entity.get("icon")
        if thumbnail:
            type_plural = entity_type.rstrip("s") + "s" if not entity_type.endswith("s") else entity_type
            embed["thumbnail"] = {"url": f"{BACKEND_URL}/files/{type_plural}/{entity_id}/assets/{thumbnail}"}

    return embed

async def _post_to_discord(webhook_url: str, embed: dict, bot_username: str | None = None,
                           bot_avatar: str | None = None) -> dict:
    """Post an embed to a Discord webhook. Returns status info."""
    username = bot_username or _get_setting("bot_username", "City of Brains")
    avatar_url = bot_avatar or _get_setting("bot_avatar_url")

    payload = {
        "username": username,
        "embeds": [embed],
    }
    if avatar_url:
        payload["avatar_url"] = avatar_url

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(webhook_url, json=payload)
            success = resp.status_code in (200, 204)
            return {
                "success": success,
                "status_code": resp.status_code,
                "detail": resp.text if not success else None,
            }
        except httpx.RequestError as exc:
            return {
                "success": False,
                "status_code": 0,
                "detail": str(exc),
            }

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/")
async def status():
    """Plugin status and info."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("discord-poster")
    webhooks = _get_webhooks()
    result = data_svc.list(record_type="post_history", limit=1)
    total_posts = result["total"]
    return {
        "plugin": "discord-poster",
        "version": "0.2.0",
        "status": "ok",
        "webhooks_configured": len(webhooks),
        "total_posts": total_posts,
        "auto_post_on_create": settings.get("auto_post_on_create", False),
        "auto_post_on_update": settings.get("auto_post_on_update", False),
    }

@router.post("/post")
async def post_to_discord(req: PostRequest):
    """Post an entity to Discord via webhook."""
    # Determine webhook URL
    webhook_url = req.webhook_url
    if not webhook_url:
        webhooks = _get_webhooks()
        if not webhooks:
            raise HTTPException(status_code=400, detail="No webhook URL configured. Add one in plugin settings.")
        webhook_url = webhooks[0]["url"]

    # Fetch entity data
    entity = await _fetch_entity(req.entity_type, req.entity_id)

    # Build embed
    embed = _build_embed(entity, req.entity_type, req.entity_id, req.message, req.include_image)

    # Post to Discord
    result = await _post_to_discord(webhook_url, embed)

    # Determine webhook name
    webhook_name = "Custom"
    for wh in _get_webhooks():
        if wh["url"] == webhook_url:
            webhook_name = wh["name"]
            break

    # Save to history
    history_entry = {
        "id": str(uuid.uuid4()),
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "entity_name": entity.get("name") or entity.get("title") or "Unknown",
        "webhook_name": webhook_name,
        "webhook_url": webhook_url[:60] + "..." if len(webhook_url) > 60 else webhook_url,
        "message": req.message,
        "include_image": req.include_image,
        "success": result["success"],
        "status_code": result["status_code"],
        "error": result.get("detail"),
        "posted_at": datetime.now(timezone.utc).isoformat(),
    }
    data_svc.create(
        record_type="post_history",
        data=history_entry,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
        record_id=history_entry["id"],
    )

    if not result["success"]:
        raise HTTPException(
            status_code=502,
            detail=f"Discord returned status {result['status_code']}: {result.get('detail', 'Unknown error')}",
        )

    return {
        "success": True,
        "message": f"Posted to Discord ({webhook_name})",
        "history_id": history_entry["id"],
    }

@router.get("/history")
async def get_history(entity_type: str | None = None, entity_id: str | None = None,
                      limit: int = 50):
    result = data_svc.list(
        record_type="post_history",
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )
    items = [r["data"] for r in result["records"]]
    return {"total": result["total"], "items": items}

@router.get("/webhooks")
async def list_webhooks():
    """List all configured webhooks (URLs are masked for security)."""
    webhooks = _get_webhooks()
    masked = []
    for wh in webhooks:
        url = wh["url"]
        # Mask the webhook URL for display
        if len(url) > 40:
            masked_url = url[:35] + "..." + url[-8:]
        else:
            masked_url = url[:20] + "..."
        masked.append({
            "name": wh["name"],
            "url_preview": masked_url,
            "url": url,
        })
    return {"webhooks": masked}

@router.post("/test-webhook")
async def test_webhook(req: TestWebhookRequest):
    """Send a test message to a Discord webhook."""
    test_embed = {
        "title": "Test Message from City of Brains",
        "description": "If you can see this, the webhook is configured correctly!",
        "color": _hex_to_int("#5865F2"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": "Discord Poster Plugin \u2022 Test"},
        "fields": [
            {"name": "Status", "value": "Connected", "inline": True},
            {"name": "Plugin", "value": "discord-poster v0.2.0", "inline": True},
        ],
    }

    result = await _post_to_discord(req.webhook_url, test_embed)

    if not result["success"]:
        raise HTTPException(
            status_code=502,
            detail=f"Webhook test failed (status {result['status_code']}): {result.get('detail', 'Unknown error')}",
        )

    return {"success": True, "message": "Test message sent successfully!"}

@router.get("/entity-preview")
async def entity_preview(entity_type: str, entity_id: str):
    """Get a preview of what the Discord embed would look like for an entity."""
    entity = await _fetch_entity(entity_type, entity_id)
    embed = _build_embed(entity, entity_type, entity_id, include_image=True)
    return {
        "entity_name": entity.get("name") or entity.get("title") or "Unknown",
        "embed": embed,
    }

@router.get("/stats")
async def get_stats():
    """Get posting statistics."""
    result = data_svc.list(record_type="post_history", limit=10000)
    history = [r["data"] for r in result["records"]]
    today = datetime.now(timezone.utc).date().isoformat()

    posts_today = sum(1 for h in history if h.get("posted_at", "").startswith(today))
    successful = sum(1 for h in history if h.get("success"))
    failed = sum(1 for h in history if not h.get("success"))

    # Most posted entity
    entity_counts: dict[str, int] = {}
    entity_names: dict[str, str] = {}
    for h in history:
        key = f"{h.get('entity_type', '?')}/{h.get('entity_id', '?')}"
        entity_counts[key] = entity_counts.get(key, 0) + 1
        entity_names[key] = h.get("entity_name", "Unknown")

    most_posted = None
    if entity_counts:
        top_key = max(entity_counts, key=entity_counts.get)
        most_posted = {
            "entity": entity_names.get(top_key, "Unknown"),
            "count": entity_counts[top_key],
        }

    return {
        "total_posts": len(history),
        "posts_today": posts_today,
        "successful": successful,
        "failed": failed,
        "most_posted": most_posted,
    }

@router.post("/migrate")
async def migrate_legacy_data():
    """One-time migration of post_history.json to database."""
    legacy_file = DATA_DIR / "post_history.json"
    if not legacy_file.exists():
        return {"migrated": 0, "message": "No legacy data found"}
    count = data_svc.import_from_json(str(legacy_file))
    return {"migrated": count, "message": f"Migrated {count} records"}
