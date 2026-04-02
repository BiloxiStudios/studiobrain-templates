"""
Music Generator Plugin — backend routes.

Provides endpoints for generating ambient music and character themes,
auto-generating prompts from entity data, managing tracks, and
serving a music library across all entities.
"""

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("plugin.music-gen")

router = APIRouter()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BRAINS_ROOT = Path("A:/Brains")
PLUGIN_DIR = Path("A:/Brains/_Plugins/music-gen")
PLUGIN_DATA = PLUGIN_DIR / "data"
TRACKS_FILE = PLUGIN_DATA / "tracks.json"

BACKEND_URL = "http://localhost:8201"

# Ensure data directory
PLUGIN_DATA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------
def _get_setting(key: str, default=None):
    from services.plugin_settings_service import get_all_settings
    return get_all_settings("music-gen").get(key, default)


def _get_api_key(provider: str = None) -> Optional[str]:
    """Get the API key for the specified or default provider."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("music-gen")
    prov = provider or settings.get("provider", "suno")
    if prov == "suno":
        return settings.get("suno_api_key") or None
    elif prov == "udio":
        return settings.get("udio_api_key") or None
    return None


# ---------------------------------------------------------------------------
# Track data persistence
# ---------------------------------------------------------------------------

def _load_tracks() -> list[dict]:
    """Load all track metadata from tracks.json."""
    try:
        if TRACKS_FILE.exists():
            return json.loads(TRACKS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_tracks(tracks: list[dict]):
    """Save track metadata, keeping last 1000 entries."""
    TRACKS_FILE.write_text(
        json.dumps(tracks[-1000:], indent=2, default=str),
        encoding="utf-8",
    )


def _add_track(track: dict):
    """Append a track entry to the data file."""
    tracks = _load_tracks()
    tracks.append(track)
    _save_tracks(tracks)


def _remove_track(track_id: str) -> bool:
    """Remove a track by ID. Returns True if found and removed."""
    tracks = _load_tracks()
    original_len = len(tracks)
    tracks = [t for t in tracks if t.get("id") != track_id]
    if len(tracks) < original_len:
        _save_tracks(tracks)
        return True
    return False


# ---------------------------------------------------------------------------
# Entity helpers
# ---------------------------------------------------------------------------

def _entity_assets_dir(entity_type: str, entity_id: str) -> Path:
    """Return the assets directory for an entity, creating it if needed."""
    type_folder = entity_type.rstrip("s") + "s"
    type_folder = type_folder[0].upper() + type_folder[1:]
    assets = BRAINS_ROOT / type_folder / entity_id / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    return assets


def _type_folder(entity_type: str) -> str:
    """Convert entity type to folder name (character -> Characters)."""
    folder = entity_type.rstrip("s") + "s"
    return folder[0].upper() + folder[1:]


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


# ---------------------------------------------------------------------------
# Prompt generation helpers
# ---------------------------------------------------------------------------

def _build_auto_prompt(entity: dict, entity_type: str) -> dict:
    """Build a music generation prompt from entity data."""
    name = entity.get("name") or entity.get("title") or entity.get("label") or "Unknown"
    description = entity.get("description") or entity.get("summary") or ""
    personality = entity.get("personality") or ""
    mood = entity.get("mood") or entity.get("atmosphere") or ""
    biome = entity.get("biome") or entity.get("environment") or ""
    race = entity.get("race") or ""
    role = entity.get("role") or ""
    faction = entity.get("faction") or ""
    region = entity.get("region") or ""

    parts = []
    suggested_genre = "ambient"
    suggested_mood = "mysterious"

    if entity_type in ("character", "npc"):
        parts.append(f"Character theme for {name}.")
        if personality:
            parts.append(f"Personality: {personality[:120]}.")
        if race:
            parts.append(f"A {race} character.")
        if role:
            parts.append(f"Role: {role}.")
        if faction:
            parts.append(f"Aligned with {faction}.")

        # Infer mood from personality keywords
        personality_lower = (personality + " " + description).lower()
        if any(w in personality_lower for w in ("dark", "evil", "sinister", "menacing")):
            suggested_mood = "dark"
            suggested_genre = "orchestral"
        elif any(w in personality_lower for w in ("cheerful", "happy", "bright", "friendly")):
            suggested_mood = "uplifting"
            suggested_genre = "folk"
        elif any(w in personality_lower for w in ("brave", "heroic", "warrior", "fierce")):
            suggested_mood = "epic"
            suggested_genre = "orchestral"
        elif any(w in personality_lower for w in ("mysterious", "enigmatic", "shadow", "rogue")):
            suggested_mood = "mysterious"
            suggested_genre = "ambient"
        elif any(w in personality_lower for w in ("wise", "sage", "ancient", "scholarly")):
            suggested_mood = "contemplative"
            suggested_genre = "classical"

    elif entity_type in ("location", "area", "region", "map"):
        parts.append(f"Ambient atmosphere for {name}.")
        if biome:
            parts.append(f"Environment: {biome}.")
        if region:
            parts.append(f"Region: {region}.")
        if mood:
            parts.append(f"Atmosphere: {mood}.")

        biome_lower = (biome + " " + description + " " + mood).lower()
        if any(w in biome_lower for w in ("forest", "woods", "grove", "jungle")):
            suggested_mood = "natural"
            suggested_genre = "ambient"
        elif any(w in biome_lower for w in ("dungeon", "cave", "underground", "crypt")):
            suggested_mood = "tense"
            suggested_genre = "dark ambient"
        elif any(w in biome_lower for w in ("city", "town", "village", "tavern", "market")):
            suggested_mood = "lively"
            suggested_genre = "folk"
        elif any(w in biome_lower for w in ("ocean", "sea", "coast", "beach", "shore")):
            suggested_mood = "serene"
            suggested_genre = "ambient"
        elif any(w in biome_lower for w in ("mountain", "peak", "summit", "highland")):
            suggested_mood = "majestic"
            suggested_genre = "orchestral"
        elif any(w in biome_lower for w in ("desert", "sand", "arid", "wasteland")):
            suggested_mood = "desolate"
            suggested_genre = "world"
        elif any(w in biome_lower for w in ("castle", "fortress", "palace", "throne")):
            suggested_mood = "regal"
            suggested_genre = "orchestral"

    elif entity_type in ("campaign", "quest", "story", "arc"):
        parts.append(f"Theme music for the campaign: {name}.")
        if description:
            parts.append(f"Story: {description[:150]}.")
        suggested_genre = "orchestral"
        suggested_mood = "epic"

    elif entity_type in ("item", "artifact", "weapon"):
        parts.append(f"Musical motif for the item: {name}.")
        rarity = entity.get("rarity") or ""
        if rarity:
            parts.append(f"Rarity: {rarity}.")
        if description:
            parts.append(f"Description: {description[:100]}.")
        suggested_genre = "cinematic"
        suggested_mood = "mystical"

    else:
        parts.append(f"Theme music for {name}.")
        if description:
            parts.append(description[:200])

    if description and len(parts) < 3:
        parts.append(description[:150])

    prompt = " ".join(parts)

    return {
        "prompt": prompt,
        "suggested_genre": suggested_genre,
        "suggested_mood": suggested_mood,
        "entity_name": name,
    }


# ---------------------------------------------------------------------------
# Mock generation (when no API key is configured)
# ---------------------------------------------------------------------------

def _generate_mock_track(prompt: str, duration: int, genre: str,
                         entity_type: str, entity_id: str) -> dict:
    """Generate a mock track entry for preview/demo when no API keys are set."""
    ts = int(time.time())
    short_id = uuid.uuid4().hex[:8]
    output_format = _get_setting("output_format", "mp3")
    filename = f"music_{genre.replace(' ', '-')}_{ts}_{short_id}.{output_format}"

    assets_dir = _entity_assets_dir(entity_type, entity_id)
    filepath = assets_dir / filename

    # Write a minimal silent placeholder file so the file exists
    # In production this would be real audio from the API
    _write_silent_placeholder(filepath, output_format, duration)

    folder = _type_folder(entity_type)
    audio_url = f"{BACKEND_URL}/files/{folder}/{entity_id}/assets/{filename}"

    track = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "prompt": prompt,
        "genre": genre,
        "duration": duration,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "audio_url": audio_url,
        "provider": "mock",
        "created_at": ts,
        "status": "completed",
    }

    _add_track(track)
    return track


def _write_silent_placeholder(filepath: Path, fmt: str, duration: int):
    """
    Write a minimal valid audio file as a placeholder.
    For WAV: write a proper RIFF header with silence.
    For MP3: write a minimal frame.
    """
    import struct

    if fmt == "wav":
        sample_rate = 22050
        num_samples = sample_rate * duration
        data_size = num_samples * 2  # 16-bit mono
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + data_size,
            b'WAVE',
            b'fmt ',
            16,           # chunk size
            1,            # PCM format
            1,            # mono
            sample_rate,
            sample_rate * 2,
            2,            # block align
            16,           # bits per sample
            b'data',
            data_size,
        )
        filepath.write_bytes(header + b'\x00' * data_size)
    else:
        # Write a minimal MP3-ish placeholder (just enough to be recognized)
        # This is a single silent MPEG frame header repeated
        # In production, the real audio bytes come from the API
        frame = bytes([
            0xFF, 0xFB, 0x90, 0x00,  # MPEG1, Layer3, 128kbps, 44100Hz
        ]) + b'\x00' * 413  # pad rest of frame
        # Write enough frames for ~1 second, repeat for duration
        frames_per_sec = 38  # approximate for 128kbps
        total_frames = frames_per_sec * max(duration, 1)
        filepath.write_bytes(frame * total_frames)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str
    duration: Optional[int] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    entity_type: str = "character"
    entity_id: str = ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def plugin_status():
    """Status endpoint with plugin configuration info."""
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("music-gen")
    provider = settings.get("provider", "suno")
    api_key = _get_api_key(provider)
    tracks = _load_tracks()

    return {
        "plugin": "music-gen",
        "version": "0.2.0",
        "status": "ok",
        "provider": provider,
        "api_configured": bool(api_key),
        "output_format": _get_setting("output_format", "mp3"),
        "default_duration": _get_setting("default_duration", 30),
        "default_genre": _get_setting("default_genre", "ambient"),
        "total_tracks": len(tracks),
    }


@router.post("/generate")
async def generate_music(req: GenerateRequest):
    """
    Generate music from a text prompt.

    When API keys are configured, calls the provider API.
    Otherwise falls back to mock generation with a placeholder file.
    """
    from services.plugin_settings_service import get_all_settings
    settings = get_all_settings("music-gen")
    provider = settings.get("provider", "suno")
    api_key = _get_api_key(provider)
    duration = req.duration or int(_get_setting("default_duration", 30))
    genre = req.genre or _get_setting("default_genre", "ambient")
    output_format = _get_setting("output_format", "mp3")

    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required for generation.")

    if not req.entity_id:
        raise HTTPException(status_code=400, detail="Entity ID is required.")

    # If no API key, use mock generation
    if not api_key:
        logger.info("No API key configured for %s, using mock generation", provider)
        track = _generate_mock_track(
            prompt=req.prompt.strip(),
            duration=duration,
            genre=genre,
            entity_type=req.entity_type,
            entity_id=req.entity_id,
        )
        return {
            "success": True,
            "message": f"Track generated (mock mode — configure {provider} API key for real generation)",
            "track": track,
            "mock": True,
        }

    # --- Real API generation ---
    ts = int(time.time())
    short_id = uuid.uuid4().hex[:8]
    filename = f"music_{genre.replace(' ', '-')}_{ts}_{short_id}.{output_format}"
    assets_dir = _entity_assets_dir(req.entity_type, req.entity_id)
    filepath = assets_dir / filename

    try:
        if provider == "suno":
            audio_data = await _generate_via_suno(
                api_key, req.prompt.strip(), duration, genre, req.mood
            )
        elif provider == "udio":
            audio_data = await _generate_via_udio(
                api_key, req.prompt.strip(), duration, genre, req.mood
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

        filepath.write_bytes(audio_data)
        logger.info("Generated music: %s (%d bytes)", filepath, len(audio_data))

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Music generation failed: %s", exc)
        return {
            "success": False,
            "message": f"Generation failed: {str(exc)}",
            "track": None,
        }

    folder = _type_folder(req.entity_type)
    audio_url = f"{BACKEND_URL}/files/{folder}/{req.entity_id}/assets/{filename}"

    track = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "prompt": req.prompt.strip(),
        "genre": genre,
        "mood": req.mood or "",
        "duration": duration,
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "audio_url": audio_url,
        "provider": provider,
        "created_at": ts,
        "status": "completed",
    }
    _add_track(track)

    return {
        "success": True,
        "message": "Track generated successfully",
        "track": track,
        "mock": False,
    }


async def _generate_via_suno(api_key: str, prompt: str, duration: int,
                              genre: str, mood: Optional[str]) -> bytes:
    """Call Suno API to generate music. Returns raw audio bytes."""
    full_prompt = prompt
    if genre:
        full_prompt += f" Genre: {genre}."
    if mood:
        full_prompt += f" Mood: {mood}."

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            "https://studio-api.suno.ai/api/external/generate/",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": full_prompt,
                "duration": duration,
                "make_instrumental": True,
            },
        )
        if resp.status_code != 200:
            detail = resp.text[:500]
            raise HTTPException(
                status_code=502,
                detail=f"Suno API error ({resp.status_code}): {detail}",
            )
        data = resp.json()
        # Suno returns a URL to the generated audio
        audio_url = data.get("audio_url") or data.get("url", "")
        if not audio_url:
            raise HTTPException(status_code=502, detail="Suno did not return an audio URL")

        audio_resp = await client.get(audio_url, timeout=60)
        if audio_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to download audio from Suno")
        return audio_resp.content


async def _generate_via_udio(api_key: str, prompt: str, duration: int,
                              genre: str, mood: Optional[str]) -> bytes:
    """Call Udio API to generate music. Returns raw audio bytes."""
    full_prompt = prompt
    if genre:
        full_prompt += f" Genre: {genre}."
    if mood:
        full_prompt += f" Mood: {mood}."

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            "https://www.udio.com/api/v1/generate",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": full_prompt,
                "duration_seconds": duration,
                "instrumental": True,
            },
        )
        if resp.status_code != 200:
            detail = resp.text[:500]
            raise HTTPException(
                status_code=502,
                detail=f"Udio API error ({resp.status_code}): {detail}",
            )
        data = resp.json()
        audio_url = data.get("audio_url") or data.get("output_url", "")
        if not audio_url:
            raise HTTPException(status_code=502, detail="Udio did not return an audio URL")

        audio_resp = await client.get(audio_url, timeout=60)
        if audio_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to download audio from Udio")
        return audio_resp.content


@router.post("/auto-prompt/{entity_type}/{entity_id}")
async def auto_generate_prompt(entity_type: str, entity_id: str):
    """
    Generate a music prompt automatically from entity data.
    Analyzes entity fields (personality, biome, description, etc.)
    to build a descriptive prompt with suggested genre and mood.
    """
    entity = await _fetch_entity(entity_type, entity_id)
    result = _build_auto_prompt(entity, entity_type)
    return {
        "success": True,
        "entity_type": entity_type,
        "entity_id": entity_id,
        **result,
    }


@router.get("/tracks/{entity_type}/{entity_id}")
async def get_entity_tracks(entity_type: str, entity_id: str):
    """List all generated tracks for a specific entity."""
    all_tracks = _load_tracks()
    entity_tracks = [
        t for t in all_tracks
        if t.get("entity_type") == entity_type and t.get("entity_id") == entity_id
    ]
    # Also scan the assets directory for any music files not tracked
    assets_dir = _entity_assets_dir(entity_type, entity_id)
    folder = _type_folder(entity_type)

    tracked_filenames = {t.get("filename") for t in entity_tracks}
    for ext in ("*.mp3", "*.wav", "*.ogg", "*.flac"):
        for f in assets_dir.glob(ext):
            if f.name.startswith("music_") and f.name not in tracked_filenames:
                stat = f.stat()
                entity_tracks.append({
                    "id": uuid.uuid4().hex,
                    "filename": f.name,
                    "prompt": "(imported from disk)",
                    "genre": _parse_genre_from_filename(f.name),
                    "duration": 0,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "audio_url": f"{BACKEND_URL}/files/{folder}/{entity_id}/assets/{f.name}",
                    "provider": "disk",
                    "created_at": int(stat.st_mtime),
                    "status": "completed",
                })

    entity_tracks.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "tracks": entity_tracks,
        "count": len(entity_tracks),
    }


def _parse_genre_from_filename(filename: str) -> str:
    """Extract genre from filename like music_ambient_1234_abcd.mp3"""
    parts = filename.replace("music_", "").split("_")
    if parts:
        return parts[0].replace("-", " ")
    return "unknown"


@router.get("/library")
async def get_library(limit: int = 100, genre: Optional[str] = None):
    """Get all generated tracks across all entities (the music library)."""
    tracks = _load_tracks()

    if genre:
        tracks = [t for t in tracks if t.get("genre", "").lower() == genre.lower()]

    tracks.sort(key=lambda x: x.get("created_at", 0), reverse=True)

    # Compute stats
    all_tracks = _load_tracks()
    genres = {}
    providers = {}
    entity_types = {}
    for t in all_tracks:
        g = t.get("genre", "unknown")
        genres[g] = genres.get(g, 0) + 1
        p = t.get("provider", "unknown")
        providers[p] = providers.get(p, 0) + 1
        et = t.get("entity_type", "unknown")
        entity_types[et] = entity_types.get(et, 0) + 1

    total_duration = sum(t.get("duration", 0) for t in all_tracks)

    return {
        "tracks": tracks[:limit],
        "total": len(all_tracks),
        "stats": {
            "total_tracks": len(all_tracks),
            "total_duration_sec": total_duration,
            "genres": genres,
            "providers": providers,
            "entity_types": entity_types,
        },
    }


@router.delete("/tracks/{track_id}")
async def delete_track(track_id: str):
    """Delete a track by ID, removing both the metadata and the audio file."""
    tracks = _load_tracks()
    track = next((t for t in tracks if t.get("id") == track_id), None)

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Delete the audio file if it exists
    entity_type = track.get("entity_type", "")
    entity_id = track.get("entity_id", "")
    filename = track.get("filename", "")

    if entity_type and entity_id and filename:
        assets_dir = _entity_assets_dir(entity_type, entity_id)
        filepath = assets_dir / filename
        if filepath.exists():
            # Path traversal check
            if filepath.resolve().is_relative_to(assets_dir.resolve()):
                filepath.unlink()
                logger.info("Deleted audio file: %s", filepath)

    # Remove from metadata
    removed = _remove_track(track_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Track metadata not found")

    return {"success": True, "message": f"Track {track_id} deleted"}
