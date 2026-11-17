"""Палітра і фон теплиці. Спільне для всіх екранів оболонки."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.shell.perf import bg_image

BG = "#F4F7F2"
GREEN = "#2E7D32"
CARD = "#FFFFFF"
TEXT = "#1B2E1B"
DANGER = "#C62828"
WARNING = "#EF6C00"
INFO = "#1565C0"

# Шлях відносно assets/. Оригінал лежить у корені, тут легша копія для вебу.
GREENHOUSE_BG = "backgrounds/greenhouse.jpg"

MIN_TAP = 44


def center_sheet(body: ft.Column) -> ft.Control:
    """Прокрутка по центру: на телефоні на всю ширину, на широкому екрані не ширше за картку."""

    def fit(page: ft.Page | None) -> None:
        if page is None or not page.width:
            return
        width = min(460.0, max(280.0, float(page.width) - 28))
        if body.width != width:
            body.width = width

    class _Frame(ft.Column):
        def before_update(self) -> None:
            fit(self.page)

    return _Frame(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[ft.Container(padding=ft.Padding(14, 6, 14, 28), content=body)],
    )


def mounted(control: ft.Control) -> bool:
    """Чи контрол уже на сторінці. До першого кадру page кидає RuntimeError."""
    try:
        return control.page is not None
    except RuntimeError:
        return False


def fill(control: ft.Control) -> ft.Control:
    """Розтягнути шар на весь Stack."""
    control.left = 0
    control.top = 0
    control.right = 0
    control.bottom = 0
    return control


def greenhouse_backdrop(
    blur: float = 18,
    clear_center: bool = True,
    veil: float = 0.12,
    make_scene: Callable[[], ft.Control] | None = None,
) -> list[ft.Control]:
    """Шари фону для Stack: розмита сцена, а ближче до центру вона чітка.

    make_scene будує сцену (за замовчуванням фото теплиці). Її кличуть двічі:
    один екземпляр розмивається, другий видно крізь коло.

    1. Сама сцена.
    2. Розмиття всього, що позаду (backdrop blur), і легка біла вуаль.
    3. Та сама картинка ще раз, але з радіальною маскою: у центрі видно повністю,
       до країв плавно зникає в розмиття.
    """
    # Одну картинку двічі дорожче: жива сцена з горщиками ×2 лагала меню.
    # Для фото достатньо одного шару + вуаль; чітке коло — лише якщо сцена легка.
    scene = make_scene or (lambda: bg_image(GREENHOUSE_BG))
    base = scene()
    layers: list[ft.Control] = [
        fill(ft.Container(content=base)),
        fill(
            ft.Container(
                # Менший blur швидший на телефоні й у браузері.
                blur=ft.Blur(min(blur, 12), min(blur, 12), ft.BlurTileMode.MIRROR),
                bgcolor=ft.Colors.with_opacity(veil, CARD),
            )
        ),
    ]
    if clear_center and make_scene is None:
        layers.append(
            fill(
                ft.ShaderMask(
                    content=bg_image(GREENHOUSE_BG),
                    shader=ft.RadialGradient(
                        center=ft.Alignment(0, -0.02),
                        radius=0.5,
                        colors=[
                            ft.Colors.WHITE,
                            ft.Colors.WHITE,
                            ft.Colors.with_opacity(0.4, ft.Colors.WHITE),
                            ft.Colors.TRANSPARENT,
                        ],
                        stops=[0.0, 0.36, 0.68, 1.0],
                    ),
                    blend_mode=ft.BlendMode.DST_IN,
                )
            )
        )
    return layers

