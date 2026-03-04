"""
DatabaseConnection — управление подключением к БД.

## Бизнес-контекст
Предоставляет асинхронные сессии для работы с БД.
Управляет пулом соединений.

## Выходные данные
- get_session: async generator для FastAPI Depends
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .config import configs


class DatabaseConnection:
    """Менеджер подключения к базе данных."""

    def __init__(self):
        self.engine = create_async_engine(
            configs.database_url,
            echo=configs.MODE_DEBUG,
            pool_pre_ping=True,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Получить сессию БД.

        ## Выходные данные
        - AsyncSession для работы с БД

        ## Обработка
        - Автоматический commit при успехе
        - Автоматический rollback при ошибке
        """
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
