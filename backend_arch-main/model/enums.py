"""
Enums — перечисления для всех моделей.

## Бизнес-контекст
Централизованное хранение всех статусов и типов,
используемых в моделях данных.
"""

from enum import Enum


class ExampleStatusEnum(str, Enum):
    """Пример статуса (замените на реальный)."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
