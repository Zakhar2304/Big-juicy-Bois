"""Open-Meteo. httpx імпортуй усередині alerts, щоб решта пакета жила без мережі на старті."""

from __future__ import annotations

from datetime import datetime

from app.contracts.models import SpeciesProfile, WeatherAlert


class WeatherService:
    def __init__(self) -> None:
        self._geo_cache: dict[str, tuple[float, float]] = {}

    def alerts(self, territory: str, species: SpeciesProfile, now: datetime) -> list[WeatherAlert]:
        raise NotImplementedError("app/knowledge/weather.py alerts — див. TASK.md")
