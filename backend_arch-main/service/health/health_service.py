"""
HealthService — сервис проверки состояния приложения.

## Бизнес-контекст
Проверяет работоспособность сервиса и его зависимостей:
- Подключение к базе данных
- Доступность внешних сервисов (при необходимости)

## Зависимости
- DatabaseConnection: проверка подключения к БД
"""

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from schema import HealthCheckResponseSchema
from core.loader import VERSION


class HealthService:
    """Сервис проверки здоровья приложения."""

    async def check_health(
        self,
        session: AsyncSession,
    ) -> HealthCheckResponseSchema:
        """
        Проверить состояние сервиса.

        ## Входные данные
        - session: сессия БД

        ## Обработка
        1. Проверка подключения к БД (SELECT 1)
        2. Формирование ответа со статусом

        ## Выходные данные
        - HealthCheckResponseSchema с информацией о состоянии
        """
        db_status = "connected"
        error = None
        status = "healthy"

        # Проверяем подключение к БД
        try:
            await session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = "disconnected"
            error = str(e)
            status = "unhealthy"

        return HealthCheckResponseSchema(
            status=status,
            version=VERSION,
            timestamp=datetime.utcnow(),
            database=db_status,
            error=error,
        )
