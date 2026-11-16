"""Ріст горщика. Формули — docs/RULES.md, розділ «Симуляція»."""

from __future__ import annotations

from datetime import datetime

from app.contracts.ids import new_id
from app.contracts.models import CareAction, CareEvent, PlantingProfile, Pot, SpeciesProfile, StageMark
from app.contracts.timeline import ideal_timeline


class GrowthEngine:
    def plant(
        self,
        zone_id: str,
        profile: PlantingProfile,
        x: float,
        y: float,
        species: SpeciesProfile,
    ) -> tuple[Pot, CareEvent]:
        raise NotImplementedError("app/core/growth.py plant — див. docs/RULES.md")

    def advance(
        self,
        pot: Pot,
        species: SpeciesProfile,
        events: list[CareEvent],
        now: datetime,
    ) -> Pot:
        raise NotImplementedError("app/core/growth.py advance — див. docs/RULES.md")

    def timeline(self, profile: PlantingProfile, species: SpeciesProfile) -> list[StageMark]:
        """Нормативний календар. Ґрунт сюди не входить: він впливає лише в advance()."""
        del profile
        return list(ideal_timeline(species))

    def make_event(self, pot_id: str, action: CareAction, now: datetime, note: str = "") -> CareEvent:
        return CareEvent(id=new_id(), pot_id=pot_id, action=action, at=now, note=note)
