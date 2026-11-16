"""Збирає екрани. Карту отримує ззовні і не імпортує app.garden."""

from __future__ import annotations

import flet as ft

from app.contracts.ports import Actions, MakeCanvas


def mount(page: ft.Page, actions: Actions, make_canvas: MakeCanvas) -> None:
    raise NotImplementedError("app/shell/mount.py — див. TASK.md")
