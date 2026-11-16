"""Форма посадки. Довідку бере з actions.describe, садить через actions.plant."""

from __future__ import annotations

import flet as ft

from app.contracts.ports import Actions


def plant_form(actions: Actions, zone_id: str, x: float, y: float, on_done, on_cancel) -> ft.Control:
    raise NotImplementedError("app/shell/plant_form.py — див. TASK.md")
