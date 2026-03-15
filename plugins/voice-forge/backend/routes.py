"""
Voice Forge Plugin — backend routes.

Provides TTS generation via ElevenLabs API, voice profile management,
and audio history tracking for character entities.
"""

import json
import logging
import os
import time
import uuid
from pathlib import Path

import aiohttp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger("plugin.voice-forge")

router = APIRouter()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BRAINS_ROOT = Path("A:/Brains")
PLUGIN_DATA = Path("A:/Brains/_Plugins/voice-forge/data")
PROFILES_FILE = PLUGIN_DATA / "voice_profiles.json"
GENERATION_LOG = PLUGIN_DATA / "generation_log.json"

# Ensure data directory
PLUGIN_DATA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("voice-forge").get(key, default)


def _get_api_key() -> Optional[str]:
    return _get_setting("elevenlabs_api_key") or None


def _entity_assets_dir(entity_type: str, entity_id: str) -> Path:
    """Return the assets directory for an entity, creating it if needed."""
    type_folder = entity_type.rstrip("s") + "s"          # character -> Characters
    type_folder = type_folder[0].upper() + type_folder[1:]
    assets = BRAINS_ROOT / type_folder / entity_id / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    return assets


def _load_profiles() -> dict:
    try:
        if PROFILES_FILE.exists():
            return json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_profiles(profiles: dict):
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2), encoding="utf-8")


def _load_generation_log() -> list:
    try:
        if GENERATION_LOG.exists():
            return json.loads(GENERATION_LOG.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_generation_log(log: list):
    # Keep last 500 entries
    GENERATION_LOG.write_text(json.dumps(log[-500:], indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    entity_type: str = "character"
    entity_id: str
    style: Optional[str] = "normal"
    model_id: Optional[str] = None


class VoiceProfile(BaseModel):
    entity_id: str
    voice_id: str
    voice_name: Optional[str] = ""
    styles: Optional[dict] = Field(default_factory=lambda: {
        "normal": {"stability": 0.5, "similarity_boost": 0.75},
        "angry": {"stability": 0.3, "similarity_boost": 0.85},
        "whisper": {"stability": 0.8, "similarity_boost": 0.6},
        "excited": {"stability": 0.25, "similarity_boost": 0.8},
        "sad": {"stability": 0.7, "similarity_boost": 0.7},
    })


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def plugin_status():
    """Status endpoint with available configuration info."""
    api_key = _get_api_key()
    provider = _get_setting("provider", "elevenlabs")
    return {
        "plugin": "voice-forge",
        "version": "0.2.0",
        "provider": provider,
        "api_configured": bool(api_key),
        "output_format": _get_setting("output_format", "mp3"),
        "default_voice_id": _get_setting("default_voice_id", "21m00Tcm4TlvDq8ikWAM"),
        "profiles_count": len(_load_profiles()),
    }


@router.get("/voices")
async def list_voices():
    """List available voices from ElevenLabs, or return defaults if no key."""
    api_key = _get_api_key()

    if not api_key:
        return {
            "source": "defaults",
            "message": "No ElevenLabs API key configured. Add one in Settings > Plugins > Voice Forge.",
            "voices": [
                {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "category": "premade"},
                {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "category": "premade"},
                {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "category": "premade"},
                {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "category": "premade"},
                {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "category": "premade"},
                {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "category": "premade"},
                {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "category": "premade"},
                {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "category": "premade"},
                {"voice_id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam", "category": "premade"},
                {"voice_id": "jBpfuIE2acCO8z3wKNLl", "name": "Gigi", "category": "premade"},
            ],
        }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": api_key},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    return {"source": "error", "message": f"ElevenLabs API error ({resp.status}): {body}", "voices": []}
                data = await resp.json()
                voices = [
                    {
                        "voice_id": v["voice_id"],
                        "name": v.get("name", "Unknown"),
                        "category": v.get("category", "premade"),
                        "labels": v.get("labels", {}),
                        "preview_url": v.get("preview_url", ""),
                    }
                    for v in data.get("voices", [])
                ]
                return {"source": "elevenlabs", "voices": voices}
    except Exception as exc:
        logger.error("Failed to fetch voices: %s", exc)
        return {"source": "error", "message": str(exc), "voices": []}


@router.post("/generate")
async def generate_speech(req: GenerateRequest):
    """Generate TTS audio and save to entity assets directory."""
    api_key = _get_api_key()
    output_format = _get_setting("output_format", "mp3")
    default_voice = _get_setting("default_voice_id", "21m00Tcm4TlvDq8ikWAM")
    model_id = req.model_id or _get_setting("default_model", "eleven_multilingual_v2")
    voice_id = req.voice_id or default_voice

    if not api_key:
        return {
            "success": False,
            "message": "No ElevenLabs API key configured. Add your key in Settings > Plugins > Voice Forge.",
            "audio_url": None,
        }

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required for generation.")

    # Load voice profile for style settings if available
    profiles = _load_profiles()
    profile = profiles.get(req.entity_id, {})
    style_settings = {}
    if profile and req.style in profile.get("styles", {}):
        style_settings = profile["styles"][req.style]

    stability = style_settings.get("stability", 0.5)
    similarity_boost = style_settings.get("similarity_boost", 0.75)

    # Style-based adjustments
    style_map = {
        "normal": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0},
        "angry": {"stability": 0.3, "similarity_boost": 0.85, "style": 0.8},
        "whisper": {"stability": 0.8, "similarity_boost": 0.6, "style": 0.2},
        "excited": {"stability": 0.25, "similarity_boost": 0.8, "style": 0.7},
        "sad": {"stability": 0.7, "similarity_boost": 0.7, "style": 0.5},
    }
    if not style_settings and req.style in style_map:
        style_settings = style_map[req.style]
        stability = style_settings.get("stability", 0.5)
        similarity_boost = style_settings.get("similarity_boost", 0.75)

    # Build request payload
    payload = {
        "text": req.text.strip(),
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style_settings.get("style", 0.0),
            "use_speaker_boost": True,
        },
    }

    # Generate filename
    ts = int(time.time())
    short_id = uuid.uuid4().hex[:8]
    filename = f"voice_{req.style}_{ts}_{short_id}.{output_format}"
    assets_dir = _entity_assets_dir(req.entity_type, req.entity_id)
    filepath = assets_dir / filename

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": f"audio/{output_format}",
            }
            async with session.post(
                url, json=payload, headers=headers,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    return {
                        "success": False,
                        "message": f"ElevenLabs API error ({resp.status}): {body}",
                        "audio_url": None,
                    }
                audio_data = await resp.read()
                filepath.write_bytes(audio_data)
                logger.info("Generated voice audio: %s (%d bytes)", filepath, len(audio_data))
    except Exception as exc:
        logger.error("TTS generation failed: %s", exc)
        return {"success": False, "message": str(exc), "audio_url": None}

    # Build asset URL
    type_folder = req.entity_type.rstrip("s") + "s"
    type_folder = type_folder[0].upper() + type_folder[1:]
    audio_url = f"http://localhost:8201/files/{type_folder}/{req.entity_id}/assets/{filename}"

    # Log the generation
    gen_log = _load_generation_log()
    gen_log.append({
        "timestamp": ts,
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "voice_id": voice_id,
        "style": req.style,
        "text_preview": req.text[:100],
        "filename": filename,
        "audio_url": audio_url,
    })
    _save_generation_log(gen_log)

    return {
        "success": True,
        "message": "Audio generated successfully",
        "filename": filename,
        "audio_url": audio_url,
        "duration_estimate": round(len(req.text.split()) * 0.4, 1),
        "style": req.style,
        "voice_id": voice_id,
    }


@router.get("/history/{entity_type}/{entity_id}")
async def get_history(entity_type: str, entity_id: str):
    """List all generated audio files for an entity."""
    assets_dir = _entity_assets_dir(entity_type, entity_id)
    type_folder = entity_type.rstrip("s") + "s"
    type_folder = type_folder[0].upper() + type_folder[1:]

    audio_files = []
    for ext in ("*.mp3", "*.wav", "*.ogg"):
        for f in assets_dir.glob(ext):
            if f.name.startswith("voice_"):
                stat = f.stat()
                audio_files.append({
                    "filename": f.name,
                    "url": f"http://localhost:8201/files/{type_folder}/{entity_id}/assets/{f.name}",
                    "size": stat.st_size,
                    "created": int(stat.st_mtime),
                    "style": _parse_style_from_filename(f.name),
                })

    audio_files.sort(key=lambda x: x["created"], reverse=True)
    return {"entity_type": entity_type, "entity_id": entity_id, "files": audio_files}


def _parse_style_from_filename(filename: str) -> str:
    """Extract style from filename like voice_angry_1234_abcd.mp3"""
    parts = filename.replace("voice_", "").split("_")
    if parts:
        return parts[0]
    return "normal"


@router.delete("/audio/{entity_type}/{entity_id}/{filename}")
async def delete_audio(entity_type: str, entity_id: str, filename: str):
    """Delete a generated audio file."""
    assets_dir = _entity_assets_dir(entity_type, entity_id)
    filepath = assets_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Prevent path traversal
    if not filepath.resolve().is_relative_to(assets_dir.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")

    filepath.unlink()
    logger.info("Deleted audio file: %s", filepath)
    return {"success": True, "message": f"Deleted {filename}"}


@router.get("/voice-profiles")
async def list_voice_profiles():
    """List all voice profiles."""
    profiles = _load_profiles()
    return {"profiles": profiles}


@router.post("/voice-profiles")
async def upsert_voice_profile(profile: VoiceProfile):
    """Create or update a voice profile for a character."""
    profiles = _load_profiles()
    profiles[profile.entity_id] = {
        "voice_id": profile.voice_id,
        "voice_name": profile.voice_name,
        "styles": profile.styles,
        "updated": int(time.time()),
    }
    _save_profiles(profiles)
    logger.info("Updated voice profile for entity %s", profile.entity_id)
    return {"success": True, "profile": profiles[profile.entity_id]}


@router.get("/generation-log")
async def get_generation_log():
    """Return recent generation history across all entities."""
    log = _load_generation_log()
    log.reverse()
    return {"entries": log[:100]}
