"""Names that belong to one sample setting, not to a default starter pack.

Default rules and templates must stay setting-neutral. The optional City of
Brains sample packs are outside the roots this module scans. Keep the list
here and only here.
"""
from __future__ import annotations

import re
from pathlib import Path

# One place for the setting's names, places, factions, and the era and
# art-direction words the default packs used to prescribe.
SETTING_NAME_PATTERNS: tuple[str, ...] = (
    r"City of Brains",
    r"city_of_brains",
    r"Double Dip",
    r"double_dip",
    r"Brain OnLine",
    r"BrainOnLine",
    r"BOL Network",
    r"BOL terminal",
    r"ELJ",
    r"Central Nervous",
    r"Rusty McDaniels",
    r"rusty_mcdaniels",
    r"Gear Head",
    r"NeuroNuggets",
    r"Northside Bears",
    r"Westside Krakens",
    r"Eastside Dragons",
    r"Southside Flamingos",
    r"Krakens",
    r"BrainBucks",
    r"low-poly luxe",
    r"low_poly_luxe",
    r"low_poly_stylized",
    r"alternate 1990s",
    r"alternate_1990s",
    r"synthwave",
    r"1990s",
    r"\b1998\b",
    r"payphone",
    r"\bVHS\b",
    r"Orbitron",
)

DEFAULT_RELATIVE_ROOTS: tuple[str, ...] = (
    "rules",
    "templates/Standard",
    "templates/Core",
    "templates/Layouts",
    "templates/Packs/core-essentials",
    "templates/Packs/full-starter",
    "templates/Packs/starter-characters",
    "templates/Packs/starter-locations",
    "templates/Packs/starter-factions",
    "templates/Packs/starter-brands",
    "templates/Packs/starter-jobs",
    "templates/Packs/starter-items",
    "templates/Packs/format-social-micro",
)

# Optional sample content. It may name the setting. It is not a default.
EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        "ExampleImplementation",
        "starter-assemblies",
        "sample-city-of-brains",
    }
)

_TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml"}
_PATTERN = re.compile("|".join(f"(?:{p})" for p in SETTING_NAME_PATTERNS), re.IGNORECASE)


def scan_roots(repo_root: Path, relative_roots: tuple[str, ...] = DEFAULT_RELATIVE_ROOTS) -> list[str]:
    """Return 'path:line: text' hits under the default roots."""
    hits: list[str] = []
    for rel in relative_roots:
        base = repo_root / rel
        if not base.exists():
            hits.append(f"{rel}: missing default root")
            continue
        files = [base] if base.is_file() else sorted(p for p in base.rglob("*") if p.is_file())
        for path in files:
            if path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                if _PATTERN.search(line):
                    rel_path = path.relative_to(repo_root)
                    hits.append(f"{rel_path}:{lineno}: {line.strip()}")
    return hits
