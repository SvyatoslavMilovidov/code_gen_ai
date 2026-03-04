# Инструкция: работа с репозиторием бэкенд-сервиса

## Что это за репозиторий

Микросервис на FastAPI со слоистой архитектурой. Отвечает за бизнес-логику, работу с БД, внешние интеграции. Предоставляет REST API, которое вызывают Telegram-боты и другие клиенты.

---

## Архитектурное правило

```
Бэкенд-сервис = бизнес-логика + данные.
Клиенты (боты, web) вызывают его по HTTP API.
```

Один бэкенд-сервис может обслуживать несколько ботов/клиентов. Бэкенд **не знает** о Telegram, UI, виджетах — он работает только с данными и бизнес-правилами.

---

## Структура проекта

```
service/
├── main.py                        # Точка входа (uvicorn)
├── prd.json                       # PRD — источник фич и сценариев
├── alembic.ini                    # Миграции
├── requirements.txt
│
├── core/                          # Ядро
│   ├── config.py                  # Pydantic Settings (env)
│   ├── database.py                # AsyncSession, engine
│   ├── loader.py                  # FastAPI app
│   └── exceptions.py              # AppException, NotFoundError, ...
│
├── model/                         # ORM модели (SQLAlchemy)
│   ├── base_model.py
│   ├── enums.py
│   └── {group}/
│       └── {entity}_model.py
│
├── schema/                        # Pydantic схемы
│   └── {group}/
│       └── {entity}_schema.py     # Create, Update, Response, Filter
│
├── repository/                    # Слой доступа к данным (CRUD)
│   ├── base_repository.py
│   └── {group}/
│       └── {entity}_repository.py
│
├── service/                       # Бизнес-логика
│   └── {group}/
│       └── {entity}_service.py
│
├── api/                           # HTTP API
│   └── v1/
│       ├── include_router.py
│       ├── exception_handlers.py
│       └── endpoints/
│           └── {entity}/
│               ├── get.py
│               ├── post.py
│               ├── put.py
│               └── delete.py
│
├── migrations/                    # Alembic
│
├── tests/                         # Тесты по фичам и сценариям
│   └── {Feature ID}_{name}/
│       └── test_{Scenario ID}_{desc}.py
│
└── docs/                          # Документация архитектуры
```

---

## Слоистая архитектура

```
HTTP Request
    ↓
┌──────────┐
│   API    │  Валидация входа (Schema), маршрутизация
├──────────┤
│ Service  │  Бизнес-логика, оркестрация, правила
├──────────┤
│Repository│  CRUD-операции, SQL-запросы
├──────────┤
│  Model   │  ORM-модели, таблицы
├──────────┤
│  Core    │  Конфигурация, БД, исключения
└──────────┘
```

**Зависимости (строго сверху вниз):**
- API → Service, Schema
- Service → Repository, Schema, Model
- Repository → Model
- Model → Core
- Core → ничего

---

## Пошаговая инструкция: добавление фичи

### 1. Проверить PRD

Убедиться, что в `prd.json` есть:
- `feature_id` (например, `F001`)
- `acceptance_criteria` с BDD-сценариями (`SC001`, `SC002`, ...)
- `test_cases`

### 2. Создать модель (model/)

```python
# model/notes/note_model.py
"""
NoteModel — модель заметки.

## Трассируемость
Feature: F001 — Управление заметками
Scenarios: SC001, SC002, SC003, SC004, SC005
"""
from sqlalchemy import Column, String, Integer, ForeignKey
from model.base_model import Base, BaseModel

class NoteModel(Base, BaseModel):
    __tablename__ = "notes"
    user_id = Column(Integer, nullable=False, index=True)
    text = Column(String(5000), nullable=False)
```

- Создать миграцию: `alembic revision --autogenerate -m "Add notes table"`
- Применить: `alembic upgrade head`

### 3. Создать схемы (schema/)

```python
# schema/notes/note_schema.py
"""
## Трассируемость
Feature: F001
Scenarios: SC001, SC002, SC003
"""
from pydantic import BaseModel, Field

class NoteCreateSchema(BaseModel):
    user_id: int
    text: str = Field(..., min_length=1, max_length=5000)

class NoteResponseSchema(BaseModel):
    id: int
    user_id: int
    text: str
    created_at: str

    class Config:
        from_attributes = True
```

### 4. Создать репозиторий (repository/)

```python
# repository/notes/note_repository.py
"""
## Трассируемость
Feature: F001
Scenarios: SC001, SC003, SC004, SC005
"""
from model.notes.note_model import NoteModel
from repository.base_repository import BaseRepository

class NoteRepository(BaseRepository[NoteModel]):
    def __init__(self):
        super().__init__(NoteModel)
```

### 5. Создать сервис (service/)

```python
# service/notes/note_service.py
"""
NoteService — сервис управления заметками.

## Трассируемость
Feature: F001 — Управление заметками
Scenarios: SC001, SC002, SC003, SC004, SC005

## Бизнес-контекст
CRUD-операции с валидацией бизнес-правил.

## Зависимости
- NoteRepository: персистенция
"""
from repository.notes.note_repository import NoteRepository
from core.exceptions import ValidationError, NotFoundError

class NoteService:
    def __init__(self):
        self.repo = NoteRepository()

    async def create_note(self, user_id: int, text: str, session) -> NoteModel:
        if not text.strip():
            raise ValidationError("Заметка не может быть пустой")
        return await self.repo.create(session, user_id=user_id, text=text)

    async def get_notes(self, user_id: int, session) -> list:
        return await self.repo.get_all(session, user_id=user_id)

    async def delete_note(self, note_id: int, session) -> None:
        note = await self.repo.get_by_id(session, note_id)
        if not note:
            raise NotFoundError(f"Заметка {note_id} не найдена")
        await self.repo.delete(session, note_id)
```

### 6. Создать API эндпоинты (api/)

```python
# api/v1/endpoints/notes/post.py
"""
## Трассируемость
Feature: F001
Scenarios: SC001, SC002
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schema.notes.note_schema import NoteCreateSchema, NoteResponseSchema
from service.notes.note_service import NoteService
from core.database import get_session

router = APIRouter()

@router.post("", response_model=NoteResponseSchema, status_code=201)
async def create_note(
    data: NoteCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    service = NoteService()
    note = await service.create_note(data.user_id, data.text, session)
    return note
```

### 7. Подключить роутер

В `api/v1/include_router.py`:

```python
from .endpoints.notes import notes_router
app.include_router(notes_router, prefix="/api/v1/notes", tags=["notes"])
```

### 8. Создать тесты

```
tests/F001_notes/
    conftest.py
    test_SC001_create_note.py
    test_SC002_create_empty_note.py
    test_SC003_list_notes.py
    test_SC004_list_notes_empty.py
    test_SC005_delete_note.py
```

Каждый тест:
- Docstring с полным BDD из PRD
- Класс `Test{ScenarioID}{Name}`
- Структура Given / When / Then
- `@pytest.mark.parametrize` если есть `examples`

### 9. Проверки

```bash
alembic upgrade head          # Миграции
pytest -q                     # Тесты
uvicorn main:app --reload     # Запуск → проверить /docs
```

---

## Нейминг

| Слой | Файл | Класс |
|------|------|-------|
| Model | `{entity}_model.py` | `{Entity}Model` |
| Schema | `{entity}_schema.py` | `{Entity}CreateSchema`, `{Entity}ResponseSchema` |
| Repository | `{entity}_repository.py` | `{Entity}Repository` |
| Service | `{entity}_service.py` | `{Entity}Service` |
| API | `get.py`, `post.py`, `put.py`, `delete.py` | функции |

Группировка: `{layer}/{group}/{entity}_{layer}.py`

---

## Docstring — обязательная секция «Трассируемость»

Каждый модуль содержит в docstring:

```python
"""
## Трассируемость
Feature: F001 — Название
Scenarios: SC001, SC002
"""
```

Для инфраструктурных модулей (core, base):

```python
"""
## Трассируемость
Infrastructure — не привязан к конкретной фиче
"""
```

---

## Справочники

| Документ | Описание |
|----------|----------|
| [docs/README.md](docs/README.md) | Оглавление документации |
| [docs/01-overview.md](docs/01-overview.md) | Обзор архитектуры |
| [docs/02-project-structure.md](docs/02-project-structure.md) | Структура проекта |
| [docs/03-naming.md](docs/03-naming.md) | Правила нейминга |
| [docs/04-documentation.md](docs/04-documentation.md) | Правила docstring |
| [docs/05-dependencies.md](docs/05-dependencies.md) | Зависимости между слоями |
| [docs/06-imports.md](docs/06-imports.md) | Правила импортов |
| [docs/07-errors.md](docs/07-errors.md) | Обработка ошибок |
| [docs/08-api-versioning.md](docs/08-api-versioning.md) | Версионирование API |
| [docs/09-checklist.md](docs/09-checklist.md) | Чеклист создания модуля |
| [docs/10-example.md](docs/10-example.md) | Пример создания сущности |
| [docs/11-traceability.md](docs/11-traceability.md) | Трассируемость PRD → код |
| [docs/12-tests.md](docs/12-tests.md) | Конвенции тестирования |
