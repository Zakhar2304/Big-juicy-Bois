"""Екран входу / реєстрації: email+пароль, Google, валідація, legal-посилання знизу."""

from __future__ import annotations

from collections.abc import Callable
from urllib.parse import parse_qs, urlparse

import flet as ft

from app.auth.client import AuthClient, AuthError, AuthSession
from app.auth.config import CONTACT_EMAIL, auth_configured, legal_url, public_site_url
from app.auth.validation import validate_auth_form
from app.contracts.labels import (
    APP_NAME,
    AUTH_SUBTITLE_SIGN_IN,
    AUTH_SUBTITLE_SIGN_UP,
    BTN_GOOGLE,
    BTN_HAVE_ACCOUNT,
    BTN_NO_ACCOUNT,
    BTN_SIGN_IN,
    BTN_SIGN_UP,
    LBL_EMAIL,
    LBL_MARKETING,
    LBL_PASSWORD,
    LBL_PASSWORD_CONFIRM,
    LBL_PRIVACY,
    LBL_SUPPORT,
    LBL_TERMS,
)
from app.shell.theme import CARD, DANGER, GREEN, MIN_TAP, TEXT, fill, greenhouse_backdrop

FORM_WIDTH = 420


def _redirect_url(page: ft.Page) -> str:
    """Куди Supabase повертає після Google. oauth_return.html перекладає hash у route."""
    base = public_site_url()
    if not base:
        current = getattr(page, "url", None) or ""
        if isinstance(current, str) and current.startswith("http"):
            base = current.split("#", 1)[0].split("?", 1)[0].rstrip("/")
        else:
            base = "http://127.0.0.1:56950"
    # У Flet web файли з assets/ віддаються з кореня: /oauth_return.html
    return f"{base.rstrip('/')}/oauth_return.html"


def oauth_params_from_page(page: ft.Page) -> dict[str, str]:
    """Збирає access_token/refresh_token з route/url/query після Google redirect."""
    merged: dict[str, str] = {}

    try:
        query_dict = page.query.to_dict
        if isinstance(query_dict, dict):
            merged.update({str(k): str(v) for k, v in query_dict.items() if v})
    except Exception:  # noqa: BLE001
        pass

    chunks: list[str] = []
    for raw in (getattr(page, "route", None), getattr(page, "url", None)):
        if isinstance(raw, str) and raw.strip():
            chunks.append(raw.strip())

    for raw in chunks:
        text = raw
        if "://" in text:
            parsed = urlparse(text)
            if parsed.fragment:
                text = parsed.fragment
            elif parsed.query:
                text = parsed.query
            else:
                text = parsed.path
        text = text.lstrip("#")
        if text.startswith("/?"):
            text = text[2:]
        elif text.startswith("?"):
            text = text[1:]
        elif text.startswith("/") and "access_token=" in text:
            # Flet hash-route інколи дає "/access_token=..."
            text = text.lstrip("/")
        if "access_token=" in text:
            text = text[text.index("access_token=") :]
        if any(key in text for key in ("access_token=", "refresh_token=", "code=")):
            parsed_qs = parse_qs(text, keep_blank_values=False)
            for key, values in parsed_qs.items():
                if values and values[0]:
                    merged[key] = values[0]
    return merged


def auth_view(
    page: ft.Page,
    on_success: Callable[[AuthSession], None],
    *,
    start_register: bool = True,
) -> ft.Control:
    registering = {"value": start_register}
    busy = {"value": False}

    title = ft.Text(BTN_SIGN_UP if start_register else BTN_SIGN_IN, size=26, weight=ft.FontWeight.BOLD, color=TEXT, text_align=ft.TextAlign.CENTER)
    subtitle = ft.Text(
        AUTH_SUBTITLE_SIGN_UP if start_register else AUTH_SUBTITLE_SIGN_IN,
        size=14,
        color=ft.Colors.with_opacity(0.7, TEXT),
        text_align=ft.TextAlign.CENTER,
    )
    email = ft.TextField(
        label=LBL_EMAIL,
        keyboard_type=ft.KeyboardType.EMAIL,
        autofill_hints=[ft.AutofillHint.EMAIL],
        border_radius=12,
        autofocus=True,
    )
    password = ft.TextField(
        label=LBL_PASSWORD,
        password=True,
        can_reveal_password=True,
        autofill_hints=[ft.AutofillHint.PASSWORD],
        border_radius=12,
    )
    confirm = ft.TextField(
        label=LBL_PASSWORD_CONFIRM,
        password=True,
        can_reveal_password=True,
        autofill_hints=[ft.AutofillHint.NEW_PASSWORD],
        border_radius=12,
        visible=start_register,
    )
    error = ft.Text("", color=DANGER, visible=False, size=13)
    primary = ft.FilledButton(
        content=ft.Text(BTN_SIGN_UP if start_register else BTN_SIGN_IN, size=16, weight=ft.FontWeight.W_600),
        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
        bgcolor=GREEN,
        color=CARD,
        height=MIN_TAP + 8,
    )
    toggle = ft.TextButton(BTN_HAVE_ACCOUNT if start_register else BTN_NO_ACCOUNT)

    async def open_link(url: str) -> None:
        await ft.UrlLauncher().launch_url(url)

    def link_btn(label: str, page_name: str) -> ft.Control:
        return ft.TextButton(
            label,
            style=ft.ButtonStyle(color=ft.Colors.with_opacity(0.75, TEXT)),
            on_click=lambda _, name=page_name: page.run_task(open_link, legal_url(name)),
        )

    legal = ft.Column(
        tight=True,
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                wrap=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    link_btn(LBL_PRIVACY, "privacy"),
                    link_btn(LBL_TERMS, "terms"),
                    link_btn(LBL_SUPPORT, "support"),
                    link_btn(LBL_MARKETING, "marketing"),
                ],
            ),
            ft.TextButton(
                CONTACT_EMAIL,
                icon=ft.Icons.MAIL_OUTLINE_ROUNDED,
                on_click=lambda _: page.run_task(open_link, f"mailto:{CONTACT_EMAIL}"),
            ),
        ],
    )

    def set_error(message: str) -> None:
        error.value = message
        error.visible = bool(message)
        error.update()

    def set_mode(is_register: bool) -> None:
        registering["value"] = is_register
        title.value = BTN_SIGN_UP if is_register else BTN_SIGN_IN
        subtitle.value = AUTH_SUBTITLE_SIGN_UP if is_register else AUTH_SUBTITLE_SIGN_IN
        confirm.visible = is_register
        primary.content = ft.Text(
            BTN_SIGN_UP if is_register else BTN_SIGN_IN,
            size=16,
            weight=ft.FontWeight.W_600,
        )
        toggle.text = BTN_HAVE_ACCOUNT if is_register else BTN_NO_ACCOUNT
        set_error("")
        for control in (title, subtitle, confirm, primary, toggle):
            control.update()

    def finish(session: AuthSession) -> None:
        busy["value"] = False
        on_success(session)

    def submit(_: ft.Event | None = None) -> None:
        if busy["value"]:
            return
        try:
            mail, secret = validate_auth_form(
                email.value or "",
                password.value or "",
                confirm=confirm.value or "",
                registering=registering["value"],
            )
        except ValueError as exc:
            set_error(str(exc))
            return
        if not auth_configured():
            set_error(
                "Додай SUPABASE_ANON_KEY у .env (Supabase → Project Settings → API)."
            )
            return
        busy["value"] = True
        set_error("")

        def work() -> None:
            try:
                client = AuthClient()
                session = (
                    client.sign_up(mail, secret)
                    if registering["value"]
                    else client.sign_in(mail, secret)
                )
            except AuthError as exc:
                busy["value"] = False
                set_error(str(exc))
                return
            except Exception as exc:  # noqa: BLE001
                busy["value"] = False
                set_error(f"Помилка мережі: {exc}")
                return
            finish(session)

        page.run_thread(work)

    async def google_sign_in(_: ft.Event | None = None) -> None:
        if busy["value"]:
            return
        if not auth_configured():
            set_error(
                "Додай SUPABASE_ANON_KEY у .env (Supabase → Project Settings → API)."
            )
            return
        try:
            client = AuthClient()
            redirect = _redirect_url(page)
            url = client.google_authorize_url(redirect)
            # Та сама вкладка: інакше токени приходять «в інше вікно», а тут лишається форма.
            await ft.UrlLauncher().launch_url(url, web_only_window_name="_self")
        except AuthError as exc:
            set_error(str(exc))
        except Exception as exc:  # noqa: BLE001
            set_error(f"Не вдалося відкрити Google: {exc}")

    primary.on_click = submit
    email.on_submit = lambda _: password.focus()
    password.on_submit = lambda _: confirm.focus() if registering["value"] else submit()
    confirm.on_submit = submit
    toggle.on_click = lambda _: set_mode(not registering["value"])

    for field in (email, password, confirm):
        field.on_change = lambda _: set_error("") if error.visible else None

    form = ft.Container(
        width=FORM_WIDTH,
        padding=28,
        border_radius=24,
        bgcolor=ft.Colors.with_opacity(0.92, CARD),
        shadow=ft.BoxShadow(blur_radius=40, color=ft.Colors.with_opacity(0.18, TEXT), offset=ft.Offset(0, 12)),
        content=ft.Column(
            tight=True,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Icon(ft.Icons.ECO_ROUNDED, color=GREEN, size=40),
                ft.Text(APP_NAME, size=28, weight=ft.FontWeight.BOLD, color=TEXT, text_align=ft.TextAlign.CENTER),
                title,
                subtitle,
                ft.Container(height=2),
                # Google першим — це основний вхід, не «стара» email-форма.
                ft.FilledButton(
                    content=ft.Text(BTN_GOOGLE, size=15, weight=ft.FontWeight.W_600),
                    icon=ft.Icons.ACCOUNT_CIRCLE_ROUNDED,
                    bgcolor="#FFFFFF",
                    color=TEXT,
                    style=ft.ButtonStyle(
                        bgcolor="#FFFFFF",
                        color=TEXT,
                        side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.25, TEXT)),
                    ),
                    height=MIN_TAP + 8,
                    on_click=google_sign_in,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(expand=True, height=1, bgcolor=ft.Colors.with_opacity(0.15, TEXT)),
                        ft.Text("або email", size=12, color=ft.Colors.with_opacity(0.6, TEXT)),
                        ft.Container(expand=True, height=1, bgcolor=ft.Colors.with_opacity(0.15, TEXT)),
                    ],
                ),
                email,
                password,
                confirm,
                error,
                primary,
                toggle,
                ft.Container(height=4),
                legal,
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


def consume_oauth_redirect(page: ft.Page) -> AuthSession | None:
    """Якщо після Google повернулись з access_token / code у URL — збираємо сесію."""
    merged = oauth_params_from_page(page)
    if not merged:
        return None
    if not auth_configured():
        return None
    try:
        client = AuthClient()
    except AuthError:
        return None
    session = client.session_from_implicit(merged)
    if session:
        return session
    code = merged.get("code")
    if code:
        try:
            return client.exchange_code(code, _redirect_url(page))
        except AuthError:
            return None
    return None


def clear_oauth_route(page: ft.Page) -> None:
    """Прибирає токени з адресного рядка після успішного входу."""
    route = getattr(page, "route", "") or ""
    if "access_token=" in route or "refresh_token=" in route or "code=" in route:
        try:
            page.go("/")
        except Exception:  # noqa: BLE001
            page.route = "/"
            page.update()
