"""Інтервал поливу і найближчі нагадування. Формули — docs/RULES.md, розділ «Догляд»."""

from __future__ import annotations

from datetime import datetime

from app.contracts.models import CareEvent, CarePlan, PlantingProfile, Pot, SpeciesProfile


class CarePlanner:
    def interval_days(self, species: SpeciesProfile, profile: PlantingProfile) -> float:
        raise NotImplementedError("app/core/care.py interval_days — див. docs/RULES.md")

    def plan(
        self,
        pot: Pot,
        species: SpeciesProfile,
        events: list[CareEvent],
        now: datetime,
    ) -> CarePlan:
        raise NotImplementedError("app/core/care.py plan — див. docs/RULES.md")
