"""Тексти віджетів головної. Рахує лише показ: дати й відсотки вже є в картці горщика."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.contracts.labels import STAGE_LABELS, as_percent
from app.contracts.models import GrowthStage, Mood, PotCard
from app.shell.dates import duration_words

# Порядок у смузі і в списку вибору.
ORDER: tuple[str, ...] = (
    "next_water",
    "next_feed",
    "grow_left",
    "next_stage",
    "thirsty",
    "ripe",
    "health",
)

# title, підказка в списку вибору.
CATALOG: dict[str, tuple[str, str]] = {
    "next_water": ("До поливки", "Час до наступного поливу на екрані телефону"),
    "next_feed": ("До добрива", "Час до наступного добрива"),
    "grow_left": ("До стиглості", "Скільки лишилось рости"),
    "next_stage": ("До етапу", "Коли наступний етап росту"),
    "thirsty": ("Хочуть пити", "Скільки рослин хочуть води"),
    "ripe": ("Стиглих", "Скільки вже можна зібрати"),
    "health": ("Здоров'я", "Середнє здоров'я рослин"),
}

DEFAULT_IDS: tuple[str, ...] = ("next_water", "grow_left")

_DONE = {GrowthStage.RIPE, GrowthStage.HARVESTED}
_THIRST = {Mood.THIRSTY, Mood.SAD}


@dataclass(frozen=True)
class Fact:
    widget_id: str
    title: str
    value: str
    caption: str
    tone: str  # plain | warn | good


def normalize_ids(raw: object) -> tuple[str, ...]:
    """Лише відомі id, у порядку каталогу. Порожній список лишається порожнім."""
    if not isinstance(raw, (list, tuple)):
        return DEFAULT_IDS
    picked = {item for item in raw if isinstance(item, str)}
    return tuple(widget_id for widget_id in ORDER if widget_id in picked)


def build_facts(cards: tuple[PotCard, ...] | list[PotCard], now: datetime, selected: tuple[str, ...]) -> list[Fact]:
    ids = tuple(widget_id for widget_id in ORDER if widget_id in selected)
    return [_fact(widget_id, tuple(cards), now) for widget_id in ids]


_SKIP_CAPTION = {
    "Поки порожньо",
    "Немає дати",
    "Немає прогнозу",
    "Можна збирати",
    "Нових плодів немає",
    "Далі лише збір",
    "усі в нормі",
    "ще не стиглі",
    "можна збирати",
    "по всіх рослинах",
    "Немає даних",
}


def phone_line(fact: Fact) -> str:
    """Рядок домашнього екрана: «До поливки 1 година · Огірок»."""
    caption = fact.caption.strip()
    if not caption or caption in _SKIP_CAPTION:
        return fact.value
    return f"{fact.value} · {caption}"


def _fact(widget_id: str, cards: tuple[PotCard, ...], now: datetime) -> Fact:
    title = CATALOG[widget_id][0]
    if not cards:
        return Fact(widget_id, title, "Поки немає рослин", "Поки порожньо", "plain")
    if widget_id == "next_water":
        return _deadline(widget_id, title, cards, now, lambda card: card.plan.next_water_at)
    if widget_id == "next_feed":
        return _deadline(widget_id, title, cards, now, lambda card: card.plan.next_fertilize_at)
    if widget_id == "grow_left":
        return _grow(title, cards, now)
    if widget_id == "next_stage":
        return _stage(title, cards, now)
    if widget_id == "thirsty":
        return _thirsty(title, cards)
    if widget_id == "ripe":
        return _ripe(title, cards)
    return _health(title, cards)


def _deadline(widget_id: str, title: str, cards: tuple[PotCard, ...], now: datetime, pick) -> Fact:
    found = _soonest(cards, pick)
    prefix = "До поливки" if widget_id == "next_water" else "До добрива"
    if found is None:
        return Fact(widget_id, title, f"{prefix} немає дати", "Немає дати", "plain")
    card, moment = found
    return Fact(widget_id, title, _until(prefix, moment, now), _plant(card), _tone_for(moment, now))


def _grow(title: str, cards: tuple[PotCard, ...], now: datetime) -> Fact:
    growing = [card for card in cards if card.pot.stage not in _DONE]
    if not growing:
        ripe = any(card.pot.stage == GrowthStage.RIPE for card in cards)
        if ripe:
            return Fact("grow_left", title, "Вже стигле", "Можна збирати", "good")
        return Fact("grow_left", title, "Зібрано", "Нових плодів немає", "plain")
    found = _soonest(tuple(growing), _ripe_at)
    if found is None:
        return Fact("grow_left", title, "Скільки рости — немає прогнозу", "Немає прогнозу", "plain")
    card, moment = found
    hours = _hours(moment, now)
    if hours <= 0:
        text = "Вже стигле"
        tone = "good"
    elif hours < 1:
        text = "Рости лишилось менше години"
        tone = "plain"
    else:
        text = f"Рости ще {duration_words(hours)}"
        tone = "plain"
    return Fact("grow_left", title, text, _plant(card), tone)


def _stage(title: str, cards: tuple[PotCard, ...], now: datetime) -> Fact:
    found = _soonest(cards, _stage_at)
    if found is None:
        if cards and all(card.pot.stage in _DONE for card in cards):
            return Fact("next_stage", title, "Вже стигле", "Далі лише збір", "good")
        return Fact("next_stage", title, "До етапу немає прогнозу", "Немає прогнозу", "plain")
    card, moment = found
    forecast = card.forecast
    stage = STAGE_LABELS[forecast.next_stage] if forecast and forecast.next_stage else ""
    caption = _plant(card) if not stage else f"{_plant(card)} · {stage}"
    hours = _hours(moment, now)
    if hours <= 0:
        text = "Етап уже настав"
    elif hours < 1:
        text = "До етапу менше години"
    else:
        text = f"До етапу {duration_words(hours)}"
    return Fact("next_stage", title, text, caption, "plain")


def _thirsty(title: str, cards: tuple[PotCard, ...]) -> Fact:
    names = [_plant(card) for card in cards if card.pot.mood in _THIRST]
    if not names:
        return Fact("thirsty", title, "Ніхто не хоче пити", "усі в нормі", "plain")
    caption = ", ".join(names[:2]) if len(names) <= 2 else f"{len(names)} рослин"
    return Fact("thirsty", title, f"Хочуть пити: {len(names)}", caption, "warn")


def _ripe(title: str, cards: tuple[PotCard, ...]) -> Fact:
    names = [_plant(card) for card in cards if card.pot.stage == GrowthStage.RIPE]
    if not names:
        return Fact("ripe", title, "Ще нічого збирати", "ще не стиглі", "plain")
    caption = ", ".join(names[:2]) if len(names) <= 2 else "можна збирати"
    return Fact("ripe", title, f"Стиглих: {len(names)}", caption, "good")


def _health(title: str, cards: tuple[PotCard, ...]) -> Fact:
    average = sum(card.pot.health for card in cards) / len(cards)
    if average < 0.45:
        tone = "warn"
    elif average >= 0.75:
        tone = "good"
    else:
        tone = "plain"
    return Fact("health", title, f"Здоров'я {as_percent(average)}%", "по всіх рослинах", tone)


def _until(prefix: str, moment: datetime, now: datetime) -> str:
    hours = _hours(moment, now)
    if hours <= 0:
        return f"{prefix} вже пора" if abs(hours) >= 1 else f"{prefix} зараз"
    if hours < 1:
        return f"{prefix} менше години"
    return f"{prefix} {duration_words(hours)}"


def _tone_for(moment: datetime, now: datetime) -> str:
    return "warn" if _hours(moment, now) <= 0 else "plain"


def _hours(moment: datetime, now: datetime) -> float:
    return (_stamp(moment) - _stamp(now)) / 3600


def _ripe_at(card: PotCard) -> datetime | None:
    forecast = card.forecast
    if forecast is None:
        return None
    return forecast.ripe_at


def _stage_at(card: PotCard) -> datetime | None:
    forecast = card.forecast
    if forecast is None:
        return None
    return forecast.next_stage_at


def _soonest(cards: tuple[PotCard, ...], pick) -> tuple[PotCard, datetime] | None:
    best: tuple[PotCard, datetime] | None = None
    best_ts: float | None = None
    for card in cards:
        moment = pick(card)
        if moment is None:
            continue
        stamp = _stamp(moment)
        if best_ts is None or stamp < best_ts:
            best = (card, moment)
            best_ts = stamp
    return best


def _plant(card: PotCard) -> str:
    name = card.species.name
    variety = (card.species.variety or "").strip()
    if variety and variety.casefold() != "загальний":
        return f"{name} · {variety}"
    return name


def _stamp(value: datetime) -> float:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.timestamp()
