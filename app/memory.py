"""Локальна пам'ять грядки поверх PreviewActions.

Зони, горщики, журнал догляду, друзі й налаштування пишуться в
Documents/HappyGarden/garden.json і читаються при наступному запуску.
Культури й погода лишаються з довідки та Open-Meteo.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from app.contracts.codec import (
    dump,
    event_from_dict,
    event_to_dict,
    friend_from_dict,
    friend_to_dict,
    group_from_dict,
    group_to_dict,
    load,
    pot_from_dict,
    pot_to_dict,
    settings_from_dict,
    settings_to_dict,
    zone_from_dict,
    zone_to_dict,
)
from app.contracts.models import Settings, SoilType, ZoneView
from app.knowledge.weather import WeatherService
from app.wiring.preview import PreviewActions


def garden_file() -> Path:
    home = os.environ.get("CFFIXED_USER_HOME") or os.environ.get("HOME") or str(Path.home())
    folder = Path(home) / "Documents" / "HappyGarden"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "garden.json"


class SavedGarden(PreviewActions):
    """PreviewActions, який після кожної зміни перезаписує garden.json."""

    def __init__(self, weather: WeatherService | None = None) -> None:
        super().__init__(weather)
        self._path = garden_file()
        self._writing = False
        self._load()

    def create_zone(self, name: str, kind, territory: str):
        zone = super().create_zone(name, kind, territory)
        self._save()
        return zone

    def plant(
        self,
        zone_id: str,
        name: str,
        variety: str,
        soil: SoilType,
        x: float,
        y: float,
        planted_at: datetime | None = None,
    ) -> ZoneView:
        view = super().plant(zone_id, name, variety, soil, x, y, planted_at)
        self._save()
        return view

    def move_pot(self, zone_id: str, pot_id: str, x: float, y: float) -> ZoneView:
        view = super().move_pot(zone_id, pot_id, x, y)
        self._save()
        return view

    def water(self, zone_id: str, pot_id: str, at: datetime | None = None) -> ZoneView:
        view = super().water(zone_id, pot_id, at)
        self._save()
        return view

    def fertilize(self, zone_id: str, pot_id: str, at: datetime | None = None) -> ZoneView:
        view = super().fertilize(zone_id, pot_id, at)
        self._save()
        return view

    def harvest(self, zone_id: str, pot_id: str) -> ZoneView:
        view = super().harvest(zone_id, pot_id)
        self._save()
        return view

    def group_crops(self, zone_id: str) -> ZoneView:
        view = super().group_crops(zone_id)
        self._save()
        return view

    def shift_days(self, delta: int) -> int:
        offset = super().shift_days(delta)
        self._save()
        return offset

    def save_settings(self, settings: Settings) -> Settings:
        saved = super().save_settings(settings)
        self._save()
        return saved

    def add_friend(self, nickname: str, points: int) -> list:
        rows = super().add_friend(nickname, points)
        self._save()
        return rows

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            data = load(self._path.read_text(encoding="utf-8"))
            self.settings = settings_from_dict(data.get("settings"))
            self.zones = [zone_from_dict(item) for item in data.get("zones", [])]
            self.pots = [pot_from_dict(item) for item in data.get("pots", [])]
            self.groups = [group_from_dict(item) for item in data.get("groups", [])]
            self.friends = [friend_from_dict(item) for item in data.get("friends", [])]
            self.events = [event_from_dict(item) for item in data.get("events", [])]
        except (OSError, KeyError, TypeError, ValueError):
            return

    def _save(self) -> None:
        if self._writing:
            return
        self._writing = True
        try:
            payload = {
                "settings": settings_to_dict(self.settings),
                "zones": [zone_to_dict(zone) for zone in self.zones],
                "pots": [pot_to_dict(pot) for pot in self.pots],
                "groups": [group_to_dict(group) for group in self.groups],
                "friends": [friend_to_dict(friend) for friend in self.friends],
                "events": [event_to_dict(event) for event in self.events],
            }
            temporary = self._path.with_suffix(".json.tmp")
            temporary.write_text(dump(payload), encoding="utf-8")
            temporary.replace(self._path)
        finally:
            self._writing = False
