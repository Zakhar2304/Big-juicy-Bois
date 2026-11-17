"""Точка входу HappyGarden. Сайт: flet run --web main.py

Поки база (людина 5) не готова, екрани працюють на PreviewActions: FakeActions без зон
(видно вхід), культури з species.json і справжня погода Open-Meteo. Дані живуть лише
до перезавантаження сторінки. Коли GardenActions запрацює, тут буде збірка з app/wiring/TASK.md.

Сцена зони — FarmBench (стіл із горщиками). Окрема полиця людини 3: flet run app/garden/demo.py
"""

try:
    import flet as ft
except ImportError as exc:
    raise SystemExit("Встанови залежності: pip install -r requirements.txt") from exc

from app.garden.farm import FarmBench
from app.shell import mount
from app.wiring import PreviewActions


def main(page: ft.Page) -> None:
    # Менше роботи на перший кадр: без зайвих відступів і з легким фоном оболонки.
    page.scroll = None
    mount(page, PreviewActions(), FarmBench)


if __name__ == "__main__":
    import os
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
    host = os.getenv("FLET_WEB_HOST", "127.0.0.1")
    port = int(os.getenv("FLET_WEB_PORT", "56950"))
    ft.run(
        main,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER,
        host=host,
        port=port,
        web_renderer=ft.WebRenderer.CANVAS_KIT,
        route_url_strategy=ft.RouteUrlStrategy.HASH,
    )
