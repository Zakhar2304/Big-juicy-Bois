import flet as ft

__all__ = ["PhoneWidget"]


@ft.control("PhoneWidget")
class PhoneWidget(ft.Service):
    """Пише рядки у віджет на домашньому екрані iPhone або Android."""

    async def publish(self, lines: list[str]) -> bool:
        return await self._invoke_method("publish", {"lines": list(lines)})
