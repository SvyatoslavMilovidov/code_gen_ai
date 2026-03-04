"""
Service — бизнес-логика приложения.

Экспортирует все сервисы для удобного импорта:
    from service import HealthService
"""

from .health.health_service import HealthService
from .user.user_service import UserService

__all__ = [
    "HealthService",
    "UserService",
]
