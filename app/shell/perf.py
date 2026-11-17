"""Спільні налаштування швидкості для картинок і анімацій."""

from __future__ import annotations

import flet as ft

# Телефон ~390–430 CSS-px; рендер у 2× вистачає, 2560 px лише їсть пам'ять.
BG_CACHE_W = 1280
POT_CACHE_MAX = 512


def bg_image(src: str, **kwargs) -> ft.Image:
    """Фон сцени: середня якість і обмежений кеш декодера."""
    return ft.Image(
        src=src,
        fit=kwargs.pop("fit", ft.BoxFit.COVER),
        gapless_playback=True,
        filter_quality=ft.FilterQuality.MEDIUM,
        cache_width=BG_CACHE_W,
        **kwargs,
    )


def pot_image(src: str, width: float, height: float) -> ft.Image:
    """PNG горщика: кеш за розміром на екрані, без зайвого апскейлу."""
    cw = max(32, min(POT_CACHE_MAX, int(width * 2)))
    ch = max(32, min(POT_CACHE_MAX, int(height * 2)))
    return ft.Image(
        src=src,
        width=width,
        height=height,
        fit=ft.BoxFit.CONTAIN,
        gapless_playback=True,
        filter_quality=ft.FilterQuality.MEDIUM,
        cache_width=cw,
        cache_height=ch,
    )
