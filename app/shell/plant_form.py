"""Форма посадки. Культури бере з actions.search_species, садить через actions.plant."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.contracts.errors import SpeciesNotFound, ZoneNotFound
from app.contracts.labels import (
    BTN_BACK,
    BTN_PLANT,
    LBL_SOIL,
    LBL_SPECIES,
    LBL_VARIETY,
    SOIL_LABELS,
    UNVERIFIED_NOTE,
)
from app.contracts.models import SoilType, SpeciesProfile, ZoneView
from app.contracts.ports import Actions
from app.shell.theme import CARD, DANGER, GREEN, MIN_TAP, TEXT, WARNING

FORM_WIDTH = 420


def plant_form(
    actions: Actions,
    zone_id: str,
    x: float,
    y: float,
    on_done: Callable[[ZoneView], None],
    on_cancel: Callable[[], None],
) -> ft.Control:
    """Картка поверх сцени: культура, сорт, ґрунт, коротка довідка і «Посадити»."""
    catalog: list[SpeciesProfile] = actions.search_species("")
    chosen = {"species": catalog[0] if catalog else None}

    variety = ft.TextField(label=LBL_VARIETY, max_length=40, border_radius=12)
    soil = ft.Dropdown(
        label=LBL_SOIL,
        options=[ft.DropdownOption(key=item.value, text=SOIL_LABELS[item]) for item in SoilType],
        border_radius=12,
        expand=True,
    )
    summary = ft.Text("", size=13, color=ft.Colors.with_opacity(0.75, TEXT))
    unverified = ft.Text(UNVERIFIED_NOTE, size=12, color=WARNING, visible=False)
    error = ft.Text("", color=DANGER, visible=False)
    chips = ft.Row(wrap=True, spacing=8, run_spacing=8)

    def render_chips() -> None:
        current = chosen["species"]
        chips.controls = [
            ft.Container(
                height=MIN_TAP,
                padding=ft.Padding(14, 0, 16, 0),
                border_radius=MIN_TAP,
                bgcolor=GREEN if current and item.species_id == current.species_id else ft.Colors.with_opacity(0.08, GREEN),
                ink=True,
                on_click=lambda _, s=item: pick(s),
                content=ft.Row(
                    tight=True,
                    spacing=6,
                    controls=[
                        ft.Text(item.glyph, size=18),
                        ft.Text(
                            item.name,
                            color=CARD if current and item.species_id == current.species_id else TEXT,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                ),
            )
            for item in catalog
        ]
        if current:
            soil.value = current.ideal_soil.value
            summary.value = current.summary
            unverified.visible = not current.verified

    def pick(species: SpeciesProfile) -> None:
        chosen["species"] = species
        render_chips()
        for control in (chips, soil, summary, unverified):
            control.update()

    def submit(_: ft.Event | None = None) -> None:
        species = chosen["species"]
        if species is None:
            return
        try:
            view = actions.plant(zone_id, species.name, variety.value or "", SoilType(soil.value), x, y)
        except (ValueError, SpeciesNotFound, ZoneNotFound) as exc:
            error.value = str(exc)
            error.visible = True
            error.update()
            return
        on_done(view)

    render_chips()

    card = ft.Container(
        width=FORM_WIDTH,
        padding=24,
        border_radius=24,
        bgcolor=ft.Colors.with_opacity(0.96, CARD),
        shadow=ft.BoxShadow(blur_radius=40, color=ft.Colors.with_opacity(0.25, TEXT), offset=ft.Offset(0, 12)),
        content=ft.Column(
            tight=True,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    controls=[
                        ft.TextButton(BTN_BACK, icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda _: on_cancel()),
                    ]
                ),
                ft.Text(LBL_SPECIES, size=14, weight=ft.FontWeight.W_600, color=TEXT),
                chips,
                summary,
                unverified,
                variety,
                ft.Row([soil]),
                error,
                ft.FilledButton(
                    content=ft.Text(BTN_PLANT, size=16, weight=ft.FontWeight.W_600),
                    icon=ft.Icons.ADD_ROUNDED,
                    bgcolor=GREEN,
                    color=CARD,
                    height=MIN_TAP + 8,
                    on_click=submit,
                ),
            ],
        ),
    )

    # Затемнення під карткою; натискання повз картку закриває форму.
    return ft.Container(
        left=0,
        top=0,
        right=0,
        bottom=0,
        bgcolor=ft.Colors.with_opacity(0.35, TEXT),
        on_click=lambda _: on_cancel(),
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[ft.Container(padding=16, content=ft.GestureDetector(on_tap=lambda _: None, content=card))],
        ),
    )
