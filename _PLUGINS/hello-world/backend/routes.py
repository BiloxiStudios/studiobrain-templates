"""
Hello World Plugin — sample routes.

Demonstrates the minimal structure a plugin needs to expose
a FastAPI router that the plugin loader will pick up.
Includes entity-scoped notes storage.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------------
# Data storage helpers
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "notes.json"


def _ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({}, indent=2))


def _read_data() -> dict:
    _ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_data(data: dict) -> None:
    _ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _entity_key(entity_type: str, entity_id: str) -> str:
    return f"{entity_type}:{entity_id}"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AddNoteRequest(BaseModel):
    entity_type: str
    entity_id: str
    text: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
async def hello():
    """Simple greeting endpoint."""
    return {
        "message": "Hello from the Hello World plugin!",
        "plugin": "hello-world",
        "version": "1.0.0",
    }


@router.get("/status")
async def status():
    """Plugin health check."""
    return {"status": "ok", "plugin": "hello-world"}


@router.get("/notes")
async def get_notes(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
):
    """Get all notes for an entity."""
    data = _read_data()
    key = _entity_key(entity_type, entity_id)
    return {"notes": data.get(key, [])}


@router.post("/notes")
async def add_note(req: AddNoteRequest):
    """Add a note to an entity."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Note text cannot be empty")
    data = _read_data()
    key = _entity_key(req.entity_type, req.entity_id)
    if key not in data:
        data[key] = []
    note = {
        "id": str(uuid.uuid4()),
        "text": req.text.strip(),
        "time": datetime.now(timezone.utc).isoformat(),
    }
    data[key].insert(0, note)
    _write_data(data)
    return note


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    entity_type: str = Query(...),
    entity_id: str = Query(...),
):
    """Delete a single note by ID."""
    data = _read_data()
    key = _entity_key(entity_type, entity_id)
    notes = data.get(key, [])
    original_len = len(notes)
    data[key] = [n for n in notes if n["id"] != note_id]
    if len(data[key]) == original_len:
        raise HTTPException(status_code=404, detail="Note not found")
    _write_data(data)
    return {"deleted": note_id}
