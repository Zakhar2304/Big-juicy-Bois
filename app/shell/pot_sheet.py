"""Картка горщика: відсотки, етапи, полити / удобрити / зібрати."""

from __future__ import annotations

import flet as ft

from app.contracts.models import PotCard
from app.contracts.ports import Actions


def pot_sheet(actions: Actions, zone_id: str, card: PotCard, on_changed, on_close) -> ft.Control:
    raise NotImplementedError("app/shell/pot_sheet.py — див. TASK.md")
