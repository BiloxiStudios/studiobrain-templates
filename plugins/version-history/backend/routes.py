"""
Version History Plugin — Backend Routes

Provides git-backed version history for entity markdown files.
Endpoints for listing commits, viewing diffs, and rolling back to
previous versions.  All git operations target the A:\\Brains repository.
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException

router = APIRouter()
logger = logging.getLogger("plugin.version-history")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BRAINS_ROOT = Path(r"A:\Brains")

# Mapping of entity_type -> (folder_name, file_prefix)
ENTITY_MAP = {
    "character":  ("Characters",  "CH_"),
    "location":   ("Locations",   "LOC_"),
    "brand":      ("Brands",      "BR_"),
    "district":   ("Districts",   "DIST_"),
    "faction":    ("Factions",    "FACT_"),
    "item":       ("Items",       "ITEM_"),
    "job":        ("Jobs",        "JOB_"),
    "quest":      ("Quests",      "QUEST_"),
    "event":      ("Events",      "EVENT_"),
    "campaign":   ("Campaigns",   "CAMP_"),
    "assembly":   ("Assemblies",  "ASSM_"),
}


def _entity_file(entity_type: str, entity_id: str) -> Path:
    """Resolve the canonical markdown file for an entity."""
    mapping = ENTITY_MAP.get(entity_type)
    if not mapping:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
    folder, prefix = mapping
    return BRAINS_ROOT / folder / entity_id / f"{prefix}{entity_id}.md"


def _relative_path(full_path: Path) -> str:
    """Return the path relative to BRAINS_ROOT (forward-slash for git)."""
    return str(full_path.relative_to(BRAINS_ROOT)).replace("\\", "/")


async def _run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command asynchronously in the Brains repo."""
    cmd = ["git", "-C", str(BRAINS_ROOT)] + list(args)
    logger.debug("git %s", " ".join(args))

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        ),
    )
    if check and result.returncode != 0:
        logger.error("git error: %s", result.stderr.strip())
        raise HTTPException(status_code=500, detail=f"Git error: {result.stderr.strip()}")
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def index():
    """Plugin status / health check."""
    return {
        "plugin": "version-history",
        "version": "1.0.0",
        "status": "ok",
    }


@router.get("/history/{entity_type}/{entity_id}")
async def get_history(entity_type: str, entity_id: str, limit: int = 50):
    """Return the git log for a specific entity file.

    Each entry includes commit hash, author, date, and message.
    """
    entity_path = _entity_file(entity_type, entity_id)
    rel_path = _relative_path(entity_path)

    # Check the file exists (it might be tracked but deleted — still fine)
    if not entity_path.exists():
        # Try to see if git knows about it at all
        probe = await _run_git("log", "--oneline", "-1", "--", rel_path, check=False)
        if not probe.stdout.strip():
            raise HTTPException(status_code=404, detail=f"Entity file not found: {rel_path}")

    # Use a NUL-delimited format so we can parse reliably
    separator = "---COMMIT---"
    fmt = f"{separator}%n%H%n%an%n%ae%n%aI%n%s"

    result = await _run_git(
        "log",
        f"--max-count={limit}",
        f"--format={fmt}",
        "--follow",
        "--",
        rel_path,
    )

    raw = result.stdout.strip()
    if not raw:
        return {"entity_type": entity_type, "entity_id": entity_id, "commits": []}

    commits: List[dict] = []
    blocks = [b.strip() for b in raw.split(separator) if b.strip()]
    for block in blocks:
        lines = block.split("\n", 4)
        if len(lines) < 4:
            continue
        commits.append({
            "sha": lines[0],
            "author_name": lines[1],
            "author_email": lines[2],
            "date": lines[3],
            "message": lines[4] if len(lines) > 4 else "",
        })

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "file": rel_path,
        "total": len(commits),
        "commits": commits,
    }


@router.get("/diff/{entity_type}/{entity_id}/{commit_sha}")
async def get_diff(entity_type: str, entity_id: str, commit_sha: str, context: int = 3):
    """Return the unified diff introduced by *commit_sha* for the entity file.

    If the commit is the very first one that introduced the file, a full-file
    diff is shown instead of a parent comparison.
    """
    entity_path = _entity_file(entity_type, entity_id)
    rel_path = _relative_path(entity_path)

    # Validate commit exists
    verify = await _run_git("cat-file", "-t", commit_sha, check=False)
    if verify.stdout.strip() != "commit":
        raise HTTPException(status_code=404, detail=f"Commit not found: {commit_sha}")

    # Check if this commit has a parent
    parent_check = await _run_git("rev-parse", f"{commit_sha}^", check=False)
    has_parent = parent_check.returncode == 0

    if has_parent:
        diff_result = await _run_git(
            "diff",
            f"-U{context}",
            f"{commit_sha}^",
            commit_sha,
            "--",
            rel_path,
            check=False,
        )
    else:
        # First commit — show diff against empty tree
        diff_result = await _run_git(
            "diff",
            f"-U{context}",
            "--diff-filter=A",
            "4b825dc642cb6eb9a060e54bf899d15363d7b169",
            commit_sha,
            "--",
            rel_path,
            check=False,
        )

    # Also grab the commit metadata
    meta = await _run_git("log", "-1", "--format=%H%n%an%n%ae%n%aI%n%s", commit_sha)
    meta_lines = meta.stdout.strip().split("\n", 4)

    # Grab stat summary
    if has_parent:
        stat_result = await _run_git(
            "diff", "--stat", f"{commit_sha}^", commit_sha, "--", rel_path, check=False,
        )
    else:
        stat_result = await _run_git(
            "diff", "--stat", "4b825dc642cb6eb9a060e54bf899d15363d7b169", commit_sha, "--", rel_path, check=False,
        )

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "commit": {
            "sha": meta_lines[0] if len(meta_lines) > 0 else commit_sha,
            "author_name": meta_lines[1] if len(meta_lines) > 1 else "",
            "author_email": meta_lines[2] if len(meta_lines) > 2 else "",
            "date": meta_lines[3] if len(meta_lines) > 3 else "",
            "message": meta_lines[4] if len(meta_lines) > 4 else "",
        },
        "diff": diff_result.stdout,
        "stat": stat_result.stdout.strip(),
    }


@router.post("/rollback/{entity_type}/{entity_id}/{commit_sha}")
async def rollback(entity_type: str, entity_id: str, commit_sha: str):
    """Restore the entity file to its state at *commit_sha*.

    This checks out the file content from the given commit and creates a new
    commit recording the rollback.
    """
    entity_path = _entity_file(entity_type, entity_id)
    rel_path = _relative_path(entity_path)

    # Validate commit
    verify = await _run_git("cat-file", "-t", commit_sha, check=False)
    if verify.stdout.strip() != "commit":
        raise HTTPException(status_code=404, detail=f"Commit not found: {commit_sha}")

    # Retrieve file content at that commit
    show_result = await _run_git("show", f"{commit_sha}:{rel_path}", check=False)
    if show_result.returncode != 0:
        raise HTTPException(
            status_code=404,
            detail=f"File not found at commit {commit_sha[:8]}: {show_result.stderr.strip()}",
        )

    old_content = show_result.stdout

    # Write the content to disk
    entity_path.parent.mkdir(parents=True, exist_ok=True)
    entity_path.write_text(old_content, encoding="utf-8")

    # Stage and commit
    await _run_git("add", rel_path)
    commit_msg = f"Rollback {entity_type} '{entity_id}' to {commit_sha[:8]}"
    commit_result = await _run_git("commit", "-m", commit_msg, "--", rel_path, check=False)

    if commit_result.returncode != 0:
        # Possible that the file is identical — no changes to commit
        if "nothing to commit" in commit_result.stdout or "no changes added" in commit_result.stdout:
            return {
                "status": "no_change",
                "message": f"Entity already matches commit {commit_sha[:8]}",
                "entity_type": entity_type,
                "entity_id": entity_id,
            }
        raise HTTPException(status_code=500, detail=f"Commit failed: {commit_result.stderr.strip()}")

    # Get the new commit sha
    new_sha = await _run_git("rev-parse", "HEAD")

    return {
        "status": "ok",
        "message": f"Rolled back to {commit_sha[:8]}",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "rolled_back_to": commit_sha,
        "new_commit": new_sha.stdout.strip(),
    }


@router.get("/stats")
async def get_stats():
    """Return aggregate version history statistics across all entities.

    Used by the plugin dashboard page.
    """
    stats: dict = {
        "total_commits": 0,
        "entity_types": {},
        "recent_changes": [],
    }

    for entity_type, (folder, prefix) in ENTITY_MAP.items():
        folder_path = BRAINS_ROOT / folder
        if not folder_path.exists():
            continue

        # Count commits touching files in this folder
        result = await _run_git(
            "log", "--oneline", "--max-count=500", "--", f"{folder}/", check=False,
        )
        count = len([l for l in result.stdout.strip().split("\n") if l.strip()]) if result.stdout.strip() else 0
        if count > 0:
            stats["entity_types"][entity_type] = count
            stats["total_commits"] += count

    # Recent changes across the whole repo (entity files only)
    entity_dirs = [f"{folder}/" for folder, _ in ENTITY_MAP.values()]
    recent_result = await _run_git(
        "log",
        "--max-count=20",
        "--format=---COMMIT---%n%H%n%an%n%aI%n%s",
        "--name-only",
        "--",
        *entity_dirs,
        check=False,
    )

    if recent_result.stdout.strip():
        blocks = [b.strip() for b in recent_result.stdout.split("---COMMIT---") if b.strip()]
        for block in blocks:
            lines = block.split("\n")
            if len(lines) < 4:
                continue
            files = [l.strip() for l in lines[4:] if l.strip()]
            stats["recent_changes"].append({
                "sha": lines[0],
                "author": lines[1],
                "date": lines[2],
                "message": lines[3],
                "files": files[:5],
            })

    return stats


@router.get("/file-at/{entity_type}/{entity_id}/{commit_sha}")
async def get_file_at_commit(entity_type: str, entity_id: str, commit_sha: str):
    """Return the full content of the entity file at a specific commit."""
    entity_path = _entity_file(entity_type, entity_id)
    rel_path = _relative_path(entity_path)

    result = await _run_git("show", f"{commit_sha}:{rel_path}", check=False)
    if result.returncode != 0:
        raise HTTPException(status_code=404, detail=f"File not found at commit {commit_sha[:8]}")

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "commit_sha": commit_sha,
        "content": result.stdout,
    }
