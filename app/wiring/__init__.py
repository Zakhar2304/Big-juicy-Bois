"""Збірка фасаду. Єдина папка, якій можна імпортувати core, knowledge і storage разом."""

from app.wiring.actions import GardenActions

__all__ = ["GardenActions"]
