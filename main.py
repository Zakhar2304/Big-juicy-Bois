"""Точка входу Flet. Поки папки не зібрані, показує каркас.

Людина ядра замінює тіло main() на збірку з app/wiring/TASK.md,
коли методи GardenActions більше не кидають NotImplementedError.
"""

try:
    import flet as ft
except ImportError as exc:
    raise SystemExit("Встанови залежності: pip install -r requirements.txt") from exc

from app.contracts.labels import APP_NAME, SUBTITLE


def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                [
                    ft.Text(APP_NAME, size=32, weight=ft.FontWeight.BOLD),
                    ft.Text(SUBTITLE),
                    ft.Text("Каркас хакатону. Кожна папка має свій TASK.md."),
                    ft.Text("1. app/core і app/wiring — людина з Opus"),
                    ft.Text("2. app/shell — меню і форми"),
                    ft.Text("3. app/garden — карта"),
                    ft.Text("4. app/knowledge — довідка і погода"),
                    ft.Text("5. app/storage — база, нагадування, картки"),
                ],
                spacing=8,
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)
