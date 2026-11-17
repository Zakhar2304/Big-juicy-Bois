"""Друзі: таблиця очок і профіль.

Очки рахує actions.leaderboard. Свій профіль показує горщики зони (ростуть / зібрані).
У друга в контракті лише нік і очки — грядку тут не вигадуємо.
"""

from __future__ import annotations

from datetime import datetime

import flet as ft

from app.contracts.checks import clean_friend
from app.contracts.clock import sim_now
from app.contracts.errors import PotNotFound, SpeciesNotFound, ZoneNotFound
from app.contracts.labels import (
    BTN_ADD_FRIEND,
    BTN_BACK,
    BTN_FRIENDS,
    EMPTY_POTS,
    EMPTY_ZONES,
    LBL_FRIEND,
    LBL_HEALTH,
    LBL_POINTS,
    MOOD_LABELS,
    NO_DATA,
    SOIL_LABELS,
    STAGE_LABELS,
    ZONE_LABELS,
    as_percent,
)
from app.contracts.models import FarmScore, GrowthStage, LeaderboardRow, Mood, PotCard, ZoneKind
from app.contracts.pictures import PICTURE_RATIO, pot_picture
from app.contracts.ports import Actions
from app.shell.dates import day_month, relative
from app.shell.perf import pot_image
from app.shell.theme import (
    CARD,
    DANGER,
    GREEN,
    INFO,
    MIN_TAP,
    TEXT,
    WARNING,
    center_sheet,
    fill,
    greenhouse_backdrop,
    mounted,
)

_ERRORS = (SpeciesNotFound, ZoneNotFound, PotNotFound, ValueError)
_MUTED = ft.Colors.with_opacity(0.62, TEXT)
_SHADOW = ft.BoxShadow(blur_radius=18, color=ft.Colors.with_opacity(0.1, TEXT), offset=ft.Offset(0, 6))
_TINTS = (INFO, WARNING, "#6D4C41", "#00897B", "#5E35B1")
_MEDAL = {1: "#F9A825", 2: "#78909C", 3: "#B87333"}
_ZONE_ICONS = {
    ZoneKind.GREENHOUSE: ft.Icons.ECO_ROUNDED,
    ZoneKind.GARDEN: ft.Icons.AGRICULTURE_ROUNDED,
    ZoneKind.FARM: ft.Icons.HOUSE_ROUNDED,
}
_MOOD_COLORS = {
    Mood.HAPPY: GREEN,
    Mood.OK: INFO,
    Mood.THIRSTY: WARNING,
    Mood.SAD: DANGER,
}


def _ordinal(n: int) -> str:
    if n % 100 in (11, 12, 13):
        return f"{n}-те"
    last = n % 10
    if last == 1:
        return f"{n}-ше"
    if last == 2:
        return f"{n}-ге"
    if last == 3:
        return f"{n}-тє"
    return f"{n}-те"


def _friends_count(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        word = "друг"
    elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        word = "друга"
    else:
        word = "друзів"
    return f"{n} {word}"


def _screen(body: ft.Column) -> ft.Control:
    return ft.Stack(
        expand=True,
        controls=[
            *greenhouse_backdrop(blur=16, clear_center=False, veil=0.32),
            fill(ft.SafeArea(expand=True, content=center_sheet(body))),
        ],
    )


def _card(*controls: ft.Control, padding: int = 16) -> ft.Control:
    return ft.Container(
        padding=padding,
        border_radius=22,
        bgcolor=ft.Colors.with_opacity(0.94, CARD),
        shadow=_SHADOW,
        content=ft.Column(
            spacing=10,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=list(controls),
        ),
    )


def _tap(control: ft.Control, handler) -> ft.Control:
    return ft.GestureDetector(mouse_cursor=ft.MouseCursor.CLICK, on_tap=handler, content=control)


def _avatar(name: str, you: bool, size: float = 44) -> ft.Control:
    letter = (name[:1] or "?").upper()
    color = GREEN if you else _TINTS[sum(ord(ch) for ch in name) % len(_TINTS)]
    return ft.Container(
        width=size,
        height=size,
        border_radius=size / 2,
        bgcolor=color,
        alignment=ft.Alignment.CENTER,
        content=ft.Text(letter, color=CARD, size=size * 0.4, weight=ft.FontWeight.BOLD),
    )


def _chip(text: str, color: str, *, fill: bool) -> ft.Control:
    return ft.Container(
        padding=ft.Padding(8, 3, 8, 3),
        border_radius=10,
        bgcolor=color if fill else ft.Colors.with_opacity(0.12, color),
        content=ft.Text(text, size=11, color=CARD if fill else color, weight=ft.FontWeight.W_600),
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
                ft.Text(label, size=11, color=TEXT),
            ],
        ),
    )


def _tiles(pairs: list[tuple[str, str]]) -> ft.Control:
    return ft.Row(spacing=8, controls=[_tile(label, value) for label, value in pairs])


def _field(label: str, **kwargs: object) -> ft.TextField:
    return ft.TextField(
        label=label,
        border=ft.OutlineInputBorder(border_radius=12),
        text_size=16,
        **kwargs,  # type: ignore[arg-type]
    )


def _plant_tile(card: PotCard, now: datetime) -> ft.Control:
    pot, species = card.pot, card.species
    picture = pot_picture(pot.profile.species_id, pot.stage)
    thumb: ft.Control = (
        pot_image(picture, 46, 46 / PICTURE_RATIO)
        if picture
        else ft.Container(width=46, alignment=ft.Alignment.CENTER, content=ft.Text(species.glyph, size=28))
    )
    mood = pot.mood
    mood_color = _MOOD_COLORS.get(mood, INFO)
    lines: list[ft.Control] = [
        ft.Text(species.name, size=15, weight=ft.FontWeight.W_600, color=TEXT),
        ft.Text(
            f"{pot.profile.variety} · {SOIL_LABELS[pot.profile.soil_type]} · {day_month(pot.profile.planted_at)}",
            size=12,
            color=_MUTED,
        ),
        ft.Row(
            spacing=6,
            controls=[
                _chip(STAGE_LABELS[pot.stage], GREEN, fill=True),
                _chip(MOOD_LABELS[mood], mood_color, fill=False),
            ],
        ),
    ]
    forecast = card.forecast
    if forecast is not None and forecast.next_stage is not None and forecast.next_stage_at is not None:
        lines.append(
            ft.Text(
                f"{STAGE_LABELS[forecast.next_stage]} · {relative(forecast.next_stage_at, now)}",
                size=12,
                color=INFO,
            )
        )
    elif forecast is not None and forecast.ripe_at is not None and pot.stage != GrowthStage.RIPE:
        lines.append(
            ft.Text(
                f"{STAGE_LABELS[GrowthStage.RIPE]} · {relative(forecast.ripe_at, now)}",
                size=12,
                color=INFO,
            )
        )
    return ft.Container(
        padding=10,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.05, TEXT),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                thumb,
                ft.Column(expand=True, spacing=2, controls=lines),
                ft.Column(
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Text(f"{as_percent(pot.health)}%", size=16, weight=ft.FontWeight.BOLD, color=mood_color),
                        ft.Text(LBL_HEALTH, size=10, color=_MUTED),
                    ],
                ),
            ],
        ),
    )


def _section(title: str, cards: list[PotCard], empty: str, now: datetime) -> ft.Control:
    body: list[ft.Control] = [_plant_tile(card, now) for card in cards] or [
        ft.Text(empty, size=13, color=_MUTED)
    ]
    return ft.Column(
        spacing=8,
        controls=[ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=TEXT), *body],
    )


def _podium_card(row: LeaderboardRow, place: int, height: float) -> ft.Control:
    medal = _MEDAL.get(place, GREEN)
    bg = ft.Colors.with_opacity(0.16, GREEN) if row.is_you else ft.Colors.with_opacity(0.94, CARD)
    border = GREEN if row.is_you else ft.Colors.with_opacity(0.14, medal)
    return ft.Container(
        height=height,
        border_radius=20,
        bgcolor=bg,
        border=ft.Border.all(2 if row.is_you else 1, border),
        shadow=_SHADOW,
        alignment=ft.Alignment.BOTTOM_CENTER,
        padding=ft.Padding(8, 10, 8, 12),
        content=ft.Column(
            tight=True,
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=28,
                            height=28,
                            border_radius=14,
                            bgcolor=medal,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(str(place), color=CARD, weight=ft.FontWeight.BOLD, size=13),
                        )
                    ],
                ),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[_avatar(row.nickname, row.is_you, 40)]),
                ft.Text(
                    row.nickname,
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=TEXT,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(str(row.points), size=16, weight=ft.FontWeight.BOLD, color=GREEN, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )


def _list_row(row: LeaderboardRow, place: int) -> ft.Control:
    bg = ft.Colors.with_opacity(0.18, GREEN) if row.is_you else ft.Colors.with_opacity(0.94, CARD)
    return ft.Container(
        height=72,
        border_radius=18,
        bgcolor=bg,
        border=ft.Border.all(2, GREEN) if row.is_you else None,
        padding=ft.Padding(12, 8, 8, 8),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=36,
                    height=36,
                    border_radius=18,
                    bgcolor=GREEN if row.is_you else ft.Colors.with_opacity(0.08, TEXT),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(str(place), color=CARD if row.is_you else TEXT, weight=ft.FontWeight.BOLD),
                ),
                _avatar(row.nickname, row.is_you, 40),
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        ft.Text(row.nickname, size=16, weight=ft.FontWeight.W_600, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{LBL_POINTS}: {row.points}", size=12, color=_MUTED),
                    ],
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=_MUTED, size=22),
            ],
        ),
    )


def _board(rows: list[LeaderboardRow], on_pick) -> list[ft.Control]:
    if not rows:
        return [ft.Text(NO_DATA, color=_MUTED)]
    blocks: list[ft.Control] = []
    if len(rows) == 1:
        blocks.append(_tap(_list_row(rows[0], 1), lambda _: on_pick(0)))
        return blocks
    order = [0, 1] if len(rows) == 2 else [1, 0, 2]
    heights = {0: 176, 1: 140, 2: 128} if len(rows) > 2 else {0: 176, 1: 140}
    cells: list[ft.Control] = []
    for index in order:
        if index >= len(rows):
            continue
        card = _podium_card(rows[index], index + 1, heights[index])
        cells.append(ft.Container(expand=True, content=_tap(card, lambda _, i=index: on_pick(i))))
    blocks.append(ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.END, controls=cells))
    start = 3 if len(rows) > 2 else 2
    for index in range(start, len(rows)):
        blocks.append(_tap(_list_row(rows[index], index + 1), lambda _, i=index: on_pick(i)))
    return blocks


def _gap(row: LeaderboardRow, rows: list[LeaderboardRow]) -> str | None:
    you = next((item for item in rows if item.is_you), None)
    if you is None or row.is_you:
        return None
    delta = row.points - you.points
    if delta > 0:
        return f"На {delta} попереду тебе"
    if delta < 0:
        return f"На {-delta} позаду тебе"
    return "Стільки ж очок, як у тебе"


def _meters(row: LeaderboardRow, rows: list[LeaderboardRow]) -> ft.Control | None:
    you = next((item for item in rows if item.is_you and item is not row), None)
    if you is None:
        return None
    scale = max(row.points, you.points, 1)
    return ft.Column(
        spacing=8,
        controls=[
            ft.Text(LBL_POINTS, size=13, weight=ft.FontWeight.W_600, color=_MUTED),
            _meter(row.nickname, row.points, scale, GREEN if not row.is_you else INFO),
            _meter(you.nickname, you.points, scale, GREEN),
        ],
    )


def _meter(label: str, points: int, scale: int, color: str) -> ft.Control:
    return ft.Column(
        spacing=2,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(label, size=12, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    ft.Text(str(points), size=12, weight=ft.FontWeight.W_600, color=TEXT),
                ],
            ),
            ft.ProgressBar(
                value=points / scale,
                color=color,
                bgcolor=ft.Colors.with_opacity(0.12, color),
                height=8,
                border_radius=8,
            ),
        ],
    )


def _unknown_garden() -> list[ft.Control]:
    return [
        ft.Text(
            "У таблиці зберігаються лише нік і очки. Грядки друга в цих даних немає.",
            size=13,
            color=_MUTED,
        ),
        _section("Зараз росте", [], NO_DATA, datetime.now()),
        _section("Вже зібрано", [], NO_DATA, datetime.now()),
    ]


def _your_gardens(actions: Actions, zone_id: str) -> list[ft.Control]:
    blocks: list[ft.Control] = []
    try:
        now = sim_now(actions.get_settings())
        zones = actions.list_zones()
    except _ERRORS as exc:
        return [ft.Text(str(exc), color=DANGER)]
    if not zones:
        return [ft.Text(EMPTY_ZONES, color=_MUTED)]
    for zone in zones:
        try:
            view = actions.open_zone(zone.id)
            score: FarmScore = actions.your_score(zone.id)
        except _ERRORS as exc:
            blocks.append(ft.Text(str(exc), color=DANGER))
            continue
        growing = [card for card in view.cards if card.pot.stage != GrowthStage.HARVESTED]
        done = [card for card in view.cards if card.pot.stage == GrowthStage.HARVESTED]
        plants: list[ft.Control]
        if not view.cards:
            plants = [ft.Text(EMPTY_POTS, size=13, color=_MUTED)]
        else:
            plants = [
                _section("Зараз росте", growing, "Зараз нічого не росте", now),
                _section("Вже зібрано", done, "Ще нічого не зібрано", now),
            ]
        note = "Очки в таблиці — з цієї зони" if zone.id == zone_id else ""
        blocks.append(
            _card(
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(_ZONE_ICONS[view.zone.kind], color=GREEN, size=22),
                        ft.Column(
                            expand=True,
                            spacing=0,
                            controls=[
                                ft.Text(view.zone.name, size=16, weight=ft.FontWeight.W_600, color=TEXT),
                                ft.Text(f"{ZONE_LABELS[view.zone.kind]} · {view.zone.territory}", size=12, color=_MUTED),
                            ],
                        ),
                    ],
                ),
                _tiles(
                    [
                        (LBL_POINTS, str(score.points)),
                        (LBL_HEALTH, f"{as_percent(score.health)}%"),
                        (STAGE_LABELS[GrowthStage.RIPE], str(score.ripe_count)),
                    ]
                ),
                *([ft.Text(note, size=12, color=INFO)] if note else []),
                *plants,
            )
        )
    return blocks


def _profile(actions: Actions, rows: list[LeaderboardRow], index: int, zone_id: str) -> list[ft.Control]:
    row = rows[index]
    place = index + 1
    gap = _gap(row, rows)
    meters = _meters(row, rows)
    hero = _card(
        ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _avatar(row.nickname, row.is_you, 72),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(row.nickname, size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text(f"{_ordinal(place)} місце · {row.points} {LBL_POINTS.lower()}", size=13, color=_MUTED),
                        *([_chip("Ти", GREEN, fill=True)] if row.is_you else []),
                    ],
                ),
            ],
        ),
        *([ft.Text(gap, size=14, weight=ft.FontWeight.W_600, color=GREEN)] if gap else []),
        *([meters] if meters is not None else []),
    )
    garden = _your_gardens(actions, zone_id) if row.is_you else [_card(*_unknown_garden())]
    return [hero, *garden]


def friends_view(actions: Actions, zone_id: str, on_back) -> ft.Control:
    rows: list[LeaderboardRow] = []
    picked: dict[str, int | None] = {"index": None}
    title = ft.Text(BTN_FRIENDS, size=26, weight=ft.FontWeight.BOLD, color=TEXT, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
    summary = ft.Text("", size=13, color=_MUTED)
    banner = ft.Text("", color=DANGER, visible=False, size=13)
    ranks = ft.Column(spacing=10)
    profile = ft.Column(spacing=12, visible=False)
    nick = _field(LBL_FRIEND, max_length=20, prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED)
    points = _field(LBL_POINTS, prefix_icon=ft.Icons.EMOJI_EVENTS_ROUNDED, keyboard_type=ft.KeyboardType.NUMBER)
    form_error = ft.Text("", color=DANGER, visible=False, size=13)

    def paint_summary() -> None:
        you = next((i for i, row in enumerate(rows) if row.is_you), None)
        others = len(rows) - (0 if you is None else 1)
        zone_name = ""
        try:
            for zone in actions.list_zones():
                if zone.id == zone_id:
                    zone_name = zone.name
                    break
        except _ERRORS:
            zone_name = ""
        bits: list[str] = []
        if zone_name:
            bits.append(zone_name)
        if you is not None:
            bits.append(f"ти на {_ordinal(you + 1)} місці")
        bits.append(_friends_count(others))
        summary.value = " · ".join(bits)

    def show_list() -> None:
        picked["index"] = None
        title.value = BTN_FRIENDS
        summary.visible = True
        paint_summary()
        profile.visible = False
        profile.controls = []
        ranks.visible = True
        form.visible = available["ok"]
        ranks.controls = _board(rows, open_profile)
        _refresh(title, summary, ranks, profile, form)

    def open_profile(index: int) -> None:
        if index < 0 or index >= len(rows):
            return
        picked["index"] = index
        title.value = rows[index].nickname
        summary.visible = False
        ranks.visible = False
        form.visible = False
        profile.visible = True
        profile.controls = _profile(actions, rows, index, zone_id)
        _refresh(title, summary, ranks, profile, form)

    def go_back(_: ft.Event | None = None) -> None:
        if picked["index"] is not None:
            show_list()
            return
        on_back()

    def add(_: ft.Event | None = None) -> None:
        raw = (points.value or "").strip()
        try:
            score = int(raw)
        except ValueError:
            score = -1
        try:
            if score < 0:
                raise ValueError("Очки — ціле число від 0 до 99999")
            clean_friend(nick.value or "", score)
            actions.add_friend(nick.value or "", score)
            rows[:] = list(actions.leaderboard(zone_id))
        except _ERRORS as exc:
            form_error.value = str(exc)
            form_error.visible = True
            if mounted(form_error):
                form_error.update()
            return
        nick.value = ""
        points.value = ""
        form_error.visible = False
        show_list()
        if mounted(nick):
            nick.update()
            points.update()

    async def focus_points(_: ft.Event) -> None:
        await points.focus()

    nick.on_submit = focus_points
    points.on_submit = add

    form = _card(
        ft.Text(BTN_ADD_FRIEND, size=16, weight=ft.FontWeight.W_600, color=TEXT),
        nick,
        points,
        form_error,
        ft.FilledButton(
            content=ft.Text(BTN_ADD_FRIEND, size=16, weight=ft.FontWeight.W_600),
            icon=ft.Icons.PERSON_ADD_ALT_1_ROUNDED,
            bgcolor=GREEN,
            color=CARD,
            height=MIN_TAP + 4,
            on_click=add,
        ),
    )

    available = {"ok": True}
    if not zone_id:
        available["ok"] = False
    else:
        try:
            rows.extend(actions.leaderboard(zone_id))
        except ZoneNotFound:
            available["ok"] = False
        except _ERRORS as exc:
            banner.value = str(exc)
            banner.visible = True

    if not available["ok"]:
        ranks.controls = [
            _card(
                ft.Icon(ft.Icons.YARD_OUTLINED, color=GREEN, size=36),
                ft.Text(EMPTY_ZONES, size=16, color=TEXT),
            )
        ]
        form.visible = False
    else:
        paint_summary()
        ranks.controls = _board(rows, open_profile)

    header = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.TextButton(
                BTN_BACK,
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                height=MIN_TAP,
                style=ft.ButtonStyle(color=TEXT, bgcolor=ft.Colors.with_opacity(0.92, CARD)),
                on_click=go_back,
            ),
            title,
        ],
    )
    body = ft.Column(spacing=14, controls=[header, summary, banner, ranks, form, profile])
    return _screen(body)


def _refresh(*controls: ft.Control) -> None:
    for control in controls:
        if mounted(control):
            control.update()
