"""
Schema — Pydantic схемы для валидации данных.

Экспортирует все схемы для удобного импорта:
    from schema import HealthCheckResponseSchema
"""

from .health.health_schema import HealthCheckResponseSchema
from .user.user_schema import UserCreateSchema, UserResponseSchema, UserGetOrCreateResponseSchema

__all__ = [
    "HealthCheckResponseSchema",
    "UserCreateSchema",
    "UserResponseSchema",
    "UserGetOrCreateResponseSchema",
]
