"""Точка входу HappyGarden. Сайт: flet run --web main.py

Екрани працюють на SavedGarden: ріст, довідка і погода як у PreviewActions,
а зони, горщики, журнал, друзі й налаштування читаються з
Documents/HappyGarden/garden.json.

Сцена зони — FarmBench (стіл із горщиками). Окрема полиця людини 3: flet run app/garden/demo.py
"""

try:
    import flet as ft
except ImportError as exc:
    raise SystemExit("Встанови залежності: pip install -r requirements.txt") from exc

from app.garden.farm import FarmBench
from app.memory import SavedGarden
from app.shell import mount


def main(page: ft.Page) -> None:
    mount(page, SavedGarden(), FarmBench)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
