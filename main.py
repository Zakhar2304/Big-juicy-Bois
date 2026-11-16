"""Полиця HappyGarden. Сайт: flet run --web main.py"""

try:
    import flet as ft
except ImportError as exc:
    raise SystemExit("Встанови залежності: pip install -r requirements.txt") from exc

from app.garden.bench import main

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
