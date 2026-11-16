"""Перевірка, що ядро імпортується. Запуск: python -m app.core.demo"""

from app.contracts.models import CareAction
from app.contracts.samples import PLANTED, sample_species, sample_zone_view
from app.core.growth import GrowthEngine


def main() -> None:
    engine = GrowthEngine()
    species = sample_species()[0]
    profile = sample_zone_view().cards[0].pot.profile
    marks = engine.timeline(profile, species)
    event = engine.make_event("pot-demo", CareAction.WATER, PLANTED)
    print(f"календар: {marks[0].label} з дня {marks[0].starts_on_day}")
    print(f"подія: {event.action.value} {event.id}")
    try:
        engine.advance(sample_zone_view().cards[0].pot, species, [], PLANTED)
    except NotImplementedError as exc:
        print(exc)


if __name__ == "__main__":
    main()
