"""Екран зони: сцена з полотна, назад, назва зони і форма посадки поверх сцени."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.contracts.labels import BTN_BACK, ZONE_LABELS
from app.contracts.models import ZoneView
from app.contracts.ports import Actions, GardenCanvas
from app.shell.plant_form import plant_form
from app.shell.theme import CARD, GREEN, MIN_TAP, TEXT, fill

_SHADOW = ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.18, TEXT), offset=ft.Offset(0, 4))


def zone_view(
    actions: Actions,
    view: ZoneView,
    canvas: GardenCanvas,
    on_back: Callable[[], None],
    on_changed: Callable[[ZoneView], None],
) -> ft.Control:
    zone = view.zone
    overlay = ft.Stack(left=0, top=0, right=0, bottom=0)

    def close_form() -> None:
        overlay.controls = []
        overlay.update()

    def planted(new_view: ZoneView) -> None:
        close_form()
        canvas.show(new_view)
        on_changed(new_view)

    def open_form() -> None:
        x, y = canvas.spawn_point()
        overlay.controls = [plant_form(actions, zone.id, x, y, planted, close_form)]
        overlay.update()

    # Сцена, що вміє «+» на вільному місці (FarmBench), кличе форму посадки.
    if hasattr(canvas, "on_add"):
        canvas.on_add = open_form
    canvas.show(view)

    back = ft.Container(
        width=MIN_TAP + 4,
        height=MIN_TAP + 4,
        border_radius=MIN_TAP,
        bgcolor=ft.Colors.with_opacity(0.9, CARD),
        shadow=_SHADOW,
        ink=True,
        tooltip=BTN_BACK,
        on_click=lambda _: on_back(),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, color=GREEN),
    )
    title = ft.Container(
        padding=ft.Padding(18, 8, 18, 8),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.85, CARD),
        shadow=_SHADOW,
        content=ft.Column(
            tight=True,
            spacing=0,
            controls=[
                ft.Text(zone.name, size=18, weight=ft.FontWeight.BOLD, color=TEXT),
                ft.Text(f"{ZONE_LABELS[zone.kind]} · {zone.territory}", size=12, color=ft.Colors.with_opacity(0.75, TEXT)),
            ],
        ),
    )
    top_bar = ft.SafeArea(
        content=ft.Container(padding=16, content=ft.Row(spacing=10, controls=[back, title])),
    )

    return ft.Stack(
        expand=True,
        controls=[
            fill(ft.Container(content=canvas.control())),
            ft.Container(left=0, top=0, right=0, content=top_bar),
            overlay,
        ],
    )
