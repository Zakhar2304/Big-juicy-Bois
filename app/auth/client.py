"""Тонкий клієнт Supabase Auth поверх httpx (працює і в десктопі, і у вебі)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from app.auth.config import auth_configured, supabase_anon_key, supabase_url


class AuthError(Exception):
    """Помилка реєстрації / входу з зрозумілим текстом для користувача."""


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    refresh_token: str
    user_id: str
    email: str

    def to_dict(self) -> dict[str, str]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthSession | None:
        try:
            access = str(data["access_token"])
            refresh = str(data["refresh_token"])
            user_id = str(data.get("user_id") or "")
            email = str(data.get("email") or "")
        except (KeyError, TypeError):
            return None
        if not access or not refresh:
            return None
        return cls(access_token=access, refresh_token=refresh, user_id=user_id, email=email)


def _message(payload: Any, fallback: str) -> str:
    if isinstance(payload, dict):
        for key in ("msg", "error_description", "error", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return fallback


class AuthClient:
    def __init__(self) -> None:
        if not auth_configured():
            raise AuthError(
                "Додай SUPABASE_ANON_KEY у файл .env "
                "(Supabase → Project Settings → API → anon public)."
            )
        self._url = supabase_url()
        self._key = supabase_anon_key()
        self._headers = {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }

    def _parse_session(self, data: dict[str, Any]) -> AuthSession:
        user = data.get("user") if isinstance(data.get("user"), dict) else {}
        session = AuthSession(
            access_token=str(data.get("access_token") or ""),
            refresh_token=str(data.get("refresh_token") or ""),
            user_id=str(user.get("id") or data.get("user_id") or ""),
            email=str(user.get("email") or data.get("email") or ""),
        )
        if not session.access_token or not session.refresh_token:
            raise AuthError("Сервер не повернув сесію. Спробуй ще раз.")
        return session

    def sign_up(self, email: str, password: str) -> AuthSession:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{self._url}/auth/v1/signup",
                headers=self._headers,
                json={"email": email, "password": password},
            )
        data = response.json() if response.content else {}
        if response.status_code >= 400:
            raise AuthError(_message(data, "Не вдалося зареєструватися."))
        # Якщо в проєкті увімкнено підтвердження email — токенів може не бути.
        if not data.get("access_token"):
            raise AuthError(
                "Акаунт створено. Підтверди email у листі від Supabase, тоді увійди."
            )
        return self._parse_session(data)

    def sign_in(self, email: str, password: str) -> AuthSession:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{self._url}/auth/v1/token?grant_type=password",
                headers=self._headers,
                json={"email": email, "password": password},
            )
        data = response.json() if response.content else {}
        if response.status_code >= 400:
            raise AuthError(_message(data, "Невірний email або пароль."))
        return self._parse_session(data)

    def refresh(self, refresh_token: str) -> AuthSession:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{self._url}/auth/v1/token?grant_type=refresh_token",
                headers=self._headers,
                json={"refresh_token": refresh_token},
            )
        data = response.json() if response.content else {}
        if response.status_code >= 400:
            raise AuthError(_message(data, "Сесію закінчено. Увійди знову."))
        return self._parse_session(data)

    def google_authorize_url(self, redirect_to: str) -> str:
        query = urlencode(
            {
                "provider": "google",
                "redirect_to": redirect_to,
            }
        )
        return f"{self._url}/auth/v1/authorize?{query}"

    def exchange_code(self, code: str, redirect_to: str) -> AuthSession:
        """PKCE/code з redirect URL після Google."""
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{self._url}/auth/v1/token?grant_type=pkce",
                headers=self._headers,
                json={"auth_code": code, "code_verifier": "", "redirect_to": redirect_to},
            )
        # Fallback: деякі проєкти віддають токени в hash без code exchange.
        data = response.json() if response.content else {}
        if response.status_code >= 400:
            raise AuthError(_message(data, "Google-вхід не завершився. Спробуй ще раз."))
        return self._parse_session(data)

    def delete_user(self, access_token: str) -> None:
        """Видаляє поточного користувача в Supabase (потрібен увімкнений self-delete)."""
        headers = {
            "apikey": self._key,
            "Authorization": f"Bearer {access_token}",
        }
        with httpx.Client(timeout=20.0) as client:
            response = client.delete(f"{self._url}/auth/v1/user", headers=headers)
        data = response.json() if response.content else {}
        if response.status_code >= 400:
            raise AuthError(
                _message(
                    data,
                    "Не вдалося видалити акаунт. Увімкни «Allow users to delete their accounts» у Supabase Auth.",
                )
            )

    def session_from_implicit(self, fragment_or_query: dict[str, str]) -> AuthSession | None:
        access = fragment_or_query.get("access_token")
        refresh = fragment_or_query.get("refresh_token")
        if not access or not refresh:
            return None
        email = fragment_or_query.get("email") or ""
        user_id = fragment_or_query.get("user_id") or ""
        if not email or not user_id:
            claims = _jwt_claims(access)
            email = email or str(claims.get("email") or "")
            user_id = user_id or str(claims.get("sub") or "")
        return AuthSession(
            access_token=access,
            refresh_token=refresh,
            user_id=user_id,
            email=email,
        )


def _jwt_claims(token: str) -> dict[str, Any]:
    """Читає payload JWT без перевірки підпису — лише щоб показати email після Google."""
    import base64
    import json

    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}
