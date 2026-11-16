"""Екран зони: карта, банер погоди, кнопки догляду і посадки."""

from __future__ import annotations

import flet as ft

from app.contracts.models import ZoneView
from app.contracts.ports import Actions, GardenCanvas


def zone_view(
    actions: Actions,
    view: ZoneView,
    canvas: GardenCanvas,
    on_back,
    on_changed,
) -> ft.Control:
    raise NotImplementedError("app/shell/zone_page.py — див. TASK.md")
