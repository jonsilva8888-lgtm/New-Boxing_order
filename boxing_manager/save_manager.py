"""JSON save manager with unlimited named save slots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SAVE_DIR = Path(__file__).with_name("saves")
SAVE_DIR.mkdir(exist_ok=True)

class SaveError(RuntimeError):
    """Raised when save data cannot be read or validated."""

def save_game(career: Any, slot: str = "autosave") -> Path:
    """Write a career object to a named JSON save slot."""
    clean = "".join(ch for ch in slot if ch.isalnum() or ch in {"-", "_"}).strip() or "autosave"
    path = SAVE_DIR / f"{clean}.json"
    path.write_text(json.dumps(career.to_dict(), indent=2), encoding="utf-8")
    return path

def list_saves() -> list[str]:
    """Return all save slots sorted by name."""
    return sorted(path.stem for path in SAVE_DIR.glob("*.json"))

def load_raw(slot: str) -> dict[str, Any]:
    """Read raw save data from a slot."""
    path = SAVE_DIR / f"{slot}.json"
    if not path.exists():
        raise SaveError(f"No save slot named {slot!r}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SaveError(f"Save slot {slot!r} is corrupted") from exc
