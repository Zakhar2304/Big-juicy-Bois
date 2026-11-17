"""Віддає вибрані рядки віджету на домашньому екрані телефону.

На комп'ютері й у браузері лишається лише файл. На iPhone і Android той самий
текст іде в нативний віджет: «До поливки 1 година».
"""

from __future__ import annotations

import json

import flet as ft

from app.shell.widget_prefs import prefs_path

_last: tuple[str, ...] | None = None
_service = None


def push_board(lines: list[str]) -> None:
    global _last
    packed = tuple(line for line in lines if line.strip())
    if packed == _last:
        return
    _last = packed
    _save(list(packed))
    _push_native(list(packed))


def _save(lines: list[str]) -> None:
    try:
        file = prefs_path().with_name("phone_widget.json")
    except OSError:
        return
    payload = json.dumps({"lines": lines}, ensure_ascii=False)
    tmp = file.with_suffix(".tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(file)
    except OSError:
        return


def _push_native(lines: list[str]) -> None:
    try:
        page = ft.context.page
    except RuntimeError:
        return
    raw = getattr(page.platform, "value", page.platform)
    if str(raw) not in {"ios", "android", "android_tv"}:
        return

    async def send() -> None:
        global _service
        try:
            from happygarden_phone import PhoneWidget
        except ImportError:
            return
        try:
            if _service is None:
                _service = PhoneWidget()
            await _service.publish(lines)
        except Exception:
            return

    page.run_task(send)
