# ⚙️ Пакет `service`

## 📋 Оглавление
1. [Описание пакета](#описание-пакета)
2. [Архитектурный принцип](#архитектурный-принцип)
3. [Внутренняя архитектура](#внутренняя-архитектура)
4. [Чек-лист добавления элементов](#чек-лист-добавления-элементов)

---

## Описание пакета

### 🎯 Назначение
Пакет `service` содержит **API-клиенты** для взаимодействия с внешними сервисами. Бот **не подключается к БД и не содержит бизнес-логики работы с данными напрямую**. Вся работа с данными происходит через вызовы API бэкенд-сервисов.

### 🏗️ Принципы организации
- **Разделение по бэкенд-сервисам:** каждый бэкенд-сервис = отдельный пакет в `service/`
- **Единая ответственность:** один сервис-клиент = один бэкенд-сервис
- **Абстракция:** Code-компоненты в `node/` вызывают методы сервисов, не зная деталей HTTP-запросов

---

## Архитектурный принцип

### Бот не владеет данными

```
┌─────────────────┐         HTTP/REST          ┌─────────────────────┐
│   Telegram Bot   │ ────────────────────────→ │  Backend Service     │
│   (bot_tca_arch) │                           │  (backend_arch)      │
│                  │  service/ = API-клиенты    │                      │
│  node/           │                           │  model/              │
│  handler/        │  ← JSON responses ──────  │  repository/         │
│  service/ ───────│─→ HTTP requests ────────→ │  service/            │
│                  │                           │  api/                │
└─────────────────┘                           └─────────────────────┘
```

**Что делает бот:**
- Принимает события от Telegram (сообщения, колбеки)
- Оркестрирует UI: Trigger → Code → Answer
- Вызывает бэкенд-сервисы через `service/` (HTTP-запросы)
- Отрисовывает ответы пользователю

**Что НЕ делает бот:**
- ❌ Подключение к БД
- ❌ ORM-модели, миграции
- ❌ CRUD-операции с данными
- ❌ Тяжёлые вычисления (ML, транскрипция, и т.д.)

**Если фиче нужна БД** — создаётся отдельный бэкенд-сервис по `backend_arch`, и бот обращается к нему через `service/`.

---

## Внутренняя архитектура

### 📂 Структура пакета

```
service/
├── __init__.py                  # Экспорт клиентов
├── base_client.py               # Базовый HTTP-клиент (общая логика)
├── notes_api/                   # Клиент к сервису заметок
│   ├── __init__.py
│   ├── notes_client.py          # HTTP-методы: create, list, delete
│   └── schemas.py               # Pydantic-схемы запросов/ответов
├── auth_api/                    # Клиент к сервису авторизации
│   ├── __init__.py
│   ├── auth_client.py
│   └── schemas.py
└── payment_api/                 # Клиент к платёжному сервису
    ├── __init__.py
    ├── payment_client.py
    └── schemas.py
```

### 🔧 Базовый HTTP-клиент

```python
"""
Базовый HTTP-клиент для вызовов бэкенд-сервисов.

## Трассируемость
Infrastructure — не привязан к конкретной фиче
"""
import aiohttp
from core.config import settings


class BaseAPIClient:
    """Базовый клиент для HTTP-запросов к бэкенд-сервисам."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{path}"
            async with session.request(method, url, **kwargs) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _get(self, path: str, **kwargs) -> dict:
        return await self._request("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs) -> dict:
        return await self._request("POST", path, **kwargs)

    async def _delete(self, path: str, **kwargs) -> dict:
        return await self._request("DELETE", path, **kwargs)
```

### 📝 Пример API-клиента: service/notes_api/notes_client.py

```python
"""
API-клиент к сервису заметок.

Feature: F001 — Управление заметками
Scenarios: SC001, SC002, SC003, SC004, SC005

Методы:
- create_note() — SC001, SC002
- get_notes() — SC003, SC004
- delete_note() — SC005
"""
from service.base_client import BaseAPIClient
from core.config import settings


class NotesClient(BaseAPIClient):
    """Клиент для взаимодействия с Notes API."""

    def __init__(self):
        super().__init__(base_url=settings.NOTES_SERVICE_URL)

    async def create_note(self, user_id: int, text: str) -> dict:
        """
        Создать заметку.

        Args:
            user_id: ID пользователя
            text: Текст заметки

        Returns:
            dict: {"id": int, "text": str, "created_at": str}

        Raises:
            aiohttp.ClientResponseError: 422 — валидация не пройдена
        """
        return await self._post(
            "/api/v1/notes",
            json={"user_id": user_id, "text": text},
        )

    async def get_notes(self, user_id: int) -> list[dict]:
        """
        Получить список заметок пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list[dict]: Список заметок
        """
        return await self._get(
            "/api/v1/notes",
            params={"user_id": user_id},
        )

    async def delete_note(self, note_id: int) -> dict:
        """
        Удалить заметку.

        Args:
            note_id: ID заметки

        Returns:
            dict: {"status": "deleted"}
        """
        return await self._delete(f"/api/v1/notes/{note_id}")
```

### 🔗 Использование в Code-компоненте

```python
"""
Code для создания заметки.

Feature: F001
Scenarios: SC001, SC002
"""
from service.notes_api.notes_client import NotesClient


class CreateNoteCode:

    def __init__(self):
        self.notes_client = NotesClient()

    async def _execute_business_logic(self, trigger_data, state, **kwargs):
        text = trigger_data.get("text", "").strip()

        if not text:
            return {"answer_name": "note_empty_error", "data": {}}

        try:
            note = await self.notes_client.create_note(
                user_id=trigger_data["telegram_id"],
                text=text,
            )
            return {"answer_name": "note_created", "data": note}
        except Exception:
            return {"answer_name": "error", "data": {}}
```

### 📝 Правила документации сервиса

Каждый пакет API-клиента должен содержать в `__init__.py`:
1. **Назначение** — к какому бэкенд-сервису подключается
2. **Base URL** — откуда берётся (из config)
3. **Список методов** — какие эндпоинты вызывает

Каждый метод клиента должен содержать:
1. **Описание** — что делает
2. **Args** — параметры
3. **Returns** — структура ответа
4. **Raises** — возможные ошибки HTTP

---

## Чек-лист добавления элементов

### ✅ Добавление нового API-клиента (новый бэкенд-сервис)

- [ ] **Определить бэкенд-сервис** — какой сервис нужен
- [ ] **Проверить**: существует ли уже бэкенд-сервис? Если нет → создать по `backend_arch`
- [ ] **Добавить URL** в `core/config.py` (из env): `{SERVICE_NAME}_URL`
- [ ] **Создать пакет** `service/{service_name}_api/`
- [ ] **Создать `__init__.py`** с описанием
- [ ] **Создать `schemas.py`** — Pydantic-схемы запросов/ответов (если нужны)
- [ ] **Создать `{name}_client.py`** — наследник `BaseAPIClient`
- [ ] **В docstring** указать Feature ID, Scenario ID
- [ ] **Экспортировать** в `service/__init__.py`

### ✅ Добавление метода в существующий клиент

- [ ] **Определить эндпоинт** бэкенда (метод + URL)
- [ ] **Добавить метод** в класс клиента
- [ ] **Написать docstring** с Args, Returns, Raises
- [ ] **Обновить docstring модуля** — добавить Scenario ID
- [ ] **Обновить schemas.py** если нужны новые типы

### ⚠️ Анти-паттерны

- ❌ Прямое подключение к БД из бота
- ❌ Импорт ORM-моделей в боте
- ❌ Бизнес-логика с данными в Code (кроме UI-логики)
- ❌ Хардкод URL бэкенд-сервисов (только через config)
- ❌ Тяжёлые вычисления в обработчиках бота
