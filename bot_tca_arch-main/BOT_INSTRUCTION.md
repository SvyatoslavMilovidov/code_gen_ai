# Инструкция: работа с репозиторием Telegram-бота

## Что это за репозиторий

Telegram-бот на aiogram 3, построенный по виджетной архитектуре: Trigger → Code → Answer. Бот **не владеет данными** — вся работа с БД, ML и другими тяжёлыми операциями происходит через вызовы API бэкенд-сервисов.

---

## Архитектурное правило

```
Бот = UI-слой.  Данные = бэкенд-сервисы.
```

Если фиче нужна работа с БД — **создаётся отдельный бэкенд-сервис** по архитектуре `backend_arch`, а бот обращается к нему через HTTP-клиент в `service/`.

**Бот делает:**
- Принимает события от Telegram
- Оркестрирует экраны: Trigger → Code → Answer
- Вызывает бэкенд-сервисы через `service/` (HTTP)
- Отрисовывает ответы

**Бот НЕ делает:**
- ❌ Подключение к БД, ORM-модели, миграции
- ❌ Тяжёлые вычисления (ML, транскрипция)
- ❌ CRUD-операции с данными напрямую

---

## Структура проекта

```
bot/
├── app.py                          # Точка входа
├── prd.json                        # PRD — источник фич и сценариев
├── requirements.txt
├── example.env
│
├── core/                           # Конфигурация
│   ├── config.py                   # Настройки из env (включая URL бэкендов)
│   ├── loader.py                   # Инициализация bot, dp
│   └── vocab.py                    # Тексты и словари
│
├── node/                           # UI-компоненты (LEGO-кирпичики)
│   └── {tag}/                      # Группировка по тегам
│       ├── trigger/                # Визуальные операции
│       ├── code/                   # Логика выбора Answer (вызовы service/)
│       └── answer/                 # Отрисовка экранов
│
├── handler/                        # Виджеты-оркестраторы
│   └── v1/user/
│       └── {tag}/
│           └── {Feature ID}/       # Группировка по фичам из PRD
│               └── {name}_widget.py
│
├── service/                        # API-клиенты к бэкенд-сервисам
│   ├── base_client.py              # Базовый HTTP-клиент
│   └── {service_name}_api/
│       ├── {name}_client.py        # HTTP-методы
│       └── schemas.py              # Pydantic-схемы запросов/ответов
│
├── callback/                       # Классы колбеков по тегам
├── state/                          # Состояния FSM по тегам
├── data/                           # Медиа и буферы
│
├── tests/                          # Тесты по фичам и сценариям
│   └── {Feature ID}_{name}/
│       └── test_{Scenario ID}_{desc}.py
│
└── docs/                           # Документация архитектуры
```

---

## Пошаговая инструкция: добавление фичи

### 1. Проверить PRD

Убедиться, что в `prd.json` есть:
- `feature_id` (например, `F001`)
- `acceptance_criteria` с BDD-сценариями (`SC001`, `SC002`, ...)
- `test_cases`

### 2. Определить, нужен ли бэкенд

| Вопрос | Действие |
|--------|----------|
| Фича требует сохранения данных? | → нужен бэкенд-сервис |
| Фича вызывает ML / внешний API? | → нужен бэкенд-сервис (worker) |
| Фича только UI (навигация, FSM)? | → только бот |

Если нужен бэкенд — **сначала создать/расширить** бэкенд-сервис по `backend_arch-main/BACKEND_INSTRUCTION.md`.

### 3. Создать/расширить API-клиент (service/)

Если фича взаимодействует с бэкендом:

```
service/{service_name}_api/
├── __init__.py
├── {name}_client.py     ← наследник BaseAPIClient
└── schemas.py           ← Pydantic-схемы
```

- Добавить URL бэкенда в `core/config.py` → `{SERVICE_NAME}_URL`
- Создать методы клиента, соответствующие эндпоинтам бэкенда
- В docstring указать Feature ID и Scenario ID

### 4. Создать компоненты (node/)

Определить тег. Для каждого действия создать:

```
node/{tag}/
    trigger/{action}_trigger.py
    code/{action}_code.py
    answer/{state}_answer.py
```

**Trigger** — визуальные операции (удаление сообщений, сброс FSM)
**Code** — вызов API-клиента из `service/`, выбор Answer
**Answer** — отрисовка UI (текст + клавиатура)

В docstring **каждого** компонента указать:

```python
"""
Feature: F001 — Управление заметками
Scenarios: SC001, SC002
"""
```

### 5. Создать виджет (handler/)

Виджет размещается в директории с Feature ID:

```
handler/v1/user/{tag}/{Feature ID}/{name}_widget.py
```

Виджет оркестрирует: Trigger → Code → Answer.

В docstring виджета:

```python
"""
Feature: F001 — Управление заметками
Scenarios: SC001, SC002

SC001 — успешное создание → answer: note_created
SC002 — пустой текст → answer: note_empty_error

Доступен из: ...
Переводит в: ...
"""
```

### 6. Создать состояния и колбеки (если нужны)

- `state/{tag}.py` — FSM-состояния
- `callback/{tag}.py` — колбек-классы

### 7. Подключить роутер

В `handler/v1/user/router.py` создать роутер тега (если новый).
В `handler/include_router.py` подключить.

### 8. Создать тесты

```
tests/{Feature ID}_{name}/
    conftest.py
    test_{Scenario ID}_{desc}.py
```

Каждый тест:
- Docstring с полным BDD из PRD
- Класс `Test{ScenarioID}{Name}`
- Структура Given / When / Then
- `@pytest.mark.parametrize` если есть `examples` в PRD

---

## Поток данных (пример: создание заметки)

```
Пользователь → /create_note → Telegram → aiogram

1. handler/v1/user/notes/F001/create_note_widget.py
   │
   ├─ 2. node/notes/trigger/create_note_trigger.py
   │     → Удалить старые сообщения, сбросить FSM
   │     → return {telegram_id, text}
   │
   ├─ 3. node/notes/code/create_note_code.py
   │     → if text пустой: return {answer: "note_empty_error"}   SC002
   │     → notes_client.create_note(user_id, text)               HTTP → Backend
   │     → return {answer: "note_created", data: note}           SC001
   │
   └─ 4. node/notes/answer/note_created_answer.py
         → Показать "Заметка сохранена ✓"

Backend (отдельный сервис):
   POST /api/v1/notes → NoteService.create() → NoteRepository → DB
```

---

## Справочники

| Документ | Описание |
|----------|----------|
| [docs/README.md](docs/README.md) | Обзор архитектуры |
| [docs/handler.md](docs/handler.md) | Виджеты-оркестраторы, чек-лист |
| [docs/node.md](docs/node.md) | Компоненты Trigger / Code / Answer |
| [docs/service.md](docs/service.md) | API-клиенты к бэкендам |
| [docs/traceability.md](docs/traceability.md) | Связь PRD → код → тесты |
| [docs/tests.md](docs/tests.md) | Конвенции тестирования |
| [docs/BRD Template.md](docs/BRD%20Template.md) | Формат PRD (JSON-схема) |
| [docs/callback.md](docs/callback.md) | Колбеки |
| [docs/state.md](docs/state.md) | FSM-состояния |
| [docs/core.md](docs/core.md) | Конфигурация |
