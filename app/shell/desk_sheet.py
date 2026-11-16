"""Вибір горщиків, які потрапляють на робочий стіл iPhone."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.contracts.labels import STAGE_LABELS
from app.contracts.models import PotCard
from app.contracts.pictures import pot_picture
from app.desk_widgets import load_pins, publish_pots, save_pins
from app.shell.theme import CARD, GREEN, TEXT

HINT = (
    "На iPhone затисни робочий стіл, натисни «+» і знайди HappyGarden. "
    "«Горщик» — одна рослина, яку обираєш. «Полиця» — усі позначені тут. "
    "Якщо нічого не позначено, полиця показує всі горщики."
)


def desk_sheet(cards: tuple[PotCard, ...] | list[PotCard], on_close: Callable[[], None]) -> ft.Control:
    pins = load_pins()
    rows: list[ft.Control] = []

    def toggle(pot_id: str, event: ft.ControlEvent) -> None:
        if event.control.value:
            pins.add(pot_id)
        else:
            pins.discard(pot_id)
        save_pins(pins)
        publish_pots(cards, pins)

    for card in cards:
        picture = pot_picture(card.pot.profile.species_id, card.pot.stage)
        face: ft.Control
        if picture:
            face = ft.Image(src=picture, width=44, height=68, fit=ft.BoxFit.CONTAIN)
        else:
            face = ft.Text(card.species.glyph or "🌱", size=28)
        rows.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    face,
                    ft.Column(
                        expand=True,
                        spacing=0,
                        controls=[
                            ft.Text(card.species.name, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Text(STAGE_LABELS[card.pot.stage], size=12, color=ft.Colors.with_opacity(0.7, TEXT)),
                        ],
                    ),
                    ft.Switch(
                        value=card.pot.id in pins,
                        active_color=GREEN,
                        on_change=lambda event, pot_id=card.pot.id: toggle(pot_id, event),
                    ),
                ],
            )
        )

    if not rows:
        rows.append(ft.Text("Спочатку посади рослину на стіл.", color=TEXT))

    body = ft.Column(
        tight=True,
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("На робочий стіл", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=GREEN, on_click=lambda _: on_close()),
                ],
            ),
            ft.Text(HINT, size=13, color=ft.Colors.with_opacity(0.75, TEXT)),
            *rows,
        ],
    )
    return ft.Container(
        left=16,
        right=16,
        bottom=24,
        padding=16,
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.96, CARD),
        shadow=ft.BoxShadow(blur_radius=18, color=ft.Colors.with_opacity(0.2, TEXT), offset=ft.Offset(0, 6)),
        content=body,
    )
