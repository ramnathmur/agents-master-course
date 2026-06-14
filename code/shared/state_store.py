"""
Atomic file-based state store introduced in Chapter 11.

state.json is the contract between agents.
    - read_state()    -> dict
    - write_state(d)  -> atomic overwrite (write to tmp, rename)
    - append_facts(f) -> additive update to a list field
    - mark_phase_complete(name) -> set boolean flag

For multi-process concurrency, a more robust store would use file locks
(portalocker, fcntl) or a real DB. This is the teaching version — clear, small,
restart-safe within a single producer / single consumer.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


DEFAULT_PATH = Path("./state.json").resolve()


def initial_state() -> dict:
    """Return a fresh state dict. Public so callers can reset cleanly."""
    return {
        "schema_version": 1,
        "facts": [],
        "phases": {"research": False, "writing": False},
        "artifacts": {},
    }


def reset_state(path: Path = DEFAULT_PATH) -> None:
    """Overwrite the store with a fresh initial state."""
    write_state(initial_state(), path)


def read_state(path: Path = DEFAULT_PATH) -> dict:
    if not path.exists():
        return initial_state()
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(state: dict, path: Path = DEFAULT_PATH) -> None:
    """Atomic write: temp file in same dir, then os.replace."""
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=parent, prefix=".state-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def append_facts(facts: list[dict], path: Path = DEFAULT_PATH) -> None:
    state = read_state(path)
    state["facts"].extend(facts)
    write_state(state, path)


def mark_phase_complete(name: str, path: Path = DEFAULT_PATH) -> None:
    state = read_state(path)
    state["phases"][name] = True
    write_state(state, path)


def is_phase_complete(name: str, path: Path = DEFAULT_PATH) -> bool:
    return read_state(path)["phases"].get(name, False)
