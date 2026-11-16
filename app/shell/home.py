"""Головне меню: свайп у зону, друзі, налаштування, стан, список зон."""

from __future__ import annotations

import flet as ft

from app.contracts.ports import Actions


def home_view(actions: Actions, on_open_zone, on_friends, on_settings, on_status) -> ft.Control:
    raise NotImplementedError("app/shell/home.py — див. TASK.md")
