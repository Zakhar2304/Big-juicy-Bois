"""Які віджети показувати на головній. Окремо від Settings: у контракті такого поля немає."""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.shell.widget_facts import DEFAULT_IDS, normalize_ids

_FILE_NAME = "home_widgets.json"


def prefs_path() -> Path:
    home = os.environ.get("CFFIXED_USER_HOME") or os.environ.get("HOME") or str(Path.home())
    folder = Path(home) / "Documents" / "HappyGarden"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / _FILE_NAME


def load_ids(path: Path | None = None) -> tuple[str, ...]:
    try:
        file = path or prefs_path()
    except OSError:
        return DEFAULT_IDS
    if not file.exists():
        return DEFAULT_IDS
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_IDS
    if not isinstance(data, dict):
        return DEFAULT_IDS
    return normalize_ids(data.get("ids"))


def save_ids(ids: tuple[str, ...], path: Path | None = None) -> None:
    file = path or prefs_path()
    file.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"ids": list(normalize_ids(ids))}, ensure_ascii=False)
    tmp = file.with_suffix(".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(file)
