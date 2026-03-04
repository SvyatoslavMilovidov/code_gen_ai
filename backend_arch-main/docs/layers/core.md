# Слой core/

[← Назад к оглавлению](../README.md)

---

**Назначение:** Ядро приложения — конфигурация, подключение к БД, инициализация FastAPI.

## Структура

| Файл | Назначение |
|------|------------|
| `config.py` | Загрузка переменных окружения, настройки приложения |
| `database.py` | Подключение к БД, управление сессиями |
| `loader.py` | Создание экземпляра FastAPI, глобальные зависимости |
| `exceptions.py` | Базовые исключения приложения (опционально) |

## Пример config.py

```python
"""
Configs — конфигурация приложения.

## Бизнес-контекст
Централизованное хранение всех настроек приложения.
Загружает значения из переменных окружения с fallback на значения по умолчанию.

## Входные данные
- Переменные окружения (DATABASE_URL, API_KEY, и т.д.)

## Обработка
- Загрузка через python-dotenv
- Валидация обязательных параметров
- Приведение типов

## Выходные данные
- Singleton объект configs с типизированными настройками
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Configs:
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


configs = Configs()
```

## Пример loader.py

```python
"""
Loader — инициализация FastAPI приложения.

## Бизнес-контекст
Создаёт и настраивает экземпляр FastAPI с метаданными,
инициализирует подключение к БД и фоновые задачи.

## Выходные данные
- app: экземпляр FastAPI
- db_connect: менеджер подключения к БД
"""

from fastapi import FastAPI
from .database import DatabaseConnection

app = FastAPI(
    title="Service Name",
    description="Описание сервиса",
    version="1.0.0",
)

db_connect = DatabaseConnection()
```

## Пример database.py

```python
"""
DatabaseConnection — управление подключением к БД.

## Бизнес-контекст
Предоставляет асинхронные сессии для работы с БД.
Управляет пулом соединений.

## Выходные данные
- get_session: async generator для Depends
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import configs


class DatabaseConnection:
    def __init__(self):
        self.engine = create_async_engine(
            configs.database_url,
            echo=configs.DEBUG,
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def get_session(self) -> AsyncSession:
        """
        Получить сессию БД.
        
        ## Выходные данные
        - AsyncSession для работы с БД
        """
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
```

## Правила

1. **Никаких бизнес-зависимостей** — core не импортирует model, service, repository
2. **Singleton паттерн** — configs, db_connect создаются один раз
3. **Типизация** — все настройки имеют явные типы
4. **Значения по умолчанию** — для опциональных настроек

---

[Далее: Слой model/ →](model.md)
