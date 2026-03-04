# Service Template

Шаблон для быстрого создания новых микросервисов на FastAPI.

## Быстрый старт

### 1. Скопировать шаблон

```bash
cp -r service_template my_new_service
cd my_new_service
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
# Отредактировать .env
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустить

```bash
python main.py
```

Сервис будет доступен на http://localhost:8000

### 5. Проверить

```bash
curl http://localhost:8000/health
```

## Структура проекта

```
service_template/
├── main.py                    # Точка входа
├── requirements.txt           # Зависимости
│
├── core/                     # Ядро приложения
│   ├── __init__.py
│   ├── config.py            # Конфигурация
│   ├── database.py          # Подключение к БД
│   ├── loader.py            # Инициализация FastAPI
│   └── exceptions.py        # Базовые исключения
│
├── model/                    # ORM модели
│   ├── __init__.py
│   ├── base_model.py
│   └── enums.py
│
├── schema/                   # Pydantic схемы
│   ├── __init__.py
│   └── health/
│       └── health_schema.py
│
├── repository/               # Слой доступа к данным
│   ├── __init__.py
│   └── base_repository.py
│
├── service/                  # Бизнес-логика
│   ├── __init__.py
│   └── health/
│       └── health_service.py
│
└── api/                      # HTTP API
    ├── __init__.py
    └── v1/
        ├── include_router.py
        ├── exception_handlers.py
        └── endpoints/
            └── health/
                ├── __init__.py
                └── get.py
```

## Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/health` | Полная проверка состояния |
| GET | `/health/live` | Liveness probe (k8s) |
| GET | `/health/ready` | Readiness probe (k8s) |

## Добавление новой сущности

### 1. Создать модель

```python
# model/example/example_model.py

from sqlalchemy import Column, String
from model.base_model import Base, BaseModel

class ExampleModel(Base, BaseModel):
    __tablename__ = "examples"
    name = Column(String(255), nullable=False)
```

### 2. Создать схему

```python
# schema/example/example_schema.py

from pydantic import BaseModel

class ExampleCreateSchema(BaseModel):
    name: str

class ExampleResponseSchema(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

### 3. Создать репозиторий

```python
# repository/example/example_repository.py

from model import ExampleModel
from repository.base_repository import BaseRepository

class ExampleRepository(BaseRepository[ExampleModel]):
    def __init__(self):
        super().__init__(ExampleModel)
```

### 4. Создать сервис

```python
# service/example/example_service.py

from repository import ExampleRepository

class ExampleService:
    def __init__(self):
        self.repo = ExampleRepository()
```

### 5. Создать endpoint

```python
# api/v1/endpoints/example/get.py

from fastapi import APIRouter
router = APIRouter()

@router.get("")
async def get_examples():
    ...
```

### 6. Подключить роутер

```python
# api/v1/include_router.py

from .endpoints import example_router
app.include_router(example_router, prefix="/api/v1")
```

## Конфигурация

Переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `MODE_DEBUG` | Режим отладки | `False` |
| `DB_ENGINE` | Тип БД | `postgresql` |
| `DB_HOST` | Хост БД | `localhost` |
| `DB_PORT` | Порт БД | `5432` |
| `DB_NAME` | Имя БД | — |
| `DB_USER` | Пользователь БД | — |
| `DB_PASSWORD` | Пароль БД | — |

## Документация архитектуры

Подробная документация по архитектуре: [docs/](docs/README.md)
