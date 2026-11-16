"""Таблиця очок. Рахує її actions.leaderboard, не цей файл."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.contracts.labels import BTN_ADD_FRIEND, BTN_BACK, BTN_FRIENDS, EMPTY_ZONES, LBL_FRIEND, LBL_POINTS
from app.contracts.models import LeaderboardRow
from app.contracts.ports import Actions
from app.shell.theme import CARD, DANGER, GREEN, MIN_TAP, TEXT, fill, greenhouse_backdrop


def friends_view(actions: Actions, zone_id: str, on_back: Callable[[], None]) -> ft.Control:
    rows = ft.Column(spacing=8, tight=True)
    nickname = ft.TextField(label=LBL_FRIEND, max_length=20, border_radius=12, expand=True)
    points = ft.TextField(
        label=LBL_POINTS,
        value="0",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=12,
        width=120,
    )
    error = ft.Text("", color=DANGER, visible=False)

    def paint(board: list[LeaderboardRow]) -> None:
        rows.controls = [_row(item) for item in board]
        if rows.page is not None:
            rows.update()

    def add(_: ft.Event | None = None) -> None:
        raw = (points.value or "").strip()
        try:
            score = int(raw)
        except ValueError:
            error.value = "Очки — ціле число від 0 до 99999"
            error.visible = True
            error.update()
            return
        try:
            board = actions.add_friend(nickname.value or "", score)
        except ValueError as exc:
            error.value = str(exc)
            error.visible = True
            error.update()
            return
        nickname.value = ""
        points.value = "0"
        error.visible = False
        nickname.update()
        points.update()
        error.update()
        paint(board)

    has_zone = bool(zone_id)
    if has_zone:
        try:
            paint(actions.leaderboard(zone_id))
        except Exception as exc:  # noqa: BLE001 — немає зони або дані зіпсовані
            rows.controls = [ft.Text(str(exc), color=DANGER)]

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
                ft.Text(BTN_FRIENDS, size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                ft.Text(EMPTY_ZONES, color=TEXT, visible=not has_zone),
                rows,
                ft.Row(
                    visible=has_zone,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[nickname, points],
                ),
                error,
                ft.FilledButton(
                    visible=has_zone,
                    content=ft.Text(BTN_ADD_FRIEND, size=16, weight=ft.FontWeight.W_600),
                    icon=ft.Icons.PERSON_ADD_ROUNDED,
                    bgcolor=GREEN,
                    color=CARD,
                    height=MIN_TAP + 8,
                    on_click=add,
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


def _row(item: LeaderboardRow) -> ft.Control:
    return ft.Container(
        height=MIN_TAP + 8,
        padding=ft.Padding(14, 0, 14, 0),
        border_radius=16,
        bgcolor=GREEN if item.is_you else ft.Colors.with_opacity(0.08, GREEN),
        alignment=ft.Alignment.CENTER_LEFT,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    item.nickname,
                    color=CARD if item.is_you else TEXT,
                    weight=ft.FontWeight.W_600,
                    size=16,
                ),
                ft.Text(
                    str(item.points),
                    color=CARD if item.is_you else GREEN,
                    weight=ft.FontWeight.BOLD,
                    size=16,
                ),
            ],
        ),
    )
