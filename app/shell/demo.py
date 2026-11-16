"""Верстка на фейкових даних. Запуск: flet run app/shell/demo.py"""

import flet as ft

from app.contracts.fakes import FakeActions
from app.contracts.labels import APP_NAME, BTN_ENTER, BTN_FRIENDS, BTN_SETTINGS, BTN_STATUS, HINT_SWIPE


def main(page: ft.Page) -> None:
    actions = FakeActions()
    page.title = APP_NAME
    page.add(
        ft.SafeArea(
            content=ft.Column(
                [
                    ft.Text(APP_NAME, size=28),
                    ft.Text(HINT_SWIPE),
                    ft.Text(BTN_ENTER),
                    ft.Text(f"{BTN_FRIENDS} · {BTN_SETTINGS} · {BTN_STATUS}"),
                    ft.Text(f"Фейкових зон: {len(actions.list_zones())}. Заміни заглушки за TASK.md."),
                ]
            )
        )
    )


if __name__ == "__main__":
    ft.run(main)
