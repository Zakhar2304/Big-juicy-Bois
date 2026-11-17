"""Валідація email / пароля для реєстрації та входу."""

from __future__ import annotations

import re

_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def clean_email(value: str) -> str:
    email = (value or "").strip().lower()
    if not email:
        raise ValueError("Вкажи email.")
    if len(email) > 120:
        raise ValueError("Email задовгий.")
    if not _EMAIL.match(email):
        raise ValueError("Некоректний email.")
    return email


def clean_password(value: str, *, confirm: str | None = None, registering: bool = False) -> str:
    password = value or ""
    if not password:
        raise ValueError("Вкажи пароль.")
    if len(password) < 8:
        raise ValueError("Пароль має містити щонайменше 8 символів.")
    if len(password) > 72:
        raise ValueError("Пароль задовгий (макс. 72).")
    if registering:
        if password.isdigit() or password.isalpha():
            raise ValueError("Додай і літери, і цифри в пароль.")
        if confirm is None or confirm != password:
            raise ValueError("Паролі не збігаються.")
    return password


def validate_auth_form(
    email: str,
    password: str,
    *,
    confirm: str | None = None,
    registering: bool = False,
) -> tuple[str, str]:
    return clean_email(email), clean_password(password, confirm=confirm, registering=registering)
