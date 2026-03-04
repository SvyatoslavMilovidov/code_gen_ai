"""
UserRepository — репозиторий для работы с пользователями.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

## Бизнес-контекст
Расширяет BaseRepository дополнительным методом поиска
по telegram_id (уникальный идентификатор Telegram).

## Зависимости
- BaseRepository: базовые CRUD операции
- UserModel: ORM модель пользователя
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.user.user_model import UserModel
from repository.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """Репозиторий пользователей с поиском по telegram_id."""

    def __init__(self):
        super().__init__(UserModel)

    async def get_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ) -> Optional[UserModel]:
        """
        Найти пользователя по Telegram ID.

        ## Входные данные
        - telegram_id: ID пользователя в Telegram
        - session: сессия БД

        ## Выходные данные
        - UserModel или None если не найден
        """
        result = await session.execute(
            select(self.model).where(self.model.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
