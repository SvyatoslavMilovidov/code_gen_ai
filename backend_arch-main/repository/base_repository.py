"""
BaseRepository — базовый класс репозитория.

## Бизнес-контекст
Предоставляет стандартные CRUD операции для всех репозиториев.
Использует Generic для типизации модели.

## Методы
- get_by_id: получение по ID
- get_all: получение списка с пагинацией
- create: создание записи
- delete: удаление записи
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD операциями."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(
        self,
        id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """
        Получить запись по ID.

        ## Входные данные
        - id: идентификатор записи
        - session: сессия БД

        ## Выходные данные
        - Модель или None если не найдена
        """
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ModelType]:
        """
        Получить список записей с пагинацией.

        ## Входные данные
        - session: сессия БД
        - limit: максимум записей (по умолчанию 50)
        - offset: смещение (по умолчанию 0)

        ## Выходные данные
        - Список моделей
        """
        result = await session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(
        self,
        session: AsyncSession,
        **kwargs,
    ) -> ModelType:
        """
        Создать новую запись.

        ## Входные данные
        - session: сессия БД
        - **kwargs: поля модели

        ## Обработка
        1. Создание экземпляра модели
        2. Добавление в сессию
        3. Flush для получения ID
        4. Refresh для актуальных данных

        ## Выходные данные
        - Созданная модель с ID
        """
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def delete(
        self,
        id: int,
        session: AsyncSession,
    ) -> bool:
        """
        Удалить запись по ID.

        ## Входные данные
        - id: идентификатор записи
        - session: сессия БД

        ## Выходные данные
        - True если удалено, False если не найдено
        """
        result = await session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0
