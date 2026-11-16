"""Збирає екрани. Карту отримує ззовні і не імпортує app.garden."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.contracts.errors import ZoneNotFound
from app.contracts.labels import APP_NAME, BTN_BACK, EMPTY_POTS, ZONE_LABELS
from app.contracts.models import Zone
from app.contracts.ports import Actions, MakeCanvas
from app.shell.home import home_view
from app.shell.onboarding import onboarding_view
from app.shell.theme import BG, CARD, GREEN, TEXT


def _pick_zone(actions: Actions) -> Zone | None:
    """Зона одна — вона. Кілька — last_zone_id, інакше перша. Список зон додасть людина 2."""
    zones = actions.list_zones()
    if not zones:
        return None
    last = actions.get_settings().last_zone_id
    return next((zone for zone in zones if zone.id == last), zones[0])


def _zone_stub(zone: Zone, pots: int, on_back: Callable[[], None]) -> ft.Control:
    """Тимчасовий екран зони, поки zone_page.py і карта не готові."""
    return ft.SafeArea(
        expand=True,
        content=ft.Container(
            padding=16,
            content=ft.Column(
                controls=[
                    ft.TextButton(BTN_BACK, icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda _: on_back()),
                    ft.Text(zone.name, size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                    ft.Text(f"{ZONE_LABELS[zone.kind]} · {zone.territory}", color=TEXT),
                    ft.Text(EMPTY_POTS if pots == 0 else f"🌱 × {pots}", color=GREEN, size=16),
                ],
            ),
        ),
    )


def mount(page: ft.Page, actions: Actions, make_canvas: MakeCanvas) -> None:
    del make_canvas  # Карту підключить zone_page.py.
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=GREEN)
    page.bgcolor = BG
    page.padding = 0
    page.spacing = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    def show(control: ft.Control) -> None:
        page.controls.clear()
        page.add(control)

    def not_ready() -> None:
        """Друзі й налаштування поки лише кнопки."""

    def go_home() -> None:
        show(
            home_view(
                actions,
                on_open_zone=open_zone,
                on_friends=not_ready,
                on_settings=not_ready,
                on_new_zone=go_new_zone,
            )
        )

    def go_onboarding() -> None:
        show(onboarding_view(actions, on_done=go_home))

    def go_new_zone() -> None:
        show(onboarding_view(actions, on_done=go_home, ask_nickname=False, on_cancel=go_home))

    def open_zone() -> None:
        zone = _pick_zone(actions)
        if zone is None:
            go_onboarding()
            return
        try:
            view = actions.open_zone(zone.id)
        except ZoneNotFound:
            go_home()
            return
        show(ft.Container(expand=True, bgcolor=CARD, content=_zone_stub(view.zone, len(view.cards), go_home)))

    if actions.list_zones():
        go_home()
    else:
        go_onboarding()
