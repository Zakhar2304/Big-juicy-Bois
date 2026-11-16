"""Нік, місцевість, перемикачі нагадувань, кнопки зсуву днів."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import flet as ft

from app.contracts.labels import (
    BTN_BACK,
    BTN_DAY_MINUS,
    BTN_DAY_PLUS,
    BTN_SETTINGS,
    BTN_WATER,
    LBL_ALERTS,
    LBL_DAY,
    LBL_NICKNAME,
    LBL_REMINDERS,
    LBL_TERRITORY,
)
from app.contracts.ports import Actions
from app.shell.theme import CARD, DANGER, GREEN, MIN_TAP, TEXT, fill, greenhouse_backdrop


def settings_view(actions: Actions, on_back: Callable[[], None]) -> ft.Control:
    settings = actions.get_settings()
    nickname = ft.TextField(label=LBL_NICKNAME, value=settings.nickname, max_length=20, border_radius=12)
    territory = ft.TextField(label=LBL_TERRITORY, value=settings.territory, max_length=60, border_radius=12)
    water = ft.Switch(
        label=f"{LBL_REMINDERS}: {BTN_WATER}",
        value=settings.notify_water,
        active_color=GREEN,
    )
    weather = ft.Switch(
        label=f"{LBL_REMINDERS}: {LBL_ALERTS}",
        value=settings.notify_weather,
        active_color=GREEN,
    )
    offset = ft.Text(f"{LBL_DAY}: {settings.debug_day_offset}", size=16, color=TEXT, weight=ft.FontWeight.W_600)
    error = ft.Text("", color=DANGER, visible=False)
    saved = ft.Text("Збережено на цьому пристрої", color=GREEN, visible=False)

    def show_error(message: str) -> None:
        error.value = message
        error.visible = True
        saved.visible = False
        error.update()
        saved.update()

    def apply(delta: int | None = None) -> None:
        try:
            current = actions.get_settings()
            actions.save_settings(
                replace(
                    current,
                    nickname=nickname.value or "",
                    territory=territory.value or "",
                    notify_water=bool(water.value),
                    notify_weather=bool(weather.value),
                )
            )
            if delta is not None:
                actions.shift_days(delta)
            offset.value = f"{LBL_DAY}: {actions.get_settings().debug_day_offset}"
            error.visible = False
            saved.visible = True
            offset.update()
            error.update()
            saved.update()
        except ValueError as exc:
            show_error(str(exc))

    form = ft.Container(
        width=420,
        padding=24,
        border_radius=24,
        bgcolor=ft.Colors.with_opacity(0.94, CARD),
        shadow=ft.BoxShadow(blur_radius=24, color=ft.Colors.with_opacity(0.16, TEXT), offset=ft.Offset(0, 8)),
        content=ft.Column(
            tight=True,
            spacing=14,
            controls=[
                ft.TextButton(BTN_BACK, icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda _: on_back()),
                ft.Text(BTN_SETTINGS, size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                nickname,
                territory,
                water,
                weather,
                offset,
                ft.Row(
                    controls=[
                        ft.OutlinedButton(BTN_DAY_MINUS, height=MIN_TAP, on_click=lambda _: apply(-1)),
                        ft.OutlinedButton(BTN_DAY_PLUS, height=MIN_TAP, on_click=lambda _: apply(1)),
                    ],
                ),
                error,
                saved,
                ft.FilledButton(
                    content=ft.Text("Зберегти", size=16, weight=ft.FontWeight.W_600),
                    icon=ft.Icons.SAVE_ROUNDED,
                    bgcolor=GREEN,
                    color=CARD,
                    height=MIN_TAP + 8,
                    on_click=lambda _: apply(),
                ),
            ],
        ),
    )
    return ft.Stack(
        expand=True,
        controls=[
            *greenhouse_backdrop(blur=24, clear_center=False, veil=0.2),
            fill(
                ft.SafeArea(
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[ft.Container(content=form, padding=16)],
                    )
                )
            ),
        ],
    )
