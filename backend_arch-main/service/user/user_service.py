"""
UserService — сервис управления пользователями.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

## Бизнес-контекст
Реализует бизнес-логику get_or_create:
- Поиск по telegram_id
- Создание нового пользователя, если не найден

## Зависимости
- UserRepository: доступ к данным пользователей
"""

from sqlalchemy.ext.asyncio import AsyncSession

from model.user.user_model import UserModel
from repository.user.user_repository import UserRepository


class UserService:
    """Сервис пользователей с логикой get_or_create."""

    def __init__(self):
        self._repo = UserRepository()

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None,
        session: AsyncSession,
    ) -> tuple[UserModel, bool]:
        """
        Получить существующего или создать нового пользователя.

        ## Входные данные
        - telegram_id: ID пользователя в Telegram
        - username: username в Telegram (может быть None)
        - session: сессия БД

        ## Обработка
        1. Поиск пользователя по telegram_id
        2. Если найден — возврат (user, False)
        3. Если не найден — создание и возврат (user, True)

        ## Выходные данные
        - tuple[UserModel, bool]: (пользователь, is_new)
        """
        existing = await self._repo.get_by_telegram_id(telegram_id, session)
        if existing:
            return existing, False

        new_user = await self._repo.create(
            session,
            telegram_id=telegram_id,
            username=username,
        )
        return new_user, True
