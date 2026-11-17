"""Читає ключі з .env. Секрет Google у застосунок не потрапляє — лише в панелі Supabase."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "zakhar.zavhorodnii.26@kse.org.ua").strip()


def _public_fallback() -> tuple[str, str]:
    try:
        from app.auth import public_keys
    except Exception:  # noqa: BLE001
        return "https://mkkxnfodswubsdbjziwp.supabase.co", ""
    return (
        (getattr(public_keys, "SUPABASE_URL", "") or "").rstrip("/"),
        (getattr(public_keys, "SUPABASE_ANON_KEY", "") or "").strip(),
    )


@lru_cache(maxsize=1)
def supabase_url() -> str:
    env = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    if env:
        return env
    return _public_fallback()[0] or "https://mkkxnfodswubsdbjziwp.supabase.co"


@lru_cache(maxsize=1)
def supabase_anon_key() -> str:
    # Новий формат Supabase: publishable ≈ anon для клієнта.
    for name in ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"):
        env = (os.getenv(name) or "").strip()
        if env:
            return env
    return _public_fallback()[1]


def supabase_secret_key() -> str:
    """Лише для серверних скриптів. У клієнтський UI / IPA не передавати."""
    return (os.getenv("SUPABASE_SECRET_KEY") or "").strip()


def public_site_url() -> str:
    return (os.getenv("PUBLIC_SITE_URL") or "").rstrip("/")


def google_web_client_id() -> str:
    return (os.getenv("GOOGLE_WEB_CLIENT_ID") or "").strip()


def google_ios_client_id() -> str:
    return (os.getenv("GOOGLE_IOS_CLIENT_ID") or "").strip()


def legal_url(page: str) -> str:
    """HTTPS-сторінка політики, або mailto, якщо сайт ще не опубліковано."""
    base = public_site_url()
    if base:
        return f"{base}/legal/{page}.html"
    return f"mailto:{CONTACT_EMAIL}?subject=HappyGarden%20{page}"


def auth_configured() -> bool:
    return bool(supabase_url() and supabase_anon_key())
