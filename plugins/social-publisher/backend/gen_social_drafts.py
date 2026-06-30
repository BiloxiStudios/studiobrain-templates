"""
Social Draft Generator — hashtag assembly for X/Twitter, Bluesky, Instagram, Threads.

SBAI-4358 fix: LLM prompts (e.g. Qwen) default to "no hashtags unless told",
so the raw LLM draft omits hashtags even when they are needed for discoverability.
This module builds per-topic hashtag suggestions and provides an assembly helper
that APPENDS them to the final draft text — guaranteeing hashtags are always
present regardless of the LLM's output.

Mirrors the youtube-manager metadata tag pattern: base tags + entity-specific tags
(e.g. #UnrealEngine + #<Device>), but adapted for short-form social platforms.
"""

import logging
from typing import Optional

logger = logging.getLogger("plugin.social-publisher.gen_social_drafts")

# ---------------------------------------------------------------------------
# Topic -> hashtag mappings
# ---------------------------------------------------------------------------

# UEFN / Verse / Fortnite Creative ecosystem tags
UEFN_TAGS = ["UEFN", "Verse", "FortniteCreative", "FortniteUEFN"]

# Unreal Engine ecosystem — broader reach
UNREAL_ENGINE_TAGS = ["UnrealEngine", "UE5", "GameDev"]

# Per-entity-type social hashtag set
# Keys are entity types (singular); values are lists of hashtag-worthy topics.
ENTITY_TYPE_TAGS: dict[str, list[str]] = {
    "character": ["CharacterDesign", "GameCharacter", "NPC"],
    "faction": ["WorldBuilding", "Lore"],
    "district": ["WorldBuilding", "GameMap", "LevelDesign"],
    "location": ["WorldBuilding", "GameMap", "LevelDesign"],
    "brand": ["BrandDesign", "InGameBrand"],
    "clothing": ["CharacterDesign", "GameFashion"],
    "vehicle": ["GameDesign", "VehicleDesign"],
    "weapon": ["GameDesign", "WeaponDesign"],
    "item": ["GameDesign", "GameItem"],
    "assembly": ["WorldBuilding", "Lore"],
    "timeline": ["Lore", "StoryDesign"],
}

# Device / feature tags — when entity data mentions specific UEFN devices
DEVICE_TAG_MAP: dict[str, str] = {
    "device": "Device",
    "prop": "Prop",
    "prefab": "Prefab",
    "verse": "Verse",
    "scene": "SceneGraph",
    "animation": "Animation",
    "vfx": "VFX",
    "sfx": "SFX",
    "lighting": "Lighting",
    "physics": "Physics",
    "ai": "AIAgent",
    "npc": "NPC",
    "dialogue": "DialogueSystem",
    "inventory": "InventorySystem",
    "quest": "QuestSystem",
    "combat": "CombatSystem",
    "spawner": "Spawner",
    "trigger": "Trigger",
    "ui": "UI",
    "hud": "HUD",
    "camera": "Camera",
    "audio": "Audio",
    "music": "Music",
}


def _suggested_tags(
    entity_type: str,
    entity_data: dict,
    *,
    include_uefn: bool = True,
    include_unreal: bool = True,
    max_tags: int = 15,
) -> list[str]:
    """
    Build a deduplicated list of hashtag suggestions for a social draft.

    Mirrors the youtube-manager metadata tag pattern:
      base_tags + entity-specific tags + device/feature tags

    Args:
        entity_type: The entity type (e.g. "character", "district").
        entity_data: The entity dict with fields like name, description, tags.
        include_uefn: Include #UEFN/#Verse/#FortniteCreative/#FortniteUEFN.
        include_unreal: Include #UnrealEngine/#UE5/#GameDev.
        max_tags: Maximum number of hashtags to return (platform limits vary).

    Returns:
        List of hashtag strings **without** the leading '#'.  Callers format
        them as needed (e.g. ``" ".join(f"#{t}" for t in tags)``).
    """
    tags: list[str] = []

    # 1. UEFN ecosystem tags (broadest reach for Fortnite Creative community)
    if include_uefn:
        tags.extend(UEFN_TAGS)

    # 2. Unreal Engine ecosystem tags
    if include_unreal:
        tags.extend(UNREAL_ENGINE_TAGS)

    # 3. Entity-type-specific tags
    type_tags = ENTITY_TYPE_TAGS.get(entity_type, [])
    tags.extend(type_tags)

    # 4. Entity's own tags field (if present on the entity)
    raw_tags = entity_data.get("tags", []) or []
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    for tag in raw_tags:
        # Convert to PascalCase-ish hashtag (strip spaces, capitalize words)
        cleaned = tag.strip().replace(" ", "").replace("-", "")
        if cleaned and len(cleaned) <= 30:
            # Title-case for readability
            tags.append(cleaned)

    # 5. Device / feature tags — scan entity name, description for device keywords
    searchable = " ".join(
        filter(
            None,
            [
                entity_data.get("name", ""),
                entity_data.get("description", ""),
                entity_data.get("summary", ""),
                entity_data.get("bio", ""),
            ],
        )
    ).lower()

    for keyword, device_tag in DEVICE_TAG_MAP.items():
        if keyword in searchable:
            tags.append(device_tag)

    # 6. Entity name as a hashtag (slugified, if short enough)
    entity_name = entity_data.get("name") or entity_data.get("title") or ""
    if entity_name:
        name_tag = entity_name.strip().replace(" ", "").replace("-", "")
        if name_tag and len(name_tag) <= 30 and name_tag.lower() not in [
            t.lower() for t in tags
        ]:
            tags.append(name_tag)

    # Deduplicate (preserve order, case-insensitive)
    seen: set[str] = set()
    deduped: list[str] = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(tag)

    return deduped[:max_tags]


def format_hashtags(tags: list[str], *, prefix: str = "#") -> str:
    """
    Format a list of tag strings into a hashtag block.

    Example: ``["UEFN", "Verse"]`` -> ``"#UEFN #Verse"``
    """
    return " ".join(f"{prefix}{t}" for t in tags)


def assemble_draft(
    llm_draft: str,
    suggested_tags: list[str],
    *,
    separator: str = "\n\n",
    append_always: bool = True,
) -> str:
    """
    Assemble the final social draft by appending suggested hashtags.

    SBAI-4358 fix: LLM prompts often say "no hashtags unless told", so the raw
    LLM output omits them. This function ensures hashtags are ALWAYS appended
    to the final draft, regardless of what the LLM produced.

    Args:
        llm_draft: The raw text from the LLM (may or may not contain hashtags).
        suggested_tags: Tag strings from ``_suggested_tags()`` (without '#').
        separator: String between draft body and hashtags.
        append_always: If True, hashtags are always appended even if the draft
            already contains some hashtags. This guarantees the curated tag set
            is present.

    Returns:
        The complete draft text ready for publishing.
    """
    if not suggested_tags:
        return llm_draft

    hashtag_block = format_hashtags(suggested_tags)

    if not append_always:
        # Only append if the draft doesn't already seem to have hashtags
        if "#" in llm_draft:
            return llm_draft

    return f"{llm_draft}{separator}{hashtag_block}"


def generate_social_draft_prompt(
    entity_type: str,
    entity_data: dict,
    platform: str = "twitter",
    *,
    include_hashtag_instruction: bool = True,
) -> str:
    """
    Build the LLM prompt for social draft generation.

    When ``include_hashtag_instruction`` is True (the default), the prompt
    explicitly tells the LLM to include hashtags — working around the default
    "no hashtags unless told" behavior.

    However, the REAL guarantee is in ``assemble_draft()`` which appends
    ``_suggested_tags()`` to the LLM output regardless.

    Args:
        entity_type: The entity type.
        entity_data: The entity dict.
        platform: Target platform ("twitter", "bluesky", "instagram", "threads").
        include_hashtag_instruction: Add hashtag instruction to the prompt.

    Returns:
        The prompt string to send to the LLM.
    """
    name = entity_data.get("name") or entity_data.get("title") or "Unnamed"
    description = (
        entity_data.get("description")
        or entity_data.get("summary")
        or entity_data.get("bio")
        or ""
    )

    platform_limits = {
        "twitter": 280,
        "bluesky": 300,
        "threads": 500,
        "instagram": 2200,
    }
    char_limit = platform_limits.get(platform, 280)

    prompt_parts = [
        f"Write a social media post for {platform} (max {char_limit} characters).",
        f"",
        f"Entity: {name}",
        f"Type: {entity_type}",
    ]

    if description:
        # Truncate description for prompt context
        short_desc = description[:200] + ("..." if len(description) > 200 else "")
        prompt_parts.append(f"Description: {short_desc}")

    prompt_parts.extend(
        [
            f"",
            f"Make it engaging and relevant to the gaming / game development community.",
        ]
    )

    if include_hashtag_instruction:
        tags = _suggested_tags(entity_type, entity_data)
        hashtag_str = format_hashtags(tags[:8])  # Show top 8 in prompt as hint
        prompt_parts.extend(
            [
                f"",
                f"Include these hashtags at the end of the post: {hashtag_str}",
            ]
        )

    return "\n".join(prompt_parts)
