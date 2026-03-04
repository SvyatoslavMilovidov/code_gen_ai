# Инструкция для AI-агента: генерация кода по архитектуре

Ты — AI-агент, который генерирует код для двух типов проектов:
- **Telegram-бот** (aiogram 3, виджетная архитектура)
- **Бэкенд-сервис** (FastAPI, слоистая архитектура)

Следуй этой инструкции при получении запроса на фичу.

---

## 1. Архитектурный принцип

```
┌─────────────────┐       HTTP / REST        ┌─────────────────────┐
│  Telegram Bot    │ ──────────────────────→  │  Backend Service     │
│                  │                          │                      │
│  UI-слой:        │  ← JSON responses ────   │  Данные + логика:    │
│  виджеты         │  → HTTP requests ─────→  │  model → repo →      │
│  Trigger/Code/   │                          │  service → API       │
│  Answer          │                          │                      │
│  service/ =      │                          │  БД, ML, внешние     │
│  API-клиенты     │                          │  интеграции          │
└─────────────────┘                          └─────────────────────┘
```

**Бот НЕ подключается к БД.** Если фиче нужны данные — создаётся бэкенд-сервис, бот обращается к нему по API.

---

## 2. PRD — источник правды

В корне каждого проекта лежит `prd.json`. Формат:

```json
{
  "product_name": "string",
  "product_overview": "string",
  "features": [
    {
      "feature_id": "F001",
      "general_info": { "name": "string", "overview": "string" },
      "goal_and_context": { "business_goal": "string", "user_problem": "string" },
      "actors_and_roles": {
        "primary_user": "string",
        "secondary_user": "string | null",
        "system_service": "string | null"
      },
      "business_rules": [
        { "rule_id": "BR001", "description": "string" }
      ],
      "acceptance_criteria": [
        {
          "scenario_id": "SC001",
          "user_story": "string",
          "bdd": {
            "given": "string",
            "and_preconditions": ["string"],
            "when": "string",
            "then": "string",
            "and_postconditions": ["string"]
          }
        }
      ],
      "non_functional_requirements": [
        { "nfr_id": "NFR001", "type": "string", "description": "string" }
      ],
      "test_cases": [
        {
          "test_id": "T001",
          "scenario_id": "SC001",
          "setup": "string",
          "action": "string",
          "assertion": "string",
          "examples": [ { "input": {}, "expected": {} } ]
        }
      ]
    }
  ]
}
```

**Канонические ID:**
- Feature: `F001`, `F002`, ...
- Scenario: `SC001`, `SC002`, ...
- Business rule: `BR001`, ...
- Test case: `T001`, ...

---

## 3. Процесс: от запроса до кода

```
1. PRD → 2. Определить проекты → 3. Gap-анализ → 4. Задачи → 5. Реализация → 6. Тесты
```

### Шаг 1. Проверить / создать PRD

Убедиться, что в `prd.json` есть feature с:
- `feature_id`
- `acceptance_criteria` с BDD-сценариями
- `test_cases` с привязкой к сценариям

Если PRD неполный — дополнить.

### Шаг 2. Определить затронутые проекты

| Вопрос | Результат |
|--------|-----------|
| Есть UI в Telegram? | → Бот |
| Нужна БД / сохранение данных? | → Бэкенд-сервис |
| Нужен ML / тяжёлые вычисления? | → Бэкенд-сервис |
| Только UI без данных? | → Только бот |

### Шаг 3. Gap-анализ

Для каждого сценария определить, что уже есть (`✓`), что нужно создать (`?`), что расширить (`~`):

| Сценарий | Бэкенд: Model | Service | API | Бот: API-клиент | Виджет | Тест (бэк) | Тест (бот) |
|----------|---------------|---------|-----|-----------------|--------|-------------|------------|
| SC001    | ?             | ?       | ?   | ?               | ?      | ?           | ?          |

### Шаг 4. Задачи и порядок

**Бэкенд создаётся первым** (бот зависит от его API).

```
БЭКЕНД:                                  БОТ (после бэкенда):
1. Model + миграция                      5. API-клиент в service/
2. Schema                                6. Ноды: Trigger, Code, Answer
3. Repository                            7. Виджет в handler/{tag}/{Feature ID}/
4. Service + API endpoints               8. Состояния, колбеки (если нужны)
   + Тесты бэкенда                       9. Тесты бота
```

### Шаг 5. Реализация

См. разделы 4 (бэкенд) и 5 (бот) ниже.

### Шаг 6. Тесты

См. раздел 6 ниже.

---

## 4. Архитектура бэкенда (FastAPI)

### Структура проекта

```
service/
├── main.py                     # uvicorn точка входа
├── prd.json
├── alembic.ini
├── requirements.txt
│
├── core/
│   ├── config.py               # Настройки из env
│   ├── database.py             # AsyncSession, engine
│   ├── loader.py               # FastAPI app
│   └── exceptions.py           # AppException, NotFoundError, ...
│
├── model/
│   ├── base_model.py           # Base, BaseModel (id, created_at, updated_at)
│   ├── enums.py
│   └── {group}/
│       └── {entity}_model.py   # ORM-модель
│
├── schema/
│   └── {group}/
│       └── {entity}_schema.py  # Pydantic: Create, Response, Filter
│
├── repository/
│   ├── base_repository.py      # Generic CRUD: get_by_id, get_all, create, delete
│   └── {group}/
│       └── {entity}_repository.py
│
├── service/
│   └── {group}/
│       └── {entity}_service.py # Бизнес-логика
│
├── api/
│   └── v1/
│       ├── include_router.py   # Подключение роутеров
│       ├── exception_handlers.py
│       └── endpoints/
│           └── {entity}/
│               ├── __init__.py # APIRouter с prefix и tags
│               ├── get.py
│               ├── post.py
│               └── delete.py
│
├── migrations/
│
└── tests/
    └── {Feature ID}_{name}/
        ├── conftest.py
        └── test_{Scenario ID}_{desc}.py
```

### Слои (строго сверху вниз)

```
API → Service, Schema
Service → Repository, Schema, Model
Repository → Model
Model → Core
Core → ничего
```

### Пошаговое добавление сущности

**1. Model:**
```python
# model/notes/note_model.py
"""
NoteModel — модель заметки.

## Трассируемость
Feature: F001 — Управление заметками
Scenarios: SC001, SC002, SC003
"""
from sqlalchemy import Column, String, Integer
from model.base_model import Base, BaseModel

class NoteModel(Base, BaseModel):
    __tablename__ = "notes"
    user_id = Column(Integer, nullable=False, index=True)
    text = Column(String(5000), nullable=False)
```

Миграция: `alembic revision --autogenerate -m "Add notes"` → `alembic upgrade head`

**2. Schema:**
```python
# schema/notes/note_schema.py
"""
## Трассируемость
Feature: F001
Scenarios: SC001, SC002
"""
from pydantic import BaseModel, Field

class NoteCreateSchema(BaseModel):
    user_id: int
    text: str = Field(..., min_length=1, max_length=5000)

class NoteResponseSchema(BaseModel):
    id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**3. Repository:**
```python
# repository/notes/note_repository.py
"""
## Трассируемость
Feature: F001
Scenarios: SC001, SC003
"""
from model.notes.note_model import NoteModel
from repository.base_repository import BaseRepository

class NoteRepository(BaseRepository[NoteModel]):
    def __init__(self):
        super().__init__(NoteModel)

    # Дополнительные методы (кроме базовых CRUD):
    async def get_by_user_id(self, user_id: int, session) -> list[NoteModel]:
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return list(result.scalars().all())
```

**4. Service:**
```python
# service/notes/note_service.py
"""
NoteService — сервис управления заметками.

## Трассируемость
Feature: F001
Scenarios: SC001, SC002, SC003

## Зависимости
- NoteRepository
"""
from repository.notes.note_repository import NoteRepository
from core.exceptions import ValidationError

class NoteService:
    def __init__(self):
        self._repo = NoteRepository()

    async def create_note(self, user_id, text, session):
        if not text.strip():
            raise ValidationError("Заметка не может быть пустой")
        return await self._repo.create(session, user_id=user_id, text=text)
```

**5. API endpoint:**
```python
# api/v1/endpoints/notes/post.py
"""
## Трассируемость
Feature: F001
Scenarios: SC001, SC002
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import db_connect
from schema.notes.note_schema import NoteCreateSchema, NoteResponseSchema
from service.notes.note_service import NoteService

router = APIRouter()
service = NoteService()

@router.post("", response_model=NoteResponseSchema, status_code=201)
async def create_note(
    data: NoteCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
):
    return await service.create_note(data.user_id, data.text, session)
```

**6. Подключить роутер** в `api/v1/endpoints/__init__.py` и `api/v1/include_router.py`:
```python
from .endpoints import notes_router
app.include_router(notes_router, prefix=API_V1_PREFIX)
```

**7. Экспорты** — добавить в `__init__.py` каждого слоя (`model/`, `schema/`, `repository/`, `service/`).

### Нейминг (бэкенд)

| Слой | Файл | Класс |
|------|------|-------|
| Model | `{entity}_model.py` | `{Entity}Model` |
| Schema | `{entity}_schema.py` | `{Entity}CreateSchema`, `{Entity}ResponseSchema` |
| Repository | `{entity}_repository.py` | `{Entity}Repository` |
| Service | `{entity}_service.py` | `{Entity}Service` |
| API | `get.py`, `post.py`, `put.py`, `delete.py` | функции |

---

## 5. Архитектура бота (aiogram 3)

### Архитектурное правило

**Бот = UI-слой.** Не содержит БД, ORM, миграций, тяжёлых вычислений. Всё через HTTP-вызовы бэкенд-сервисов.

### Структура проекта

```
bot/
├── app.py                          # Точка входа
├── prd.json
├── requirements.txt
├── example.env
│
├── core/
│   ├── config.py                   # BOT_TOKEN, BACKEND_URL, ...
│   ├── loader.py                   # Bot, Dispatcher
│   └── vocab.py                    # Тексты, команды, кнопки
│
├── node/                           # UI-компоненты (LEGO-кирпичики)
│   └── {tag}/
│       ├── trigger/
│       │   └── {action}_trigger.py # Визуальные операции на входе
│       ├── code/
│       │   └── {action}_code.py    # Логика + вызов service/ + выбор Answer
│       └── answer/
│           └── {state}_answer.py   # Отрисовка экрана
│
├── handler/                        # Виджеты-оркестраторы
│   ├── include_router.py
│   └── v1/user/
│       ├── router.py               # Роутеры по тегам
│       └── {tag}/
│           └── {Feature ID}/       # ← Группировка по фичам
│               └── {name}_widget.py
│
├── service/                        # API-клиенты к бэкенд-сервисам
│   └── api/
│       └── {name}_api.py           # HTTP-методы (httpx)
│
├── callback/                       # Классы колбеков по тегам
├── state/                          # Состояния FSM по тегам
├── data/                           # Медиа и буферы
│
└── tests/
    └── {Feature ID}_{name}/
        ├── conftest.py
        └── test_{Scenario ID}_{desc}.py
```

### Виджетная архитектура: Trigger → Code → Answer

Каждое действие пользователя обрабатывается тремя компонентами:

**Trigger** — визуальные операции на входе:
- Удаление старых сообщений
- Сброс/установка FSM-состояний
- Извлечение данных из события
- Возвращает `dict` с данными для Code

**Code** — логика и роутинг:
- Вызывает API-клиенты из `service/`
- Применяет бизнес-правила
- Выбирает Answer (`answer_name`)
- Возвращает `{"answer_name": str, "data": dict}`

**Answer** — отрисовка UI:
- Формирует текст и клавиатуру
- Отправляет сообщение пользователю
- Никакой логики, только отображение

**Виджет** — оркестратор, который связывает Trigger → Code → Answer:
```python
# handler/v1/user/{tag}/{Feature ID}/{name}_widget.py
"""
Виджет: Создание заметки.

## Трассируемость
Feature: F001 — Управление заметками
Scenarios: SC001, SC002

SC001 — текст → создана → answer: note_created
SC002 — пустой текст → answer: note_empty_error
"""
ANSWER_REGISTRY = {
    "note_created": NoteCreatedAnswer(),
    "note_empty_error": NoteEmptyErrorAnswer(),
}

@notes_router.message(...)
async def handle_create_note(message: Message, state: FSMContext):
    trigger = CreateNoteTrigger()
    trigger_data = await trigger.run(message, state)

    code = CreateNoteCode()
    code_result = await code.run(trigger_data, state)

    answer = ANSWER_REGISTRY[code_result["answer_name"]]
    await answer.run(event=message, user_lang="ru", data=code_result["data"])
```

### API-клиент (service/)

```python
# service/api/notes_api.py
"""
HTTP-клиент к бэкенду заметок.

## Трассируемость
Feature: F001
Scenarios: SC001, SC003
"""
import httpx
from core.config import config

class NotesAPI:
    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or config.BACKEND_URL

    async def create_note(self, user_id: int, text: str) -> dict:
        async with httpx.AsyncClient(base_url=self._base_url) as client:
            resp = await client.post("/api/v1/notes", json={"user_id": user_id, "text": text})
            resp.raise_for_status()
            return resp.json()
```

### Нейминг (бот)

| Компонент | Файл | Класс |
|-----------|------|-------|
| Trigger | `{action}_trigger.py` | `{Action}Trigger` |
| Code | `{action}_code.py` | `{Action}Code` |
| Answer | `{state}_answer.py` | `{State}Answer` |
| Виджет | `{name}_widget.py` | функция `handle_{name}` |
| API-клиент | `{name}_api.py` | `{Name}API` |

**Feature ID в нейминге директорий** — только для виджетов: `handler/v1/user/{tag}/{Feature ID}/`.
В остальных модулях — Feature ID и Scenario ID только в docstrings.

---

## 6. Тесты

### Структура (одинаковая для бота и бэкенда)

```
tests/
├── conftest.py                          # Глобальные фикстуры
└── {Feature ID}_{name}/                 # Например: F001_base_commands/
    ├── __init__.py
    ├── conftest.py                      # Фикстуры фичи
    ├── test_{Scenario ID}_{desc}.py     # Например: test_SC001_new_user.py
    └── test_{Scenario ID}_{desc}.py
```

### Формат тестового файла

```python
"""
Тест SC001 — Описание сценария.

## Трассируемость
Feature: F001 — Название фичи
Scenario: SC001 — Описание сценария

## BDD
Given: Предусловие
When:  Действие
Then:  Ожидаемый результат
"""
import pytest

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_data, expected",
    [...],                    # Из prd.json → test_cases → examples
    ids=[...],
)
async def test_scenario_name(client, input_data, expected):
    """
    Given: ...
    When: ...
    Then: ...
    """
    # Given
    ...
    # When
    response = await client.post("/api/v1/...", json=input_data)
    # Then
    assert response.status_code == expected["status"]
```

### Бэкенд: conftest.py (PostgreSQL)

```python
import os
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from model.base_model import Base
from core import app, db_connect

def _test_db_url() -> str:
    host = os.getenv("TEST_DB_HOST", os.getenv("DB_HOST", "localhost"))
    port = os.getenv("TEST_DB_PORT", os.getenv("DB_PORT", "5432"))
    user = os.getenv("TEST_DB_USER", os.getenv("DB_USER", "postgres"))
    password = os.getenv("TEST_DB_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))
    name = os.getenv("TEST_DB_NAME", os.getenv("DB_NAME", "test_db"))
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(_test_db_url(), echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with sm() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(async_session):
    async def override():
        yield async_session
    app.dependency_overrides[db_connect.get_session] = override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

### Бот: conftest.py (моки)

```python
from unittest.mock import AsyncMock, MagicMock
import pytest

@pytest.fixture
def mock_message():
    msg = AsyncMock()
    msg.from_user = MagicMock(id=123, username="testuser")
    msg.text = "Hello"
    msg.answer = AsyncMock()
    return msg

@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.set_data = AsyncMock()
    state.clear = AsyncMock()
    return state
```

### Что тестируется где

| Что проверяем | Где | Как |
|---------------|-----|-----|
| Данные в БД | Бэкенд | HTTP → assert БД |
| Статус API | Бэкенд | HTTP → assert response |
| Бот показывает экран | Бот | mock message → assert answer |
| Бот вызывает API | Бот | mock API-клиент → assert call |

---

## 7. Трассируемость

### Docstring — обязательная секция

Каждый модуль (и бота, и бэкенда) содержит:

```python
"""
НазваниеМодуля — описание.

## Трассируемость
Feature: F001 — Название фичи
Scenarios: SC001, SC002

## Бизнес-контекст
...
"""
```

### Где что указывается

| Артефакт | Feature ID в нейминге | Feature/Scenario в docstring |
|----------|----------------------|------------------------------|
| Виджет (handler/) | ✓ Директория `{Feature ID}/` | ✓ |
| Нода (node/) | ✗ | ✓ |
| API-клиент (service/) | ✗ | ✓ |
| Model, Schema, Repo, Service | ✗ | ✓ |
| API endpoint | ✗ | ✓ |
| Тест | ✓ Директория `{Feature ID}_{name}/`, файл `test_{Scenario ID}_...` | ✓ |

---

## 8. Чек-лист перед завершением

- [ ] PRD (`prd.json`) актуален и содержит все сценарии
- [ ] Каждый модуль содержит `## Трассируемость` в docstring
- [ ] Виджеты лежат в `handler/.../{Feature ID}/`
- [ ] Тесты в `tests/{Feature ID}_{name}/test_{Scenario ID}_{desc}.py`
- [ ] Каждый сценарий из PRD покрыт тестом
- [ ] Экспорты добавлены в `__init__.py` всех слоёв
- [ ] Роутеры подключены в `include_router.py`
- [ ] Бот не содержит прямого доступа к БД
- [ ] `pytest -q` проходит
