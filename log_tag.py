"""print() с префиксом города: при параллельной работе строки разных городов не перемешиваются без метки."""
import builtins
import contextvars

_city_tag = contextvars.ContextVar("city_tag", default="")


def set_city(city_name: str) -> None:
    """Задаёт префикс для текущей задачи (каждый город работает в своей asyncio-задаче)."""
    _city_tag.set(f"[{city_name}] " if city_name else "")


def print(*args, **kwargs):
    tag = _city_tag.get()
    if tag and args:
        args = (f"{tag}{args[0]}",) + tuple(args[1:])
    builtins.print(*args, **kwargs)
