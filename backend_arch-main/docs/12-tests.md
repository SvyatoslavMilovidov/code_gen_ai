# Тестирование

[← Назад к оглавлению](README.md)

---

## Назначение

Тесты генерируются на основе BDD-сценариев из `prd.json`. Каждый сценарий = один тестовый модуль. Тесты являются доказательством реализации бизнес-требований.

---

## Структура тестов

```
tests/
├── conftest.py                                  # Глобальные фикстуры (db, client)
├── F001_notes/                                  # Feature ID + описание
│   ├── conftest.py                              # Фикстуры фичи
│   ├── test_SC001_create_note.py
│   ├── test_SC002_create_empty_note.py
│   ├── test_SC003_list_notes.py
│   ├── test_SC004_list_notes_empty.py
│   └── test_SC005_delete_note.py
├── F002_auth/
│   ├── conftest.py
│   └── test_SC001_login.py
└── ...
```

### Правила нейминга

| Элемент | Формат | Пример |
|---------|--------|--------|
| Директория фичи | `{Feature ID}_{snake_case_name}/` | `F001_notes/` |
| Тестовый модуль | `test_{Scenario ID}_{snake_case_desc}.py` | `test_SC001_create_note.py` |
| Класс тестов | `Test{ScenarioID}{PascalCaseDesc}` | `TestSC001CreateNote` |
| Метод теста | `test_{описание_проверки}` | `test_returns_201` |

---

## Формат тестового модуля

### Docstring — BDD-сценарий

```python
"""
Feature: F001 — Управление заметками
Scenario: SC001 — Пользователь создаёт текстовую заметку

Given: Пользователь авторизован
And: Пользователь на главном экране
When: Отправляет POST /api/v1/notes с текстом
Then: Заметка сохранена в БД, статус 201
And: Ответ содержит ID заметки
"""
```

### Структура тела — Given / When / Then

```python
import pytest
from httpx import AsyncClient


class TestSC001CreateNote:
    """Тесты для SC001 — создание текстовой заметки."""

    @pytest.fixture
    async def setup(self, db_session, auth_headers):
        """Given: Авторизованный пользователь."""
        return {"headers": auth_headers}

    async def test_returns_201(self, client: AsyncClient, setup):
        """POST /notes с текстом возвращает 201."""
        # When
        response = await client.post(
            "/api/v1/notes",
            json={"text": "Купить молоко"},
            headers=setup["headers"],
        )

        # Then
        assert response.status_code == 201
        assert "id" in response.json()

    async def test_note_persisted(self, client: AsyncClient, setup, db_session):
        """Заметка сохраняется в БД."""
        # When
        response = await client.post(
            "/api/v1/notes",
            json={"text": "Купить молоко"},
            headers=setup["headers"],
        )

        # Then
        note_id = response.json()["id"]
        note = await db_session.get(NoteModel, note_id)
        assert note is not None
        assert note.text == "Купить молоко"
```

---

## Генерация тестов из PRD

Из `prd.json` для каждого сценария берём:

| Поле PRD | Куда в тесте |
|----------|-------------|
| `acceptance_criteria[].scenario_id` | Имя файла: `test_{scenario_id}_...` |
| `acceptance_criteria[].user_story` | Docstring теста |
| `acceptance_criteria[].bdd.given` | Фикстура `setup` / секция Given |
| `acceptance_criteria[].bdd.and_preconditions` | Дополнительная настройка в Given |
| `acceptance_criteria[].bdd.when` | HTTP-запрос или вызов сервиса |
| `acceptance_criteria[].bdd.then` | Assert на response / БД |
| `acceptance_criteria[].bdd.and_postconditions` | Дополнительные assert |
| `test_cases[].examples` | `@pytest.mark.parametrize` |

### Пример с parametrize

```python
"""
Feature: F001 — Управление заметками
Scenario: SC002 — Пустая заметка отклоняется

Given: Пользователь авторизован
When: Отправляет POST /api/v1/notes с пустым текстом
Then: Статус 422, ошибка валидации
"""
import pytest


class TestSC002CreateEmptyNote:

    @pytest.mark.parametrize("text,expected_status", [
        ("", 422),
        ("   ", 422),
    ])
    async def test_empty_note_rejected(self, client, auth_headers, text, expected_status):
        # When
        response = await client.post(
            "/api/v1/notes",
            json={"text": text},
            headers=auth_headers,
        )

        # Then
        assert response.status_code == expected_status
```

---

## Глобальные фикстуры (conftest.py)

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.database import DatabaseConnection
from api import app


@pytest.fixture
async def db_session():
    """Сессия БД для тестов (с rollback)."""
    ...

@pytest.fixture
async def client():
    """HTTP-клиент для тестов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(db_session):
    """Заголовки авторизованного пользователя."""
    ...
```

---

## Чек-лист тестирования

### Для каждого сценария из PRD:

- [ ] Создать директорию `tests/{Feature ID}_{name}/` (если не существует)
- [ ] Создать `conftest.py` с фикстурами фичи (если не существует)
- [ ] Создать файл `test_{Scenario ID}_{name}.py`
- [ ] В docstring — Feature, Scenario и полный BDD
- [ ] Класс `Test{ScenarioID}{Name}`
- [ ] Тесты по структуре Given / When / Then
- [ ] Если есть `examples` в PRD — `@pytest.mark.parametrize`
- [ ] Assert покрывает `then` и `and_postconditions`

### Проверка покрытия:

- [ ] Для каждого `acceptance_criteria` в PRD существует тест
- [ ] Каждый тестовый файл ссылается на существующий Scenario ID
- [ ] Нет тестов-сирот (без привязки к сценарию)
- [ ] Все тесты проходят: `pytest -q`

---

[← Назад к оглавлению](README.md)
