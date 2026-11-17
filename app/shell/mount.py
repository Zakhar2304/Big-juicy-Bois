"""Збирає екрани. Сцену зони отримує ззовні (make_canvas) і не імпортує app.garden."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import flet as ft

from app.auth.client import AuthClient, AuthError, AuthSession
from app.auth.session_store import SessionStore
from app.contracts.errors import ZoneNotFound
from app.contracts.labels import APP_NAME, BTN_BACK, EMPTY_POTS, ZONE_LABELS
from app.contracts.models import Zone, ZoneKind
from app.contracts.ports import Actions, MakeCanvas
from app.shell.auth_page import auth_view, clear_oauth_route, consume_oauth_redirect
from app.shell.friends_page import friends_view
from app.shell.home import home_view
from app.shell.onboarding import onboarding_view
from app.shell.settings_page import settings_view
from app.shell.perf import bg_image
from app.shell.theme import BG, CARD, GREEN, TEXT, fill
from app.shell.zone_page import zone_view

FARM_BG = "backgrounds/farm.jpg"  # те саме фото, що під столом FarmBench

# Зони, для яких уже є сцена (стіл із горщиками). Інші поки відкривають заглушку.
SCENE_KINDS = {ZoneKind.FARM}

ZOOM_MS = 380
# Точка, до якої «летимо»: стіл у колі меню і стіл на сцені.
MENU_FOCUS = ft.Alignment(0, 0.1)
TABLE_FOCUS = ft.Alignment(0, 0.45)


def _pick_zone(actions: Actions) -> Zone | None:
    """Зона одна — вона. Кілька — last_zone_id, інакше перша."""
    zones = actions.list_zones()
    if not zones:
        return None
    last = actions.get_settings().last_zone_id
    return next((zone for zone in zones if zone.id == last), zones[0])


def _zone_stub(zone: Zone, pots: int, on_back: Callable[[], None]) -> ft.Control:
    """Тимчасовий екран для теплиці й городу, поки для них немає сцени."""
    return ft.Container(
        expand=True,
        bgcolor=CARD,
        content=ft.SafeArea(
            expand=True,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    controls=[
                        ft.TextButton(BTN_BACK, icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda _: on_back()),
                        ft.Text(zone.name, size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text(f"{ZONE_LABELS[zone.kind]} · {zone.territory}", color=TEXT),
                        ft.Text(EMPTY_POTS if pots == 0 else f"🌱 × {pots}", color=GREEN, size=16),
                    ],
                ),
            ),
        ),
    )


def mount(page: ft.Page, actions: Actions, make_canvas: MakeCanvas) -> None:
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=GREEN)
    page.bgcolor = BG
    page.padding = 0
    page.spacing = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    # Календарі (DatePicker) українською.
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("uk", "UA")],
        current_locale=ft.Locale("uk", "UA"),
    )

    current: dict[str, ft.Control | None] = {"screen": None}

    def show(control: ft.Control) -> None:
        current["screen"] = control
        page.controls.clear()
        page.add(control)

    animating = {"busy": False}

    def transition(target: ft.Control, forward: bool) -> None:
        """Наближення без sleep на UI-потоці: інакше сайт і телефон зависають на час анімації."""
        old = current["screen"]
        if old is None or animating["busy"]:
            show(target)
            return
        curve = ft.AnimationCurve.EASE_IN_OUT
        for control in (old, target):
            control.animate_scale = ft.Animation(ZOOM_MS, curve)
            control.animate_opacity = ft.Animation(ZOOM_MS * 2 // 3, curve)
        old_focus, new_focus = (MENU_FOCUS, TABLE_FOCUS) if forward else (TABLE_FOCUS, MENU_FOCUS)
        target.scale = ft.Scale(0.75 if forward else 1.8, alignment=new_focus)
        target.opacity = 0
        old_layer = fill(ft.Container(content=old))
        stage = ft.Stack(expand=True, controls=[fill(ft.Container(content=target)), old_layer])
        current["screen"] = stage
        page.controls.clear()
        page.add(stage)
        animating["busy"] = True

        async def play() -> None:
            try:
                await asyncio.sleep(0.03)
                old.scale = ft.Scale(2.0 if forward else 0.7, alignment=old_focus)
                old.opacity = 0
                target.scale = ft.Scale(1.0, alignment=new_focus)
                target.opacity = 1
                page.update()
                await asyncio.sleep(ZOOM_MS / 1000)
                if old_layer in stage.controls:
                    stage.controls.remove(old_layer)
                    stage.update()
            finally:
                animating["busy"] = False

        page.run_task(play)

    def open_friends() -> None:
        zone = _pick_zone(actions)
        show(friends_view(actions, zone.id if zone else "", go_home))

    def delete_account() -> None:
        session = auth_state["session"]
        if session is None:
            logout()
            return
        try:
            AuthClient().delete_user(session.access_token)
        except AuthError as exc:
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Не вдалося видалити"),
                    content=ft.Text(str(exc)),
                    actions=[ft.TextButton("OK", on_click=lambda _: page.pop_dialog())],
                )
            )
            return
        wipe = getattr(actions, "wipe_local", None)
        if callable(wipe):
            wipe()
        logout()

    def open_settings() -> None:
        show(
            settings_view(
                actions,
                go_home,
                page=page,
                on_logout=logout,
                on_delete_account=delete_account,
            )
        )

    def scene_for(zone: Zone) -> Callable[[], ft.Control] | None:
        """Легкий фон меню: лише фото столу. Живий FarmBench тут лагав (будувався двічі)."""
        if zone.kind not in SCENE_KINDS:
            return None

        def build() -> ft.Control:
            return bg_image(FARM_BG)

        return build

    def home(animated: bool = False) -> ft.Control:
        screen = home_view(
            actions,
            on_open_zone=open_zone,
            on_friends=open_friends,
            on_settings=open_settings,
            on_new_zone=go_new_zone,
            scene_for=scene_for,
        )
        if animated:
            transition(screen, forward=False)
        else:
            show(screen)
        return screen

    def go_home() -> None:
        home()

    def back_home() -> None:
        home(animated=True)

    def logout() -> None:
        store.clear()
        auth_state["session"] = None
        go_auth(register=False)

    def go_onboarding() -> None:
        session = auth_state["session"]
        show(
            onboarding_view(
                actions,
                on_done=go_home,
                account_email=session.email if session else None,
                on_logout=logout,
            )
        )

    def go_new_zone() -> None:
        show(onboarding_view(actions, on_done=go_home, ask_nickname=False, on_cancel=go_home))

    def open_zone() -> None:
        zone = _pick_zone(actions)
        if zone is None:
            go_onboarding()
            return
        try:
            view = actions.open_zone(zone.id)
        except ZoneNotFound:
            go_home()
            return
        if zone.kind in SCENE_KINDS:
            select: dict[str, Callable[[str], None]] = {}
            canvas = make_canvas(
                lambda pot_id: select["open"](pot_id) if "open" in select else None,
                lambda _pot_id, _x, _y: None,
            )
            screen = zone_view(
                actions,
                view,
                canvas,
                on_back=back_home,
                on_changed=lambda _v: None,
                bind_select=lambda handler: select.__setitem__("open", handler),
            )
        else:
            screen = _zone_stub(view.zone, len(view.cards), back_home)
        transition(screen, forward=True)

    store = SessionStore()
    auth_state: dict[str, AuthSession | None] = {"session": None}

    def enter_app() -> None:
        if actions.list_zones():
            go_home()
        else:
            go_onboarding()

    def go_auth(*, register: bool = True) -> None:
        show(auth_view(page, on_authed, start_register=register))

    def on_authed(session: AuthSession) -> None:
        store.save(session)
        auth_state["session"] = session
        clear_oauth_route(page)
        enter_app()

    def restore_session() -> AuthSession | None:
        oauth = consume_oauth_redirect(page)
        if oauth:
            store.save(oauth)
            return oauth
        saved = store.load()
        if not saved:
            return None
        try:
            refreshed = AuthClient().refresh(saved.refresh_token)
            store.save(refreshed)
            return refreshed
        except AuthError:
            store.clear()
            return None
        except Exception:  # noqa: BLE001 — офлайн: лишаємо збережену сесію
            return saved

    def try_oauth_from_route(_: ft.Event | None = None) -> None:
        if auth_state["session"] is not None:
            return
        oauth = consume_oauth_redirect(page)
        if oauth:
            on_authed(oauth)

    page.on_route_change = try_oauth_from_route

    session = restore_session()
    if session:
        on_authed(session)
    else:
        go_auth(register=True)
        # Інколи hash з Google з’являється вже після першого кадру.
        try_oauth_from_route()

