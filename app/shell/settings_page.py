"""Нік, місцевість, нагадування, зсув днів і статистика профілю.

Мову не перемикаємо: у налаштуваннях її немає на екрані, збережене значення лишається.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import flet as ft

from app.contracts.errors import PotNotFound, SpeciesNotFound, ZoneNotFound
from app.auth.config import legal_url
from app.contracts.labels import (
    BTN_BACK,
    BTN_CANCEL,
    BTN_CONFIRM_DELETE_ACCOUNT,
    BTN_DAY_MINUS,
    BTN_DAY_PLUS,
    BTN_DELETE_ACCOUNT,
    BTN_LOGOUT,
    BTN_SETTINGS,
    BTN_STATUS,
    DELETE_ACCOUNT_HINT,
    EMPTY_ZONES,
    LBL_ALERTS,
    LBL_DAY,
    LBL_HEALTH,
    LBL_LEGAL,
    LBL_NICKNAME,
    LBL_POINTS,
    LBL_PRIVACY,
    LBL_REMINDERS,
    LBL_TERMS,
    LBL_TERRITORY,
    STAGE_LABELS,
    ZONE_LABELS,
    as_percent,
)
from app.contracts.models import GrowthStage
from app.contracts.ports import Actions
from app.shell.theme import CARD, DANGER, GREEN, INFO, MIN_TAP, TEXT, center_sheet, fill, greenhouse_backdrop, mounted

_ERRORS = (SpeciesNotFound, ZoneNotFound, PotNotFound, ValueError)
_MUTED = ft.Colors.with_opacity(0.62, TEXT)
_SHADOW = ft.BoxShadow(blur_radius=18, color=ft.Colors.with_opacity(0.1, TEXT), offset=ft.Offset(0, 6))


def _screen(body: ft.Column) -> ft.Control:
    return ft.Stack(
        expand=True,
        controls=[
            *greenhouse_backdrop(blur=16, clear_center=False, veil=0.32),
            fill(ft.SafeArea(expand=True, content=center_sheet(body))),
        ],
    )


def _card(*controls: ft.Control) -> ft.Control:
    return ft.Container(
        padding=16,
        border_radius=22,
        bgcolor=ft.Colors.with_opacity(0.94, CARD),
        shadow=_SHADOW,
        content=ft.Column(
            spacing=12,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=list(controls),
        ),
    )


def _tile(label: str, value: str) -> ft.Control:
    return ft.Container(
        expand=True,
        padding=ft.Padding(10, 10, 10, 10),
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.08, GREEN),
        content=ft.Column(
            tight=True,
            spacing=0,
            controls=[
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=GREEN),
                ft.Text(label, size=11, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            ],
        ),
    )


def _tiles(pairs: list[tuple[str, str]]) -> ft.Control:
    return ft.Row(spacing=8, controls=[_tile(label, value) for label, value in pairs])


def _field(label: str, value: str, icon: ft.IconData, max_length: int) -> ft.TextField:
    return ft.TextField(
        label=label,
        value=value,
        max_length=max_length,
        prefix_icon=icon,
        border=ft.OutlineInputBorder(border_radius=12),
        text_size=16,
    )


def _toggle(icon: ft.IconData, title: str, hint: str, switch: ft.Switch) -> ft.Control:
    return ft.Container(
        height=MIN_TAP + 16,
        alignment=ft.Alignment.CENTER_LEFT,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon, color=GREEN, size=22),
                ft.Column(
                    expand=True,
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=TEXT),
                        ft.Text(hint, size=12, color=_MUTED),
                    ],
                ),
                switch,
            ],
        ),
    )


def _profile(actions: Actions) -> list[ft.Control]:
    """Числа з your_score і widgets. Кількість «росте / зібрано» — це перелік уже порахованих горщиків."""
    blocks: list[ft.Control] = []
    try:
        settings = actions.get_settings()
        zones = actions.list_zones()
    except _ERRORS as exc:
        return [ft.Text(str(exc), color=DANGER)]

    blocks.append(ft.Text(settings.nickname, size=22, weight=ft.FontWeight.BOLD, color=TEXT))
    blocks.append(
        ft.Row(
            spacing=6,
            controls=[
                ft.Icon(ft.Icons.PLACE_OUTLINED, size=16, color=GREEN),
                ft.Text(settings.territory, size=13, color=_MUTED),
            ],
        )
    )
    if not zones:
        blocks.append(ft.Text(EMPTY_ZONES, size=14, color=_MUTED))
    else:
        for zone in zones:
            try:
                score = actions.your_score(zone.id)
                view = actions.open_zone(zone.id)
            except _ERRORS as exc:
                blocks.append(ft.Text(f"{zone.name}: {exc}", color=DANGER, size=13))
                continue
            growing = sum(1 for card in view.cards if card.pot.stage != GrowthStage.HARVESTED)
            harvested = sum(1 for card in view.cards if card.pot.stage == GrowthStage.HARVESTED)
            blocks.append(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            f"{zone.name} · {ZONE_LABELS[zone.kind]}",
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=TEXT,
                        ),
                        _tiles(
                            [
                                (LBL_POINTS, str(score.points)),
                                (LBL_HEALTH, f"{as_percent(score.health)}%"),
                                (STAGE_LABELS[GrowthStage.RIPE], str(score.ripe_count)),
                            ]
                        ),
                        _tiles(
                            [
                                ("Росте", str(growing)),
                                ("Зібрано", str(harvested)),
                                ("Горщиків", str(len(view.cards))),
                            ]
                        ),
                    ],
                )
            )

    try:
        snaps = actions.widgets()
    except _ERRORS as exc:
        blocks.append(ft.Text(str(exc), color=DANGER, size=13))
        snaps = []
    if snaps:
        lines: list[ft.Control] = [
            ft.Text(BTN_STATUS, size=13, weight=ft.FontWeight.W_600, color=_MUTED)
        ]
        for snap in snaps:
            lines.append(ft.Text(snap.title, size=14, weight=ft.FontWeight.W_600, color=TEXT))
            lines.extend(ft.Text(line, size=13, color=_MUTED) for line in snap.lines)
        blocks.append(ft.Column(spacing=2, controls=lines))
    return blocks


def settings_view(
    actions: Actions,
    on_back,
    page: ft.Page | None = None,
    on_logout: Callable[[], None] | None = None,
    on_delete_account: Callable[[], None] | None = None,
) -> ft.Control:
    try:
        current = actions.get_settings()
    except _ERRORS as exc:
        title = ft.Text(BTN_SETTINGS, size=26, weight=ft.FontWeight.BOLD, color=TEXT, expand=True)
        body = ft.Column(
            spacing=14,
            controls=[
                _back_row(title, on_back),
                ft.Text(str(exc), color=DANGER),
            ],
        )
        return _screen(body)

    nickname = _field(LBL_NICKNAME, current.nickname, ft.Icons.BADGE_OUTLINED, 20)
    territory = _field(LBL_TERRITORY, current.territory, ft.Icons.PLACE_OUTLINED, 60)
    water = ft.Switch(value=current.notify_water, active_color=GREEN)
    weather = ft.Switch(value=current.notify_weather, active_color=INFO)
    offset = ft.Text(str(current.debug_day_offset), size=28, weight=ft.FontWeight.BOLD, color=GREEN, text_align=ft.TextAlign.CENTER)
    error = ft.Text("", color=DANGER, visible=False, size=13)
    saved = ft.Text("", color=GREEN, visible=False, size=13, weight=ft.FontWeight.W_600)
    stats = ft.Column(spacing=10, controls=_profile(actions))

    def hide_note(_: ft.Event | None = None) -> None:
        if saved.visible or error.visible:
            saved.visible = False
            error.visible = False
            if mounted(saved):
                saved.update()
                error.update()

    def fail(message: str) -> None:
        error.value = message
        error.visible = True
        saved.visible = False
        if mounted(error):
            error.update()
            saved.update()

    def save(_: ft.Event | None = None) -> None:
        try:
            latest = actions.get_settings()
            stored = actions.save_settings(
                replace(
                    latest,
                    nickname=nickname.value or "",
                    territory=territory.value or "",
                    notify_water=bool(water.value),
                    notify_weather=bool(weather.value),
                )
            )
        except _ERRORS as exc:
            fail(str(exc))
            return
        nickname.value = stored.nickname
        territory.value = stored.territory
        water.value = stored.notify_water
        weather.value = stored.notify_weather
        error.visible = False
        saved.value = "Збережено"
        saved.visible = True
        stats.controls = _profile(actions)
        for control in (nickname, territory, water, weather, saved, error, stats):
            if mounted(control):
                control.update()

    def shift(delta: int) -> None:
        try:
            value = actions.shift_days(delta)
        except _ERRORS as exc:
            fail(str(exc))
            return
        offset.value = str(value)
        if mounted(offset):
            offset.update()

    nickname.on_change = hide_note
    territory.on_change = hide_note
    nickname.on_submit = save
    territory.on_submit = save

    title = ft.Text(BTN_SETTINGS, size=26, weight=ft.FontWeight.BOLD, color=TEXT, expand=True)

    async def open_legal(name: str) -> None:
        await ft.UrlLauncher().launch_url(legal_url(name))

    def legal_btn(label: str, name: str) -> ft.Control:
        return ft.TextButton(
            label,
            icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
            height=MIN_TAP,
            style=ft.ButtonStyle(color=TEXT),
            on_click=lambda _, page_name=name: page.run_task(open_legal, page_name) if page is not None else None,
        )

    account: list[ft.Control] = [
        _card(
            ft.Text(LBL_LEGAL, size=13, weight=ft.FontWeight.W_600, color=_MUTED),
            ft.Row(
                wrap=True,
                spacing=4,
                controls=[
                    legal_btn(LBL_PRIVACY, "privacy"),
                    legal_btn(LBL_TERMS, "terms"),
                ],
            ),
        )
    ]
    if on_logout is not None:
        account.append(
            ft.OutlinedButton(
                content=ft.Text(BTN_LOGOUT),
                icon=ft.Icons.LOGOUT_ROUNDED,
                height=MIN_TAP,
                style=ft.ButtonStyle(color=DANGER, side=ft.BorderSide(1, DANGER)),
                on_click=lambda _: on_logout(),
            )
        )
    if on_delete_account is not None and page is not None:
        def ask_delete(_: ft.Event | None = None) -> None:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(BTN_DELETE_ACCOUNT),
                content=ft.Text(DELETE_ACCOUNT_HINT),
                actions=[
                    ft.TextButton(BTN_CANCEL, on_click=lambda e: page.pop_dialog()),
                    ft.TextButton(
                        BTN_CONFIRM_DELETE_ACCOUNT,
                        style=ft.ButtonStyle(color=DANGER),
                        on_click=lambda e: (page.pop_dialog(), on_delete_account()),
                    ),
                ],
            )
            page.show_dialog(dialog)

        account.append(
            ft.TextButton(
                BTN_DELETE_ACCOUNT,
                icon=ft.Icons.DELETE_FOREVER_ROUNDED,
                height=MIN_TAP,
                style=ft.ButtonStyle(color=DANGER),
                on_click=ask_delete,
            )
        )

    body = ft.Column(
        spacing=14,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            _back_row(title, on_back),
            error,
            saved,
            _card(stats),
            _card(nickname, territory),
            _card(
                ft.Text(LBL_REMINDERS, size=13, weight=ft.FontWeight.W_600, color=_MUTED),
                _toggle(ft.Icons.WATER_DROP_ROUNDED, "Полив", "Сповіщати, коли пора полити", water),
                _toggle(ft.Icons.WB_CLOUDY_OUTLINED, LBL_ALERTS, "Сповіщати про попередження погоди", weather),
            ),
            _card(
                ft.Text(LBL_DAY, size=13, weight=ft.FontWeight.W_600, color=_MUTED),
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Text(BTN_DAY_MINUS),
                            height=MIN_TAP,
                            expand=True,
                            on_click=lambda _: shift(-1),
                        ),
                        ft.Container(width=72, alignment=ft.Alignment.CENTER, content=offset),
                        ft.OutlinedButton(
                            content=ft.Text(BTN_DAY_PLUS),
                            height=MIN_TAP,
                            expand=True,
                            on_click=lambda _: shift(1),
                        ),
                    ],
                ),
            ),
            ft.FilledButton(
                content=ft.Text("Зберегти", size=16, weight=ft.FontWeight.W_600),
                icon=ft.Icons.CHECK_ROUNDED,
                bgcolor=GREEN,
                color=CARD,
                height=MIN_TAP + 4,
                on_click=save,
            ),
            *account,
        ],
    )
    return _screen(body)


def _back_row(title: ft.Text, on_back) -> ft.Control:
    return ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.TextButton(
                BTN_BACK,
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                height=MIN_TAP,
                style=ft.ButtonStyle(color=TEXT, bgcolor=ft.Colors.with_opacity(0.92, CARD)),
                on_click=lambda _: on_back(),
            ),
            title,
        ],
    )
