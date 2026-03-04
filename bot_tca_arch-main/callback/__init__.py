"""
Пакет callback - классы колбеков для Telegram.

Структура:
- callback/{tag}.py - колбеки для каждого тега

Для эхо-бота колбеки не требуются (нет inline-кнопок).
Структура готова для расширения.

Пример колбека:
```python
from aiogram.filters.callback_data import CallbackData

class SomeCallback(CallbackData, prefix="some_action"):
    field1: str
    field2: int
```
"""
