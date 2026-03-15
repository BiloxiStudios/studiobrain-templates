"""
Social Publisher Plugin -- backend routes.

Provides endpoints for publishing entity data to X/Twitter, Bluesky,
Instagram, and Threads.  Supports scheduled posts, templates, history
tracking, and cross-platform publishing.

When API credentials are not configured the endpoints return mock
responses with clear setup instructions so the frontend can still
render previews.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger("plugin.social-publisher")

router = APIRouter()

# ---------------------------------------------------------------------------
# Data directory for persistent storage
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "post_history.json"
SCHEDULED_FILE = DATA_DIR / "scheduled.json"
TEMPLATES_FILE = DATA_DIR / "templates.json"

BACKEND_URL = "http://localhost:8201"

# ---------------------------------------------------------------------------
# Platform definitions
# ---------------------------------------------------------------------------
PLATFORMS = {
    "twitter": {
        "id": "twitter",
        "name": "X / Twitter",
        "color": "#000000",
        "icon": "twitter",
        "char_limit": 280,
    },
    "bluesky": {
        "id": "bluesky",
        "name": "Bluesky",
        "color": "#0085FF",
        "icon": "cloud",
        "char_limit": 300,
    },
    "instagram": {
        "id": "instagram",
        "name": "Instagram",
        "color": "#E1306C",
        "icon": "instagram",
        "char_limit": 2200,
    },
    "threads": {
        "id": "threads",
        "name": "Threads",
        "color": "#000000",
        "icon": "at-sign",
        "char_limit": 500,
    },
}

# ---------------------------------------------------------------------------
# Default templates
# ---------------------------------------------------------------------------
DEFAULT_TEMPLATES = [
    {
        "id": "character-reveal",
        "name": "Character Reveal",
        "description": "Dramatic character introduction post",
        "template": "Meet {name} -- {description_short}\n\n{hashtags}",
        "platforms": ["twitter", "bluesky", "threads"],
        "builtin": True,
    },
    {
        "id": "lore-drop",
        "name": "Lore Drop",
        "description": "Share a piece of world lore",
        "template": "LORE DROP\n\n{description}\n\n{hashtags}",
        "platforms": ["twitter", "bluesky", "threads"],
        "builtin": True,
    },
    {
        "id": "art-showcase",
        "name": "Art Showcase",
        "description": "Highlight AI-generated or concept art",
        "template": "New art for {name}!\n\n{hashtags}",
        "platforms": ["twitter", "bluesky", "instagram", "threads"],
        "builtin": True,
    },
    {
        "id": "dev-update",
        "name": "Dev Update",
        "description": "Development progress announcement",
        "template": "Dev Update: We just added {name} to the world of City of Brains.\n\n{description_short}\n\n{hashtags}",
        "platforms": ["twitter", "bluesky", "threads"],
        "builtin": True,
    },
    {
        "id": "minimal",
        "name": "Minimal",
        "description": "Clean, short-form post",
        "template": "{name}\n{hashtags}",
        "platforms": ["twitter", "bluesky", "instagram", "threads"],
        "builtin": True,
    },
]


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def _ensure_data_dir():
    """Create the data directory and seed files if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
    if not SCHEDULED_FILE.exists():
        SCHEDULED_FILE.write_text("[]", encoding="utf-8")
    if not TEMPLATES_FILE.exists():
        TEMPLATES_FILE.write_text(
            json.dumps(DEFAULT_TEMPLATES, indent=2), encoding="utf-8"
        )


def _load_json(path: Path) -> list[dict]:
    _ensure_data_dir()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_json(path: Path, data: list[dict]):
    _ensure_data_dir()
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _load_history() -> list[dict]:
    return _load_json(HISTORY_FILE)


def _save_history(history: list[dict]):
    _save_json(HISTORY_FILE, history)


def _append_history(entry: dict):
    history = _load_history()
    history.insert(0, entry)
    _save_history(history[:1000])


def _load_scheduled() -> list[dict]:
    return _load_json(SCHEDULED_FILE)


def _save_scheduled(items: list[dict]):
    _save_json(SCHEDULED_FILE, items)


def _load_templates() -> list[dict]:
    templates = _load_json(TEMPLATES_FILE)
    if not templates:
        _save_json(TEMPLATES_FILE, DEFAULT_TEMPLATES)
        return DEFAULT_TEMPLATES
    return templates


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------
def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("social-publisher").get(key, default)


def _platform_configured(platform: str) -> bool:
    """Check whether the required API keys exist for a platform."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("social-publisher")
    if platform == "twitter":
        return bool(
            settings.get("twitter_api_key")
            and settings.get("twitter_api_secret")
            and settings.get("twitter_access_token")
            and settings.get("twitter_access_secret")
        )
    elif platform == "bluesky":
        return bool(
            settings.get("bluesky_handle") and settings.get("bluesky_app_password")
        )
    elif platform == "instagram":
        return bool(
            settings.get("instagram_access_token")
            and settings.get("instagram_business_id")
        )
    elif platform == "threads":
        return bool(
            settings.get("threads_access_token")
            and settings.get("threads_user_id")
        )
    return False


# ---------------------------------------------------------------------------
# Entity helpers
# ---------------------------------------------------------------------------
async def _fetch_entity(entity_type: str, entity_id: str) -> dict:
    """Fetch entity data from the backend API."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BACKEND_URL}/api/entity/{entity_type}/{entity_id}"
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch entity {entity_type}/{entity_id}",
            )
        return resp.json()


def _get_entity_image_url(entity: dict, entity_type: str, entity_id: str) -> str | None:
    """Resolve the primary image URL for an entity."""
    image_file = (
        entity.get("primary_image")
        or entity.get("image")
        or entity.get("portrait")
    )
    if not image_file:
        return None
    type_plural = (
        entity_type.rstrip("s") + "s"
        if not entity_type.endswith("s")
        else entity_type
    )
    return f"{BACKEND_URL}/files/{type_plural}/{entity_id}/assets/{image_file}"


def _render_template(
    template_str: str, entity: dict, hashtags: str = ""
) -> str:
    """Fill a template string with entity fields."""
    name = (
        entity.get("name") or entity.get("title") or entity.get("label") or "Unnamed"
    )
    description = entity.get("description") or entity.get("summary") or ""
    description_short = description[:120] + ("..." if len(description) > 120 else "")

    replacements = {
        "{name}": name,
        "{description}": description[:500],
        "{description_short}": description_short,
        "{hashtags}": hashtags,
        "{type}": entity.get("type", "").replace("_", " ").title(),
        "{race}": entity.get("race", ""),
        "{class}": entity.get("class_name", ""),
        "{role}": entity.get("role", ""),
        "{faction}": entity.get("faction", ""),
        "{location}": entity.get("location", ""),
    }
    text = template_str
    for key, val in replacements.items():
        text = text.replace(key, val)
    # Clean up double newlines from empty replacements
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


# ---------------------------------------------------------------------------
# Platform publishers (mock when not configured)
# ---------------------------------------------------------------------------
async def _publish_twitter(text: str, image_url: str | None = None) -> dict:
    """Publish to X/Twitter.  Returns mock when credentials missing."""
    if not _platform_configured("twitter"):
        return {
            "success": True,
            "mock": True,
            "platform": "twitter",
            "message": "MOCK -- Configure X/Twitter API keys in plugin settings to publish for real.",
            "post_url": "https://x.com/i/status/mock_123456",
        }
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("social-publisher")
    try:
        import tweepy

        auth = tweepy.OAuth1UserHandler(
            settings["twitter_api_key"],
            settings["twitter_api_secret"],
            settings["twitter_access_token"],
            settings["twitter_access_secret"],
        )
        api = tweepy.API(auth)
        client_v2 = tweepy.Client(
            consumer_key=settings["twitter_api_key"],
            consumer_secret=settings["twitter_api_secret"],
            access_token=settings["twitter_access_token"],
            access_token_secret=settings["twitter_access_secret"],
        )

        media_id = None
        if image_url:
            async with httpx.AsyncClient(timeout=30) as http:
                img_resp = await http.get(image_url)
                if img_resp.status_code == 200:
                    tmp_path = DATA_DIR / "tmp_upload.jpg"
                    tmp_path.write_bytes(img_resp.content)
                    media = api.media_upload(str(tmp_path))
                    media_id = media.media_id
                    tmp_path.unlink(missing_ok=True)

        kwargs = {}
        if media_id:
            kwargs["media_ids"] = [media_id]
        resp = client_v2.create_tweet(text=text, **kwargs)
        tweet_id = resp.data["id"]
        return {
            "success": True,
            "mock": False,
            "platform": "twitter",
            "post_id": tweet_id,
            "post_url": f"https://x.com/i/status/{tweet_id}",
        }
    except Exception as exc:
        return {
            "success": False,
            "mock": False,
            "platform": "twitter",
            "error": str(exc),
        }


async def _publish_bluesky(text: str, image_url: str | None = None) -> dict:
    """Publish to Bluesky.  Returns mock when credentials missing."""
    if not _platform_configured("bluesky"):
        return {
            "success": True,
            "mock": True,
            "platform": "bluesky",
            "message": "MOCK -- Configure Bluesky handle and app password in plugin settings to publish for real.",
            "post_url": "https://bsky.app/profile/mock/post/mock123",
        }
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("social-publisher")
    try:
        from atproto import Client as BskyClient

        bsky = BskyClient()
        bsky.login(settings["bluesky_handle"], settings["bluesky_app_password"])

        image_blob = None
        if image_url:
            async with httpx.AsyncClient(timeout=30) as http:
                img_resp = await http.get(image_url)
                if img_resp.status_code == 200:
                    image_blob = bsky.upload_blob(img_resp.content).blob

        embed = None
        if image_blob:
            embed = {
                "$type": "app.bsky.embed.images",
                "images": [{"alt": text[:100], "image": image_blob}],
            }

        resp = bsky.send_post(text=text, embed=embed)
        return {
            "success": True,
            "mock": False,
            "platform": "bluesky",
            "post_url": f"https://bsky.app/profile/{settings['bluesky_handle']}/post/{resp.uri.split('/')[-1]}",
        }
    except Exception as exc:
        return {
            "success": False,
            "mock": False,
            "platform": "bluesky",
            "error": str(exc),
        }


async def _publish_instagram(text: str, image_url: str | None = None) -> dict:
    """Publish to Instagram via Graph API.  Returns mock when not configured."""
    if not _platform_configured("instagram"):
        return {
            "success": True,
            "mock": True,
            "platform": "instagram",
            "message": "MOCK -- Configure Instagram Graph API token and business ID in plugin settings to publish for real.",
            "post_url": "https://instagram.com/p/mock123",
        }
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("social-publisher")
    token = settings["instagram_access_token"]
    ig_id = settings["instagram_business_id"]
    try:
        async with httpx.AsyncClient(timeout=30) as http:
            # Step 1: create media container
            container_params = {
                "caption": text,
                "access_token": token,
            }
            if image_url:
                container_params["image_url"] = image_url
            resp1 = await http.post(
                f"https://graph.facebook.com/v18.0/{ig_id}/media",
                params=container_params,
            )
            creation_id = resp1.json().get("id")
            if not creation_id:
                return {
                    "success": False,
                    "mock": False,
                    "platform": "instagram",
                    "error": resp1.text,
                }
            # Step 2: publish
            resp2 = await http.post(
                f"https://graph.facebook.com/v18.0/{ig_id}/media_publish",
                params={"creation_id": creation_id, "access_token": token},
            )
            post_id = resp2.json().get("id")
            return {
                "success": True,
                "mock": False,
                "platform": "instagram",
                "post_id": post_id,
                "post_url": f"https://instagram.com/p/{post_id}",
            }
    except Exception as exc:
        return {
            "success": False,
            "mock": False,
            "platform": "instagram",
            "error": str(exc),
        }


async def _publish_threads(text: str, image_url: str | None = None) -> dict:
    """Publish to Threads via API.  Returns mock when not configured."""
    if not _platform_configured("threads"):
        return {
            "success": True,
            "mock": True,
            "platform": "threads",
            "message": "MOCK -- Configure Threads API token and user ID in plugin settings to publish for real.",
            "post_url": "https://threads.net/t/mock123",
        }
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("social-publisher")
    token = settings["threads_access_token"]
    user_id = settings["threads_user_id"]
    try:
        async with httpx.AsyncClient(timeout=30) as http:
            params = {
                "text": text,
                "media_type": "IMAGE" if image_url else "TEXT",
                "access_token": token,
            }
            if image_url:
                params["image_url"] = image_url
            resp1 = await http.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads",
                params=params,
            )
            creation_id = resp1.json().get("id")
            if not creation_id:
                return {
                    "success": False,
                    "mock": False,
                    "platform": "threads",
                    "error": resp1.text,
                }
            resp2 = await http.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
                params={"creation_id": creation_id, "access_token": token},
            )
            post_id = resp2.json().get("id")
            return {
                "success": True,
                "mock": False,
                "platform": "threads",
                "post_id": post_id,
                "post_url": f"https://threads.net/t/{post_id}",
            }
    except Exception as exc:
        return {
            "success": False,
            "mock": False,
            "platform": "threads",
            "error": str(exc),
        }


PUBLISHER_MAP = {
    "twitter": _publish_twitter,
    "bluesky": _publish_bluesky,
    "instagram": _publish_instagram,
    "threads": _publish_threads,
}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class PublishRequest(BaseModel):
    platforms: list[str]
    text: str
    image_url: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    template_id: Optional[str] = None
    schedule_at: Optional[str] = None  # ISO-8601 datetime string


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/")
async def status():
    """Plugin status and configured platforms."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("social-publisher")
    history = _load_history()
    scheduled = _load_scheduled()

    platform_status = {}
    for pid, pinfo in PLATFORMS.items():
        configured = _platform_configured(pid)
        platform_status[pid] = {
            **pinfo,
            "configured": configured,
            "status": "connected" if configured else "not_configured",
        }

    return {
        "plugin": "social-publisher",
        "version": "0.2.0",
        "status": "ok",
        "platforms": platform_status,
        "total_posts": len(history),
        "scheduled_count": len(scheduled),
        "auto_post_on_create": settings.get("auto_post_on_create", False),
        "default_hashtags": settings.get(
            "default_hashtags", "#CityOfBrains,#GameDev,#IndieGame"
        ),
        "auto_include_image": settings.get("auto_include_image", True),
    }


@router.post("/publish")
async def publish(req: PublishRequest):
    """
    Publish a post to one or more platforms.

    If ``schedule_at`` is provided the post is queued for later instead
    of being sent immediately.
    """
    if not req.platforms:
        raise HTTPException(status_code=400, detail="At least one platform must be selected.")

    # Validate platforms
    for p in req.platforms:
        if p not in PLATFORMS:
            raise HTTPException(status_code=400, detail=f"Unknown platform: {p}")

    # ---- Scheduled post ----
    if req.schedule_at:
        try:
            schedule_dt = datetime.fromisoformat(req.schedule_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid schedule_at datetime format. Use ISO-8601.")

        scheduled_entry = {
            "id": str(uuid.uuid4()),
            "platforms": req.platforms,
            "text": req.text,
            "image_url": req.image_url,
            "entity_type": req.entity_type,
            "entity_id": req.entity_id,
            "template_id": req.template_id,
            "schedule_at": schedule_dt.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        scheduled = _load_scheduled()
        scheduled.append(scheduled_entry)
        _save_scheduled(scheduled)

        return {
            "success": True,
            "scheduled": True,
            "post_id": scheduled_entry["id"],
            "schedule_at": scheduled_entry["schedule_at"],
            "message": f"Post scheduled for {schedule_dt.strftime('%Y-%m-%d %H:%M UTC')}",
        }

    # ---- Immediate publish ----
    # Optionally fetch entity for metadata
    entity_name = None
    if req.entity_type and req.entity_id:
        try:
            entity = await _fetch_entity(req.entity_type, req.entity_id)
            entity_name = entity.get("name") or entity.get("title") or "Unknown"
        except Exception:
            entity_name = "Unknown"

    results = []
    for platform in req.platforms:
        publisher = PUBLISHER_MAP.get(platform)
        if publisher:
            result = await publisher(req.text, req.image_url)
            results.append(result)

            # Record in history
            history_entry = {
                "id": str(uuid.uuid4()),
                "platform": platform,
                "text": req.text,
                "image_url": req.image_url,
                "entity_type": req.entity_type,
                "entity_id": req.entity_id,
                "entity_name": entity_name,
                "template_id": req.template_id,
                "success": result.get("success", False),
                "mock": result.get("mock", False),
                "post_url": result.get("post_url"),
                "error": result.get("error"),
                "posted_at": datetime.now(timezone.utc).isoformat(),
            }
            _append_history(history_entry)

    all_ok = all(r.get("success") for r in results)
    return {
        "success": all_ok,
        "results": results,
        "message": f"Published to {len(results)} platform(s)"
        + (" (some mocked)" if any(r.get("mock") for r in results) else ""),
    }


@router.get("/templates")
async def list_templates():
    """Return all available post templates."""
    templates = _load_templates()
    return {"templates": templates}


@router.get("/templates/preview")
async def preview_template(
    template_id: str,
    entity_type: str,
    entity_id: str,
):
    """Render a template with a specific entity's data for preview."""
    templates = _load_templates()
    template = next((t for t in templates if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")

    entity = await _fetch_entity(entity_type, entity_id)
    hashtags = _get_setting("default_hashtags", "#CityOfBrains,#GameDev,#IndieGame")
    hashtag_str = " ".join(h.strip() for h in hashtags.split(",") if h.strip())

    rendered = _render_template(template["template"], entity, hashtag_str)
    image_url = _get_entity_image_url(entity, entity_type, entity_id)

    return {
        "template_id": template_id,
        "rendered_text": rendered,
        "image_url": image_url,
        "char_counts": {
            pid: {
                "count": len(rendered),
                "limit": pinfo["char_limit"],
                "over": len(rendered) > pinfo["char_limit"],
            }
            for pid, pinfo in PLATFORMS.items()
        },
    }


@router.get("/history")
async def get_history(
    entity_type: str | None = None,
    entity_id: str | None = None,
    platform: str | None = None,
    limit: int = 50,
):
    """Get post history, optionally filtered by entity or platform."""
    history = _load_history()

    if entity_type and entity_id:
        history = [
            h
            for h in history
            if h.get("entity_type") == entity_type
            and h.get("entity_id") == entity_id
        ]
    elif entity_type:
        history = [h for h in history if h.get("entity_type") == entity_type]

    if platform:
        history = [h for h in history if h.get("platform") == platform]

    return {"total": len(history), "items": history[:limit]}


@router.get("/scheduled")
async def get_scheduled():
    """Return all upcoming scheduled posts."""
    scheduled = _load_scheduled()
    # Filter to only pending
    pending = [s for s in scheduled if s.get("status") == "pending"]
    # Sort by schedule_at ascending
    pending.sort(key=lambda s: s.get("schedule_at", ""))
    return {"total": len(pending), "items": pending}


@router.delete("/scheduled/{post_id}")
async def cancel_scheduled(post_id: str):
    """Cancel a scheduled post by ID."""
    scheduled = _load_scheduled()
    found = False
    new_scheduled = []
    for item in scheduled:
        if item.get("id") == post_id:
            found = True
            item["status"] = "cancelled"
            # Move to history as cancelled
            _append_history({
                **item,
                "success": False,
                "mock": False,
                "error": "Cancelled by user",
                "posted_at": datetime.now(timezone.utc).isoformat(),
            })
        else:
            new_scheduled.append(item)
    _save_scheduled(new_scheduled)

    if not found:
        raise HTTPException(status_code=404, detail=f"Scheduled post '{post_id}' not found.")

    return {"success": True, "message": "Scheduled post cancelled."}


@router.get("/stats")
async def get_stats():
    """Aggregate posting statistics for the dashboard."""
    history = _load_history()
    today = datetime.now(timezone.utc).date().isoformat()

    posts_today = sum(1 for h in history if h.get("posted_at", "").startswith(today))
    successful = sum(1 for h in history if h.get("success"))
    failed = sum(1 for h in history if not h.get("success"))
    mocked = sum(1 for h in history if h.get("mock"))

    # Per-platform counts
    platform_counts = {}
    for h in history:
        p = h.get("platform", "unknown")
        platform_counts[p] = platform_counts.get(p, 0) + 1

    # Per entity-type counts
    type_counts = {}
    for h in history:
        t = h.get("entity_type") or "unknown"
        type_counts[t] = type_counts.get(t, 0) + 1

    # Most posted entity
    entity_counts: dict[str, int] = {}
    entity_names: dict[str, str] = {}
    for h in history:
        if h.get("entity_type") and h.get("entity_id"):
            key = f"{h['entity_type']}/{h['entity_id']}"
            entity_counts[key] = entity_counts.get(key, 0) + 1
            entity_names[key] = h.get("entity_name") or "Unknown"

    most_posted = None
    if entity_counts:
        top_key = max(entity_counts, key=entity_counts.get)
        most_posted = {
            "entity": entity_names.get(top_key, "Unknown"),
            "key": top_key,
            "count": entity_counts[top_key],
        }

    return {
        "total_posts": len(history),
        "posts_today": posts_today,
        "successful": successful,
        "failed": failed,
        "mocked": mocked,
        "platform_counts": platform_counts,
        "entity_type_counts": type_counts,
        "most_posted": most_posted,
    }
