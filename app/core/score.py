"""Очки грядки для екрана друзів. Формула — docs/RULES.md, розділ «Очки»."""

from __future__ import annotations

from app.contracts.models import CareEvent, FarmScore, Friend, LeaderboardRow, Pot, Zone


class Scoreboard:
    def score_zone(
        self,
        zone: Zone,
        pots: list[Pot],
        events: list[CareEvent],
        nickname: str,
    ) -> FarmScore:
        raise NotImplementedError("app/core/score.py score_zone — див. docs/RULES.md")

    def leaderboard(self, you: FarmScore, friends: list[Friend]) -> list[LeaderboardRow]:
        raise NotImplementedError("app/core/score.py leaderboard — див. docs/RULES.md")
