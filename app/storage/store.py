"""SQLite. У колонці data лежить JSON з app.contracts.codec."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.contracts.codec import (
    event_from_dict,
    event_to_dict,
    pot_from_dict,
    pot_to_dict,
    settings_from_dict,
    settings_to_dict,
    zone_from_dict,
    zone_to_dict,
)
from app.contracts.models import CareEvent, Pot, Settings, Zone


class GardenStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self.schema = str(Path(__file__).with_name("schema.sql"))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.executescript(Path(self.schema).read_text(encoding="utf-8"))
        self._db.commit()

    def load_garden(self) -> tuple[Settings, list[Zone], list[Pot], list[CareEvent]]:
        settings_row = self._db.execute("SELECT data FROM settings WHERE id = 1").fetchone()
        settings = settings_from_dict(json.loads(settings_row[0]) if settings_row else None)
        zones = [zone_from_dict(json.loads(row[0])) for row in self._db.execute("SELECT data FROM zones")]
        pots = [pot_from_dict(json.loads(row[0])) for row in self._db.execute("SELECT data FROM pots")]
        events = [event_from_dict(json.loads(row[0])) for row in self._db.execute("SELECT data FROM events")]
        return settings, zones, pots, events

    def save_garden(
        self,
        settings: Settings,
        zones: list[Zone],
        pots: list[Pot],
        events: list[CareEvent],
    ) -> None:
        cur = self._db.cursor()
        cur.execute("DELETE FROM settings")
        cur.execute(
            "INSERT INTO settings (id, data) VALUES (1, ?)",
            (json.dumps(settings_to_dict(settings), ensure_ascii=False),),
        )
        cur.execute("DELETE FROM zones")
        cur.executemany(
            "INSERT INTO zones (id, data) VALUES (?, ?)",
            [(zone.id, json.dumps(zone_to_dict(zone), ensure_ascii=False)) for zone in zones],
        )
        cur.execute("DELETE FROM pots")
        cur.executemany(
            "INSERT INTO pots (id, zone_id, data) VALUES (?, ?, ?)",
            [(pot.id, pot.zone_id, json.dumps(pot_to_dict(pot), ensure_ascii=False)) for pot in pots],
        )
        cur.execute("DELETE FROM events")
        cur.executemany(
            "INSERT INTO events (id, pot_id, zone_id, data) VALUES (?, ?, ?, ?)",
            [
                (
                    event.id,
                    event.pot_id,
                    next((pot.zone_id for pot in pots if pot.id == event.pot_id), ""),
                    json.dumps(event_to_dict(event), ensure_ascii=False),
                )
                for event in events
            ],
        )
        self._db.commit()
