"""Смуга на головній і вибір того, що показує віджет на екрані телефону."""

from __future__ import annotations

import flet as ft

from app.contracts.clock import sim_now
from app.contracts.labels import NO_DATA
from app.contracts.models import ZoneView
from app.contracts.ports import Actions
from app.shell.phone_board import push_board
from app.shell.theme import CARD, GREEN, MIN_TAP, TEXT, WARNING
from app.shell.widget_facts import CATALOG, ORDER, Fact, build_facts, phone_line
from app.shell.widget_prefs import load_ids, save_ids

CHIP_H = 76
CHOOSE_W = 72

_ICONS: dict[str, ft.IconData] = {
    "next_water": ft.Icons.WATER_DROP_ROUNDED,
    "next_feed": ft.Icons.SPA_ROUNDED,
    "grow_left": ft.Icons.ECO_ROUNDED,
    "next_stage": ft.Icons.TIMELINE_ROUNDED,
    "thirsty": ft.Icons.WATER_DROP_ROUNDED,
    "ripe": ft.Icons.EMOJI_NATURE_ROUNDED,
    "health": ft.Icons.FAVORITE_ROUNDED,
}

_TONE = {"warn": WARNING, "good": GREEN, "plain": TEXT}


class HomeWidgets:
    """Вибір живе в Documents/HappyGarden/home_widgets.json."""

    def __init__(self, actions: Actions, width: float) -> None:
        self.actions = actions
        self.ids = load_ids()
        self.view: ZoneView | None = None
        self.failed = False
        self.open = False
        self.row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8, height=CHIP_H)
        self.sheet = ft.Stack(visible=False)
        self.control = ft.Container(width=width, content=self.row)
        self._paint()

    def show(self, view: ZoneView | None, *, failed: bool = False) -> None:
        self.view = view
        self.failed = failed
        self._paint()

    def update(self) -> None:
        self.row.update()

    def _paint(self) -> None:
        facts = self._facts() if self.ids else []
        if not facts:
            self.row.controls = [_choose_chip(self._open_sheet, wide=True)]
            push_board(["Обери віджети в HappyGarden"])
            return
        chips: list[ft.Control] = [_choose_chip(self._open_sheet)]
        chips.extend(_chip(fact) for fact in facts)
        self.row.controls = chips
        push_board([phone_line(fact) for fact in facts])

    def _facts(self) -> list[Fact]:
        if self.failed:
            return [
                Fact(widget_id, CATALOG[widget_id][0], NO_DATA, NO_DATA, "plain")
                for widget_id in self.ids
            ]
        cards = () if self.view is None else self.view.cards
        now = sim_now(self.actions.get_settings())
        return build_facts(cards, now, self.ids)

    def _toggle(self, widget_id: str, on: bool) -> None:
        picked = set(self.ids)
        if on:
            picked.add(widget_id)
        else:
            picked.discard(widget_id)
        self.ids = tuple(item for item in ORDER if item in picked)
        try:
            save_ids(self.ids)
        except OSError:
            pass
        self._paint()
        self.row.update()

    def _open_sheet(self, _e: ft.Event | None = None) -> None:
        self.open = True
        self.sheet.controls = [_picker(self._close_sheet, self._options())]
        self.sheet.visible = True
        self.sheet.update()

    def _close_sheet(self, _e: ft.Event | None = None) -> None:
        self.open = False
        self.sheet.visible = False
        self.sheet.controls = []
        self.sheet.update()

    def _options(self) -> list[ft.Control]:
        rows: list[ft.Control] = []
        for widget_id in ORDER:
            title, hint = CATALOG[widget_id]
            rows.append(
                ft.Container(
                    height=MIN_TAP + 12,
                    alignment=ft.Alignment.CENTER_LEFT,
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(_ICONS[widget_id], color=GREEN, size=22),
                            ft.Column(
                                expand=True,
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=TEXT),
                                    ft.Text(hint, size=12, color=ft.Colors.with_opacity(0.65, TEXT)),
                                ],
                            ),
                            ft.Switch(
                                value=widget_id in self.ids,
                                active_color=GREEN,
                                on_change=lambda e, wid=widget_id: self._toggle(wid, bool(e.control.value)),
                            ),
                        ],
                    ),
                )
            )
        return rows


def _choose_chip(on_click, wide: bool = False) -> ft.Control:
    return ft.Container(
        width=220 if wide else CHOOSE_W,
        height=CHIP_H,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.9, CARD),
        ink=True,
        on_click=on_click,
        tooltip="Обрати віджети",
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            tight=True,
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.TUNE_ROUNDED, color=GREEN, size=22),
                ft.Text("Обрати", size=11, weight=ft.FontWeight.W_600, color=TEXT),
            ],
        ),
    )


def _chip(fact: Fact) -> ft.Control:
    color = _TONE.get(fact.tone, TEXT)
    return ft.Container(
        width=188,
        height=CHIP_H,
        padding=ft.Padding(10, 8, 10, 8),
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.9, CARD),
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(_ICONS[fact.widget_id], size=16, color=color),
                        ft.Text(
                            fact.value,
                            expand=True,
                            size=13,
                            weight=ft.FontWeight.W_700,
                            color=color,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
                ft.Text(
                    fact.caption,
                    size=11,
                    color=ft.Colors.with_opacity(0.75, TEXT),
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    )


def _picker(on_close, options: list[ft.Control]) -> ft.Control:
    card = ft.Container(
        width=420,
        padding=16,
        border_radius=24,
        bgcolor=CARD,
        on_click=lambda _e: None,
        content=ft.Column(
            tight=True,
            spacing=10,
            controls=[
                ft.Text("Віджет на екрані", size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                ft.Text(
                    "Обери, що писати на віджеті телефону. Наприклад: «До поливки 1 година».",
                    size=13,
                    color=ft.Colors.with_opacity(0.7, TEXT),
                ),
                ft.Column(spacing=0, height=360, scroll=ft.ScrollMode.AUTO, controls=options),
                ft.Container(
                    height=MIN_TAP,
                    border_radius=14,
                    bgcolor=GREEN,
                    ink=True,
                    on_click=on_close,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("Готово", color=CARD, size=16, weight=ft.FontWeight.W_600),
                ),
            ],
        ),
    )
    return ft.Container(
        bgcolor=ft.Colors.with_opacity(0.35, TEXT),
        on_click=on_close,
        alignment=ft.Alignment.BOTTOM_CENTER,
        padding=16,
        content=card,
    )
