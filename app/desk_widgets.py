"""Знімок горщиків для віджетів робочого столу iPhone.

Пише JSON і картинки в Documents/HappyGardenWidgets. Нативний код застосунку
копіює цю теку в App Group, звідки їх читає WidgetKit.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from app.contracts.labels import STAGE_LABELS
from app.contracts.models import PotCard
from app.contracts.pictures import pot_picture

FOLDER = "HappyGardenWidgets"


def widget_root() -> Path:
    """Пісочниця iOS: HOME вказує на контейнер застосунку. На комп'ютері — тека користувача."""
    home = os.environ.get("CFFIXED_USER_HOME") or os.environ.get("HOME") or str(Path.home())
    root = Path(home) / "Documents" / FOLDER
    (root / "images").mkdir(parents=True, exist_ok=True)
    return root


def _assets() -> Path:
    return Path(__file__).resolve().parent.parent / "assets"


def load_pins() -> set[str]:
    path = widget_root() / "pins.json"
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {str(item) for item in data.get("ids", [])}


def save_pins(ids: set[str]) -> None:
    path = widget_root() / "pins.json"
    path.write_text(json.dumps({"ids": sorted(ids)}, ensure_ascii=False), encoding="utf-8")


def _percent(value: float) -> int:
    return int(round(value * 100 if value <= 1 else value))


def publish_pots(cards: list[PotCard] | tuple[PotCard, ...], pins: set[str] | None = None) -> None:
    """Оновлює state.json. Якщо pins не передано — лишає вже збережений вибір."""
    root = widget_root()
    images = root / "images"
    chosen = load_pins() if pins is None else set(pins)
    pots: list[dict[str, object]] = []
    keep: set[str] = set()
    for card in cards:
        picture = pot_picture(card.pot.profile.species_id, card.pot.stage)
        image = ""
        if picture:
            source = _assets() / picture
            if source.is_file():
                image = f"{card.pot.id}.png"
                shutil.copyfile(source, images / image)
                keep.add(image)
        pots.append(
            {
                "id": card.pot.id,
                "name": card.species.name,
                "stage": STAGE_LABELS.get(card.pot.stage, card.pot.stage.value),
                "health": _percent(card.pot.health),
                "glyph": card.species.glyph or "🌱",
                "image": image,
                "pinned": card.pot.id in chosen,
            }
        )
    for old in images.glob("*.png"):
        if old.name not in keep:
            old.unlink(missing_ok=True)
    (root / "state.json").write_text(json.dumps({"pots": pots}, ensure_ascii=False), encoding="utf-8")
