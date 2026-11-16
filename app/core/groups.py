"""Збирання горщиків одного виду в групу. Поріг — GROUP_MIN_POTS."""

from __future__ import annotations

from app.contracts.models import CropGroup, Pot


class GroupBuilder:
    def suggest(
        self,
        pots: list[Pot],
        existing: list[CropGroup],
        titles: dict[str, str],
    ) -> tuple[list[CropGroup], list[Pot]]:
        raise NotImplementedError("app/core/groups.py suggest — див. docs/RULES.md")
