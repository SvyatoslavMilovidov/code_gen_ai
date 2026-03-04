"""
Configs — конфигурация приложения.

## Бизнес-контекст
Централизованное хранение всех настроек приложения.
Загружает значения из переменных окружения с fallback на значения по умолчанию.

## Входные данные
- Переменные окружения (DB_HOST, DB_PORT, и т.д.)

## Обработка
- Загрузка через python-dotenv
- Приведение типов

## Выходные данные
- Singleton объект configs с типизированными настройками
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Configs:
    # Debug mode
    MODE_DEBUG: bool = os.getenv("MODE_DEBUG", "False") == "True"

    # Database
    DB_ENGINE: str = os.getenv("DB_ENGINE", "postgresql")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    @property
    def database_url(self) -> str:
        """URL для асинхронного подключения к БД."""
        return (
            f"{self.DB_ENGINE}+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        """URL для синхронного подключения (Alembic)."""
        return (
            f"{self.DB_ENGINE}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


configs = Configs()
