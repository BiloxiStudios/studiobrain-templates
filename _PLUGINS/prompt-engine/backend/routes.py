"""
Prompt Engine Plugin — variable resolution routes.

Implements the cross-entity variable resolution engine described in
PROMPT_ENGINE_RULES.md (SBAI-1643).

Supported variable syntax
──────────────────────────
  $field                           local field on the current entity context
  $type.field                      cross-entity implicit (nearest entity of type)
  $type:entity_id.field            cross-entity explicit (pinned entity ID)
  $type:entity_id.path.to.field    explicit with arbitrary nested dot-path

Resolution pipeline
────────────────────
  1. Parse  — tokenise all $… tokens, validate syntax
  2. Plan   — deduplicate entity lookups, batch into minimum DB queries
  3. Fetch  — retrieve entities via the host app's entity service
  4. Resolve — walk nested dot-paths, apply fallback strategy
  5. Sanitise — HTML-escape, truncate to max_value_length per value
  6. Substitute — replace tokens in template text
"""

import html
import logging
import re
import time
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("plugin.prompt-engine")

router = APIRouter()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ENTITY_TYPES = {
    "character", "location", "item", "brand", "faction", "district",
    "quest", "dialogue", "event", "campaign", "timeline", "assembly",
    "job", "universe",
}

# Regex for a single variable token.
# Groups: (field_only) OR (type, optional_entity_id, field_path)
_TOKEN_RE = re.compile(
    r"\$(?:"
    r"(?P<type>[a-z_]+):(?P<entity_id>[a-z0-9_\-]+)\.(?P<explicit_path>[a-zA-Z0-9_.]+)"  # explicit
    r"|(?P<itype>[a-z_]+)\.(?P<implicit_path>[a-zA-Z0-9_.]+)"                              # implicit
    r"|(?P<local>[a-zA-Z0-9_]+)"                                                            # local
    r")"
)

_RESOLVER_CACHE: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at; 0 means no-expiry)

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class VariableToken(BaseModel):
    token: str
    form: str          # "local" | "implicit" | "explicit"
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    field_path: str


class ParseResponse(BaseModel):
    tokens: list[VariableToken]
    errors: list[str]


class ResolveRequest(BaseModel):
    template_text: str = Field(..., description="Raw prompt text containing $variable tokens")
    context_entity_type: Optional[str] = Field(
        None, description="Entity type of the current context entity (for local and implicit resolution)"
    )
    context_entity_id: Optional[str] = Field(
        None, description="Entity ID of the current context entity"
    )
    strict_mode: bool = Field(True, description="Fail on first unresolvable required variable")
    fallback_strategy: str = Field(
        "empty_string",
        description="empty_string | placeholder | skip | error",
    )
    cache_ttl: int = Field(300, description="Cache TTL in seconds (0 = disabled)")
    max_value_length: int = Field(1000, description="Max chars per resolved value")


class ResolvedVariable(BaseModel):
    token: str
    resolved_value: Optional[str]
    error: Optional[str] = None


class ResolveResponse(BaseModel):
    resolved_text: str
    variables: list[ResolvedVariable]
    resolution_time_ms: float
    errors: list[str]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_tokens(template_text: str) -> tuple[list[VariableToken], list[str]]:
    """Extract and validate all $variable tokens from template_text."""
    tokens: list[VariableToken] = []
    errors: list[str] = []
    seen: set[str] = set()

    for m in _TOKEN_RE.finditer(template_text):
        raw = m.group(0)
        if raw in seen:
            continue
        seen.add(raw)

        if m.group("local"):
            tokens.append(VariableToken(
                token=raw,
                form="local",
                field_path=m.group("local"),
            ))
        elif m.group("itype"):
            entity_type = m.group("itype")
            if entity_type not in VALID_ENTITY_TYPES:
                errors.append(
                    f"Unknown entity type '{entity_type}' in token '{raw}' (pe_002)"
                )
                continue
            tokens.append(VariableToken(
                token=raw,
                form="implicit",
                entity_type=entity_type,
                field_path=m.group("implicit_path"),
            ))
        elif m.group("type"):
            entity_type = m.group("type")
            if entity_type not in VALID_ENTITY_TYPES:
                errors.append(
                    f"Unknown entity type '{entity_type}' in token '{raw}' (pe_002)"
                )
                continue
            tokens.append(VariableToken(
                token=raw,
                form="explicit",
                entity_type=entity_type,
                entity_id=m.group("entity_id"),
                field_path=m.group("explicit_path"),
            ))

    return tokens, errors


# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------


def _cache_get(key: str) -> Optional[Any]:
    entry = _RESOLVER_CACHE.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    # expires_at == 0 means the entry was stored with ttl=0 — this path never
    # occurs because _cache_set returns early when ttl <= 0, but guard anyway.
    if expires_at != 0 and time.monotonic() > expires_at:
        del _RESOLVER_CACHE[key]
        return None
    return value


def _cache_set(key: str, value: Any, ttl: int) -> None:
    if ttl <= 0:
        return
    _RESOLVER_CACHE[key] = (value, time.monotonic() + ttl)


def _resolve_dot_path(data: dict, path: str) -> tuple[Any, Optional[str]]:
    """Walk *data* along dot-separated *path*. Return (value, error)."""
    parts = path.split(".")
    current: Any = data
    for part in parts:
        if not isinstance(current, dict):
            return None, f"Field '{part}' not accessible on non-mapping value"
        if part not in current:
            return None, f"Field '{part}' not found"
        current = current[part]
    return current, None


def _serialise_value(value: Any) -> str:
    """Serialise any Python value to a string for substitution."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def _sanitise(value: str, max_len: int) -> str:
    """HTML-escape and truncate resolved value (pe_030)."""
    escaped = html.escape(value, quote=False)
    if len(escaped) > max_len:
        escaped = escaped[:max_len]
    return escaped


async def _fetch_entity(
    request: Request,
    entity_type: str,
    entity_id: Optional[str],
    context_entity_type: Optional[str],
    context_entity_id: Optional[str],
) -> tuple[Optional[dict], Optional[str]]:
    """
    Retrieve an entity from the host application's entity service.

    The host app is expected to expose a service at `request.app.state.entity_service`
    with a `get_entity(entity_type, entity_id) -> dict | None` coroutine and a
    `find_nearest(entity_type, context_type, context_id) -> dict | None` coroutine
    for implicit resolution.

    Returns (entity_data, error_message).
    """
    svc = getattr(getattr(request.app, "state", None), "entity_service", None)
    if svc is None:
        return None, "Entity service not available"

    try:
        if entity_id:
            entity = await svc.get_entity(entity_type, entity_id)
            if entity is None:
                return None, f"Entity '{entity_type}:{entity_id}' not found (pe_010)"
            return entity, None
        else:
            # Implicit resolution — nearest entity of this type given current context
            entity = await svc.find_nearest(entity_type, context_entity_type, context_entity_id)
            if entity is None:
                return None, f"No '{entity_type}' entity found in current context (pe_011)"
            return entity, None
    except Exception as exc:
        logger.exception("Entity fetch error for %s:%s", entity_type, entity_id)
        return None, f"Entity fetch error: {exc}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/")
async def root():
    """Plugin health check."""
    return {"plugin": "prompt-engine", "version": "1.0.0", "status": "ok"}


@router.get("/status")
async def status():
    return {"status": "ok", "plugin": "prompt-engine", "cache_entries": len(_RESOLVER_CACHE)}


@router.post("/parse", response_model=ParseResponse)
async def parse_template(body: dict):
    """
    Parse a prompt template and return all discovered variable tokens.
    Does NOT resolve values — useful for validation and UI highlighting.
    """
    template_text = body.get("template_text", "")
    if not isinstance(template_text, str):
        raise HTTPException(status_code=400, detail="template_text must be a string")

    tokens, errors = _parse_tokens(template_text)
    return ParseResponse(tokens=tokens, errors=errors)


@router.post("/resolve", response_model=ResolveResponse)
async def resolve_template(req: ResolveRequest, request: Request):
    """
    Resolve all $variable tokens in *template_text* using live entity data.

    Resolution pipeline:
      1. Parse tokens
      2. Deduplicate + batch entity lookups
      3. Fetch entities
      4. Walk dot-paths
      5. Sanitise values
      6. Substitute into template
    """
    start = time.monotonic()
    tokens, parse_errors = _parse_tokens(req.template_text)

    if parse_errors and req.strict_mode:
        raise HTTPException(
            status_code=422,
            detail={"message": "Template parse errors (strict_mode)", "errors": parse_errors},
        )

    all_errors: list[str] = list(parse_errors)
    resolved_vars: list[ResolvedVariable] = []
    substitutions: dict[str, str] = {}

    # ── Step 2: deduplicate entity lookups ──────────────────────────────────
    entity_keys: set[tuple[str, Optional[str]]] = set()
    for tok in tokens:
        if tok.form in ("implicit", "explicit"):
            entity_keys.add((tok.entity_type, tok.entity_id))

    # ── Step 3: batch-fetch entities ────────────────────────────────────────
    entity_cache: dict[tuple[str, Optional[str]], tuple[Optional[dict], Optional[str]]] = {}
    for etype, eid in entity_keys:
        cache_key = f"{etype}:{eid or '__implicit__'}:{req.context_entity_type}:{req.context_entity_id}"
        cached = _cache_get(cache_key)
        if cached is not None:
            entity_cache[(etype, eid)] = (cached, None)
        else:
            entity_data, err = await _fetch_entity(
                request, etype, eid, req.context_entity_type, req.context_entity_id
            )
            entity_cache[(etype, eid)] = (entity_data, err)
            if entity_data is not None:
                _cache_set(cache_key, entity_data, req.cache_ttl)

    # ── Steps 4–6: resolve, sanitise, substitute ────────────────────────────
    for tok in tokens:
        resolved_value: Optional[str] = None
        error: Optional[str] = None

        if tok.form == "local":
            # Resolve from context entity
            if req.context_entity_id and req.context_entity_type:
                ctx_data, ctx_err = await _fetch_entity(
                    request,
                    req.context_entity_type,
                    req.context_entity_id,
                    None,
                    None,
                )
                if ctx_err:
                    error = ctx_err
                else:
                    raw_val, path_err = _resolve_dot_path(ctx_data or {}, tok.field_path)
                    if path_err:
                        error = path_err
                    else:
                        resolved_value = _sanitise(
                            _serialise_value(raw_val), req.max_value_length
                        )
            else:
                error = "No context entity provided for local variable resolution"

        elif tok.form in ("implicit", "explicit"):
            entity_data, fetch_err = entity_cache.get((tok.entity_type, tok.entity_id), (None, "not fetched"))
            if fetch_err:
                error = fetch_err
            else:
                raw_val, path_err = _resolve_dot_path(entity_data or {}, tok.field_path)
                if path_err:
                    error = path_err
                else:
                    resolved_value = _sanitise(
                        _serialise_value(raw_val), req.max_value_length
                    )

        # ── Apply fallback strategy ──────────────────────────────────────────
        if error:
            all_errors.append(f"{tok.token}: {error}")
            if req.strict_mode or req.fallback_strategy == "error":
                raise HTTPException(
                    status_code=422,
                    detail={"message": f"Unresolvable variable (strict_mode): {tok.token}", "errors": all_errors},
                )
            elif req.fallback_strategy == "placeholder":
                substitutions[tok.token] = tok.token
            elif req.fallback_strategy == "skip":
                # Mark token with a sentinel; sentences containing it are
                # stripped after all substitutions are complete.
                substitutions[tok.token] = f"\x00SKIP:{tok.token}\x00"
            else:  # empty_string
                substitutions[tok.token] = ""
        else:
            substitutions[tok.token] = resolved_value or ""

        resolved_vars.append(ResolvedVariable(
            token=tok.token,
            resolved_value=substitutions.get(tok.token),
            error=error,
        ))

    # ── Substitute all tokens in order of length (longest first) ────────────
    resolved_text = req.template_text
    for token in sorted(substitutions.keys(), key=len, reverse=True):
        resolved_text = resolved_text.replace(token, substitutions[token])

    # ── Apply "skip" post-processing: remove sentences with sentinel markers ─
    if req.fallback_strategy == "skip" and "\x00SKIP:" in resolved_text:
        # Process line by line to avoid cross-line backtracking. Within each
        # line, split on sentence-ending punctuation and drop fragments that
        # contain an unresolved-variable sentinel. This approach is linear and
        # avoids polynomial backtracking on inputs with many repeated spaces.
        clean_lines = []
        for line in resolved_text.splitlines(keepends=True):
            if "\x00SKIP:" not in line:
                clean_lines.append(line)
                continue
            # Split the line on sentence terminators, preserving the terminator.
            parts = re.split(r"(?<=[.!?])\s*", line)
            kept = [p for p in parts if "\x00SKIP:" not in p]
            clean_lines.append(" ".join(kept).strip())
        resolved_text = "".join(clean_lines)
        # Strip any leftover sentinels not caught by the line splitter.
        resolved_text = resolved_text.replace("\x00", "")
        resolved_text = re.sub(r"SKIP:[^ ]*", "", resolved_text)
        # Collapse multiple spaces left by removals.
        resolved_text = " ".join(resolved_text.split())

    resolution_time_ms = (time.monotonic() - start) * 1000
    logger.info(
        "[prompt-engine] Resolved %d token(s) in %.1f ms",
        len(tokens),
        resolution_time_ms,
    )

    return ResolveResponse(
        resolved_text=resolved_text,
        variables=resolved_vars,
        resolution_time_ms=resolution_time_ms,
        errors=all_errors,
    )


@router.post("/cache/invalidate")
async def invalidate_cache(body: dict):
    """
    Invalidate cache entries for a given entity (called on entity.updated events).
    Accepts {entity_type, entity_id} and removes all matching cache keys.
    """
    entity_type = body.get("entity_type", "")
    entity_id = body.get("entity_id", "")
    prefix = f"{entity_type}:{entity_id}"
    removed = [k for k in list(_RESOLVER_CACHE) if k.startswith(prefix)]
    for k in removed:
        del _RESOLVER_CACHE[k]
    return {"invalidated": len(removed), "prefix": prefix}
