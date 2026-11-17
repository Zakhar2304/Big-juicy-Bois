"""Зберігає сесію локально (файл у Documents)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.auth.client import AuthSession

_FILE_NAME = "auth_session.json"


def _path() -> Path:
    home = os.environ.get("CFFIXED_USER_HOME") or os.environ.get("HOME") or str(Path.home())
    folder = Path(home) / "Documents" / "HappyGarden"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / _FILE_NAME


class SessionStore:
    def load(self) -> AuthSession | None:
        path = _path()
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(data, dict):
            return None
        return AuthSession.from_dict(data)

    def save(self, session: AuthSession) -> None:
        path = _path()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(session.to_dict()), encoding="utf-8")
        tmp.replace(path)

    def clear(self) -> None:
        path = _path()
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
