"""Запуск: flet run app/garden/demo.py"""

import flet as ft

from app.contracts.labels import APP_NAME


def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.add(ft.SafeArea(content=ft.Text("Карта грядки. Реалізуй app/garden за TASK.md.")))


if __name__ == "__main__":
    ft.run(main)
