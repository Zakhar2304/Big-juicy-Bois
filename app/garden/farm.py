"""Сцена фазенди: фото теплиці зі столом, горщики стоять на стільниці.

Реалізує GardenCanvas (control, show, spawn_point) з тим самим конструктором, що GardenMap.
Додатково має `on_add`: якщо його задати, на вільному місці столу з'являється «+».
Стан рослин не рахує: етап і культуру бере з ZoneView.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import flet as ft

from app.contracts.checks import clamp_world
from app.contracts.constants import SPAWN_GAP, WORLD_SIZE
from app.contracts.labels import BTN_CHANGE_POT, BTN_DELETE_POT, BTN_PLANT, BTN_POT_INFO, STAGE_LABELS
from app.contracts.models import STAGE_ORDER, GrowthStage, PotCard, ZoneView
from app.contracts.pictures import PICTURE_FOOT, PICTURE_POT_SHARE, PICTURE_RATIO, pot_picture
from app.shell.perf import bg_image, pot_image

BACKGROUND = "backgrounds/farm.jpg"  # стиснута копія для телефону й вебу
BG_W, BG_H = 1600, 893

# Стільниця на фото, частки картинки.
TABLE_LEFT, TABLE_RIGHT = 0.08, 0.92
TABLE_FOOT_Y = 0.735  # де стоїть дно горщика

POT_W = 0.24  # ширина кадру горщика від висоти картинки (сам горщик — 0.62 кадру)
MIN_POT_W = 70
GAP = -0.12  # кадри трохи заходять один на один: по боках горщика в кадрі порожньо
PLUS = 64


class FarmBench:
    def __init__(
        self,
        on_select_pot: Callable[[str], None],
        on_move_pot: Callable[[str, float, float], None],
    ) -> None:
        self._on_select_pot = on_select_pot
        self._on_move_pot = on_move_pot  # стіл не перетягує горщики
        self.on_add: Callable[[], None] | None = None
        self.on_delete: Callable[[str], None] | None = None
        self.on_change: Callable[[str], None] | None = None
        self.on_info: Callable[[str], None] | None = None
        self._cards: list[PotCard] = []
        self._selected: str | None = None
        self._size = (0.0, 0.0)
        self._render_key: tuple | None = None
        self._reveal: list[tuple[ft.Container, list[ft.Container], ft.Container]] = []
        self._layer = ft.Stack(expand=True)
        self._root = ft.Container(
            expand=True,
            on_size_change=self._resized,
            content=ft.Stack(
                expand=True,
                controls=[
                    bg_image(BACKGROUND, left=0, top=0, right=0, bottom=0),
                    self._layer,
                ],
            ),
        )

    # --- GardenCanvas ---

    def control(self) -> ft.Control:
        return self._root

    def show(self, view: ZoneView) -> None:
        self._cards = sorted(view.cards, key=lambda card: (card.pot.x, card.pot.id))
        if self._selected not in {card.pot.id for card in self._cards}:
            self._selected = None
        self._render()

    def spawn_point(self) -> tuple[float, float]:
        """Нові горщики стають праворуч: x росте з кількістю, тож порядок на столі сталий."""
        right = max((card.pot.x for card in self._cards), default=0.0)
        return clamp_world(right + SPAWN_GAP, WORLD_SIZE / 2)

    # --- розкладка ---

    def _resized(self, e: ft.LayoutSizeChangeEvent) -> None:
        size = (float(e.width), float(e.height))
        # Ігноруємо тремтіння на 1 px під час анімації переходу.
        if abs(size[0] - self._size[0]) < 1.5 and abs(size[1] - self._size[1]) < 1.5:
            return
        self._size = size
        self._render()

    def _render(self) -> None:
        width, height = self._size
        if width <= 0 or height <= 0:
            return
        key = (
            round(width),
            round(height),
            self._selected,
            tuple((c.pot.id, c.pot.stage, c.pot.profile.species_id) for c in self._cards),
            self.on_add is not None,
        )
        if key == self._render_key:
            return
        self._render_key = key

        scale = max(width / BG_W, height / BG_H)
        img_w, img_h = BG_W * scale, BG_H * scale
        origin_x, origin_y = (width - img_w) / 2, (height - img_h) / 2

        # Видима частина стільниці: на телефоні фото обрізане з боків.
        left = max(origin_x + TABLE_LEFT * img_w, 12.0)
        right = min(origin_x + TABLE_RIGHT * img_w, width - 12.0)
        foot = origin_y + TABLE_FOOT_Y * img_h

        slots = len(self._cards) + (1 if self.on_add else 0)
        pot_w = POT_W * img_h
        pot_h = pot_w / PICTURE_RATIO
        if slots:
            fit_w = (right - left) / (slots + GAP * (slots - 1))
            if pot_w > fit_w:
                pot_w = max(fit_w, MIN_POT_W)
                pot_h = pot_w / PICTURE_RATIO
        step = pot_w * (1 + GAP)
        row = pot_w + step * (slots - 1) if slots else 0.0
        start = (left + right) / 2 - row / 2 + pot_w / 2  # центр першого місця

        controls: list[ft.Control] = []
        self._reveal = []
        for index, card in enumerate(self._cards):
            controls.extend(self._pot(card, start + index * step, foot, pot_w, pot_h))
        if self.on_add:
            controls.append(self._plus(start + len(self._cards) * step, foot, min(PLUS, pot_w * PICTURE_POT_SHARE)))
        self._layer.controls = controls
        try:
            self._layer.update()
        except Exception:  # noqa: BLE001 — ще не на сторінці, покажеться при додаванні
            return
        if self._reveal:
            items = list(self._reveal)

            async def rise() -> None:
                await asyncio.sleep(0.02)
                steps = 46
                shown = [0 for _ in items]
                for step_i in range(1, steps + 1):
                    ease = 1 - (1 - step_i / steps) ** 3
                    for item_i, (box, frames, panel) in enumerate(items):
                        span = len(frames) - 1
                        index = span if ease >= 1 else min(span, int(ease * span + 0.5))
                        box.offset = ft.Offset(0, -0.06 * ease)
                        panel.opacity = ease
                        panel.offset = ft.Offset(0, 0.28 * (1 - ease))
                        try:
                            if index != shown[item_i]:
                                frames[shown[item_i]].opacity = 0
                                frames[index].opacity = 1
                                frames[shown[item_i]].update()
                                frames[index].update()
                                shown[item_i] = index
                            box.update()
                            panel.update()
                        except Exception:  # noqa: BLE001
                            return
                    await asyncio.sleep(0.016)

            page = self._layer.page
            if page is not None:
                page.run_task(rise)

    def _pot(self, card: PotCard, cx: float, foot: float, w: float, h: float) -> list[ft.Control]:
        selected = card.pot.id == self._selected
        shadow_w, shadow_h = w * 0.6, max(w * 0.08, 4)
        picture = pot_picture(card.pot.profile.species_id, card.pot.stage)
        body: ft.Control
        if picture:
            body = pot_image(picture, w, h)
        else:
            body = _drawn_pot(card.species.glyph, w, h)
        top = foot - h * PICTURE_FOOT
        frames: list[ft.Container] = []
        if selected and picture:
            layers = [body]
            for src in _tilt_frames(picture):
                layers.append(pot_image(src, w, h))
            frames = [ft.Container(opacity=1 if index == 0 else 0, content=layer) for index, layer in enumerate(layers)]
            body = ft.Stack(controls=frames)
        pot_box = ft.Container(
            width=w,
            height=h,
            offset=ft.Offset(0, 0),
            on_click=lambda _, pot_id=card.pot.id: self._select(pot_id),
            content=body,
        )
        panel = self._panel(card, cx, top, h, animate=bool(frames)) if selected else None
        if panel is not None and frames:
            self._reveal.append((pot_box, frames, panel))
        controls: list[ft.Control] = [
            ft.Container(
                left=cx - shadow_w / 2,
                top=foot - shadow_h / 2,
                width=shadow_w,
                height=shadow_h,
                bgcolor="#000000",
                opacity=0.16 if selected and frames else 0.2,
                border_radius=100,
            ),
            ft.Container(left=cx - w / 2, top=top, width=w, height=h, content=pot_box),
        ]
        if panel is not None:
            controls.append(panel)
        return controls

    def _panel(self, card: PotCard, cx: float, top: float, h: float, *, animate: bool) -> ft.Control:
        pot_id = card.pot.id
        width = 280
        # Паростки низькі — плашка біля вінчика. Доросліші рослини вищі, тож піднімаємо вище.
        stage = GrowthStage(card.pot.stage)
        maturity = 0 if stage == GrowthStage.HARVESTED else STAGE_ORDER.index(stage)
        lift = h * (0.08 + 0.16 * maturity / max(len(STAGE_ORDER) - 1, 1))
        rim = top + h * 0.44
        above = rim - 74 - lift if animate else top - 8 - lift
        return ft.Container(
            left=min(max(cx - width / 2, 8.0), max(8.0, self._size[0] - width - 8)),
            top=max(8.0, above),
            width=width,
            opacity=0 if animate else 1,
            offset=ft.Offset(0, 0.45) if animate else ft.Offset(0, 0),
            content=ft.Container(
                padding=ft.Padding(8, 6, 8, 6),
                border_radius=16,
                bgcolor=ft.Colors.with_opacity(0.94, "#FFFFFF"),
                shadow=ft.BoxShadow(blur_radius=18, color=ft.Colors.with_opacity(0.22, "#1B2E1B"), offset=ft.Offset(0, 6)),
                content=ft.Column(
                    tight=True,
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        ft.Text(
                            f"{card.species.name} · {STAGE_LABELS[card.pot.stage]}",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color="#1B2E1B",
                            text_align=ft.TextAlign.CENTER,
                            no_wrap=True,
                        ),
                        ft.Row(
                            spacing=4,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                _chip(BTN_POT_INFO, ft.Icons.INFO_OUTLINE_ROUNDED, lambda: self.on_info(pot_id) if self.on_info else None),
                                _chip(BTN_CHANGE_POT, ft.Icons.EDIT_OUTLINED, lambda: self.on_change(pot_id) if self.on_change else None),
                                _chip(BTN_DELETE_POT, ft.Icons.DELETE_OUTLINE_ROUNDED, lambda: self.on_delete(pot_id) if self.on_delete else None, danger=True),
                            ],
                        ),
                    ],
                ),
            ),
        )

    def _plus(self, cx: float, foot: float, size: float) -> ft.Control:
        return ft.Container(
            left=cx - size / 2,
            top=foot - size,
            width=size,
            height=size,
            border_radius=size,
            bgcolor=ft.Colors.with_opacity(0.85, "#FFFFFF"),
            border=ft.Border.all(2, "#2E7D32"),
            shadow=ft.BoxShadow(blur_radius=14, color=ft.Colors.with_opacity(0.25, "#1B2E1B"), offset=ft.Offset(0, 4)),
            tooltip=BTN_PLANT,
            ink=True,
            on_click=lambda _: self.on_add() if self.on_add else None,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.ADD_ROUNDED, color="#2E7D32", size=size * 0.5),
        )

    def _select(self, pot_id: str) -> None:
        self._selected = None if self._selected == pot_id else pot_id
        self._render_key = None
        self._render()
        if self._selected:
            self._on_select_pot(pot_id)


def _tilt_frames(picture: str) -> tuple[str, ...]:
    stem = picture.rsplit("/", 1)[-1].removesuffix(".png")
    return tuple(f"pots/tilt/{stem}_{degrees}.png" for degrees in range(1, 46))


def _chip(label: str, icon: ft.IconData, on_click: Callable[[], None], danger: bool = False) -> ft.Control:
    color = "#C62828" if danger else "#2E7D32"
    return ft.Container(
        ink=True,
        border_radius=12,
        padding=ft.Padding(8, 6, 8, 6),
        on_click=lambda _: on_click(),
        content=ft.Column(
            tight=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon, size=18, color=color),
                ft.Text(label, size=11, color=color, weight=ft.FontWeight.W_600),
            ],
        ),
    )


def _drawn_pot(glyph: str, w: float, h: float) -> ft.Control:
    """Запасний горщик, коли для культури ще немає PNG: глиняний горщик і glyph з довідки."""
    # Розмір як у рендерах render_pots.py: горщик 0.62 ширини кадру, тіло ~0.3 висоти.
    pot_w, pot_h = w * PICTURE_POT_SHARE, h * 0.3
    rim_h = pot_h * 0.18
    return ft.Container(
        width=w,
        height=h,
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(glyph or "🌱", size=w * 0.28),
                ft.Container(width=pot_w * 1.06, height=rim_h, bgcolor="#A0533B", border_radius=4),
                ft.Container(
                    width=pot_w,
                    height=pot_h - rim_h,
                    margin=ft.Margin(0, 0, 0, h * (1 - PICTURE_FOOT)),
                    bgcolor="#8E4A35",
                    border_radius=ft.BorderRadius(2, 2, pot_w * 0.18, pot_w * 0.18),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("• ‿ •", size=w * 0.09, color="#2B1A14"),
                ),
            ],
        ),
    )
