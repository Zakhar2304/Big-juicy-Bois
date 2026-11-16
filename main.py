"""Точка входу HappyGarden. Сайт: flet run --web main.py

Поки фасад GardenActions не зібраний (база й довідка ще кидають NotImplementedError),
екрани працюють на FakeActions, очищеному до першого запуску: без зон, тож видно вхід.
Дані живуть лише до перезавантаження сторінки.

Сцена зони — FarmBench (стіл із горщиками). Окрема полиця людини 3: flet run app/garden/demo.py
"""

try:
    import flet as ft
except ImportError as exc:
    raise SystemExit("Встанови залежності: pip install -r requirements.txt") from exc

import json
from pathlib import Path

from app.contracts.codec import species_from_dict
from app.contracts.fakes import FakeActions
from app.contracts.models import Settings
from app.garden.farm import FarmBench
from app.shell import mount


SPECIES_FILE = Path(__file__).resolve().parent / "app" / "knowledge" / "data" / "species.json"


def _catalog() -> list:
    """Культури з довідки людини 4, поки FarmingCatalog не готовий."""
    raw = json.loads(SPECIES_FILE.read_text(encoding="utf-8"))
    return [species_from_dict(item) for item in raw["species"]]


def _first_run_actions() -> FakeActions:
    """Тимчасово: вітрина без зон, щоб пройти екран входу. Культури — з species.json."""
    actions = FakeActions()
    actions.species = _catalog()
    actions.zones.clear()
    actions.pots.clear()
    actions.groups.clear()
    actions.settings = Settings()
    return actions


def main(page: ft.Page) -> None:
    mount(page, _first_run_actions(), FarmBench)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
