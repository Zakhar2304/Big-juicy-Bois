"""Точка входу Flet.

Поки фасад GardenActions не зібраний (база й довідка ще кидають NotImplementedError),
екрани працюють на FakeActions, очищеному до першого запуску: без зон, тож видно вхід.
Дані живуть лише до перезавантаження сторінки. Коли app/wiring буде готовий,
тут з'явиться збірка з app/wiring/TASK.md.
"""

try:
    import flet as ft
except ImportError as exc:
    raise SystemExit("Встанови залежності: pip install -r requirements.txt") from exc

from app.contracts.fakes import FakeActions
from app.contracts.models import Settings
from app.garden.map import GardenMap
from app.shell import mount


def _first_run_actions() -> FakeActions:
    """Тимчасово: вітрина без зон, щоб пройти екран входу."""
    actions = FakeActions()
    actions.zones.clear()
    actions.pots.clear()
    actions.groups.clear()
    actions.settings = Settings()
    return actions


def main(page: ft.Page) -> None:
    mount(page, _first_run_actions(), GardenMap)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
