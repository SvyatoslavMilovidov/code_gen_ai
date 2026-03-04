"""
UserSchema — схемы валидации для пользователей.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

## Бизнес-контекст
Входные/выходные схемы для API управления пользователями.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    """Схема для создания/поиска пользователя."""
    telegram_id: int
    username: Optional[str] = None


class UserResponseSchema(BaseModel):
    """Схема ответа с данными пользователя."""
    id: int
    telegram_id: int
    username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserGetOrCreateResponseSchema(BaseModel):
    """Схема ответа get_or_create: пользователь + флаг is_new."""
    user: UserResponseSchema
    is_new: bool
