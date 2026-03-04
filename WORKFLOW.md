# Workflow: от запроса на фичу до рабочего кода

## Архитектурный принцип

```
┌─────────────────┐         HTTP / REST         ┌─────────────────────┐
│  Telegram Bot    │ ──────────────────────────→ │  Backend Service     │
│  (bot_tca_arch)  │                             │  (backend_arch)      │
│                  │                             │                      │
│  UI-слой:        │   ← JSON responses ───────  │  Данные + логика:    │
│  виджеты         │   → HTTP requests ────────→ │  model → repo →      │
│  Trigger/Code/   │                             │  service → API       │
│  Answer          │                             │                      │
│  service/ =      │                             │  БД, ML, внешние     │
│  API-клиенты     │                             │  интеграции          │
└─────────────────┘                             └─────────────────────┘
```

**Бот НЕ подключается к БД.** Если фиче нужны данные — создаётся бэкенд-сервис, бот обращается к нему по API.

---

## Обзор процесса

```
1. PRD         →  2. Определить   →  3. Gap-анализ  →  4. Задачи   →  5. Реализация  →  6. Тесты
   (prd.json)      проекты               по проектам     с порядком     код               проверка
```

---

## Шаг 1. Проверить PRD

**Вход:** описание фичи.

Убедиться, что в `prd.json` есть:
- `feature_id` (`F001`)
- `acceptance_criteria` с BDD-сценариями (`SC001`, `SC002`, ...)
- `test_cases` с привязкой к сценариям

Если PRD неполный — дополнить перед началом работы.

**Выход:** валидный `prd.json`.

---

## Шаг 2. Определить затронутые проекты

| Вопрос | Результат |
|--------|-----------|
| Есть UI в Telegram? | → **Бот** (`bot_tca_arch`) |
| Нужна БД / сохранение данных? | → **Бэкенд-сервис** (`backend_arch`) |
| Нужен ML / тяжёлые вычисления? | → **Бэкенд-сервис** (worker) |
| Нужен только UI без данных? | → **Только бот** |
| Нужен новый бэкенд-сервис? | → Scaffold по `backend_arch` |

**Типичные комбинации:**

| Фича | Бот | Бэкенд |
|------|-----|--------|
| Заметки (CRUD) | Виджеты + API-клиент | Model → Repo → Service → API |
| Навигация (/start, /help) | Только виджеты | Не нужен |
| ML-обработка аудио | Виджет + API-клиент | API + Worker |

---

## Шаг 3. Gap-анализ

Для каждого сценария из PRD определить, что есть и чего не хватает:

### Если нужен только бот:

| Сценарий | Виджет | Trigger | Code | Answer | Тест |
|----------|--------|---------|------|--------|------|
| SC001 | ? | ? | ? | ? | ? |
| SC002 | ? | ? | ? | ? | ? |

### Если нужен бот + бэкенд:

| Сценарий | **Бэкенд:** Model | Service | API | **Бот:** API-клиент | Виджет | Тест (бэк) | Тест (бот) |
|----------|-------------------|---------|-----|---------------------|--------|-------------|------------|
| SC001 | ? | ? | ? | ? | ? | ? | ? |
| SC002 | ? | ? | ? | ? | ? | ? | ? |

Где `?` = нужно создать, `✓` = уже есть, `~` = нужно расширить.

---

## Шаг 4. Создать задачи (порядок реализации)

### Если нужен бот + бэкенд:

```
БЭКЕНД (сначала):                          БОТ (после бэкенда):
1. Model + миграция                        5. API-клиент в service/
2. Schema                                  6. Ноды: Trigger, Code, Answer
3. Repository                              7. Виджет в handler/{tag}/{Feature ID}/
4. Service + API endpoints                 8. Состояния, колбеки (если нужны)
                                           9. Тесты бота
         ↓
    Тесты бэкенда (параллельно с п.4)
```

**Правило:** бэкенд создаётся первым, потому что бот зависит от его API.

### Если нужен только бот:

```
1. Ноды: Trigger, Code, Answer
2. Виджет в handler/{tag}/{Feature ID}/
3. Состояния, колбеки (если нужны)
4. Тесты
```

---

## Шаг 5. Реализация

### 5.1 Бэкенд-сервис

Подробная инструкция: **`backend_arch-main/BACKEND_INSTRUCTION.md`**

Краткий чек-лист:

1. Model → `model/{group}/{entity}_model.py` + миграция Alembic
2. Schema → `schema/{group}/{entity}_schema.py` (Create, Response, Filter)
3. Repository → `repository/{group}/{entity}_repository.py`
4. Service → `service/{group}/{entity}_service.py`
5. API → `api/v1/endpoints/{entity}/get.py`, `post.py`, `delete.py`
6. Подключить роутер → `api/v1/include_router.py`
7. Тесты → `tests/{Feature ID}_{name}/test_{Scenario ID}_{desc}.py`

**Обязательно:** секция `## Трассируемость` в docstring каждого модуля.

### 5.2 Telegram-бот

Подробная инструкция: **`bot_tca_arch-main/BOT_INSTRUCTION.md`**

Краткий чек-лист:

1. API-клиент → `service/{name}_api/{name}_client.py` (если фича работает с бэкендом)
2. URL бэкенда → `core/config.py`
3. Trigger → `node/{tag}/trigger/{action}_trigger.py`
4. Code → `node/{tag}/code/{action}_code.py` (вызывает API-клиент)
5. Answer → `node/{tag}/answer/{state}_answer.py`
6. Виджет → `handler/v1/user/{tag}/{Feature ID}/{name}_widget.py`
7. Состояния → `state/{tag}.py` (если нужны)
8. Колбеки → `callback/{tag}.py` (если нужны)
9. Роутер → подключить в `include_router.py`
10. Тесты → `tests/{Feature ID}_{name}/test_{Scenario ID}_{desc}.py`

**Обязательно:** Feature ID и Scenario ID в docstring каждого модуля.

---

## Шаг 6. Тестирование

### Структура тестов (одинаковая для бота и бэкенда)

```
tests/
├── conftest.py
└── {Feature ID}_{name}/
    ├── conftest.py
    └── test_{Scenario ID}_{desc}.py
```

### Что тестируется где

| Что проверяем | Где тестируем | Как |
|---------------|---------------|-----|
| Данные сохраняются в БД | **Бэкенд** | HTTP-запрос → assert БД |
| API возвращает правильный статус | **Бэкенд** | HTTP-запрос → assert response |
| Бот показывает нужный экран | **Бот** | Simulate message → assert answer |
| Бот корректно вызывает API | **Бот** | Mock API-клиент → assert call |
| BDD-сценарий end-to-end | **Бот** | Полный цикл с мокнутым бэкендом |

### Генерация теста из PRD

Для каждого сценария из `prd.json → acceptance_criteria`:

1. Файл: `test_{scenario_id}_{name}.py`
2. Docstring: полный BDD (Given / When / Then)
3. Класс: `Test{ScenarioID}{Name}`
4. Структура: Given → When → Then
5. Если есть `examples` → `@pytest.mark.parametrize`

### Проверка покрытия

- Каждый сценарий из PRD имеет тест в бэкенде (если затрагивает API/данные)
- Каждый сценарий из PRD имеет тест в боте (если затрагивает UI)
- Нет тестов-сирот
- `pytest -q` проходит в обоих проектах

---

## Сводная таблица

| Артефакт | Бот | Бэкенд |
|----------|-----|--------|
| **Репозиторий** | `bot_tca_arch` | `backend_arch` |
| **Инструкция** | `BOT_INSTRUCTION.md` | `BACKEND_INSTRUCTION.md` |
| **PRD** | `prd.json` в корне | `prd.json` в корне |
| **Feature ID в нейминге** | `handler/.../F001/` | Нет (только тесты) |
| **Feature ID в docstring** | Все модули | Все модули |
| **Scenario ID** | Docstring + тесты | Docstring + тесты |
| **БД** | ❌ Нет | ✓ Model + Alembic |
| **Сервисы** | API-клиенты (HTTP) | Бизнес-логика (Repository) |
| **Тесты** | `tests/F001_{name}/test_SC001_...` | `tests/F001_{name}/test_SC001_...` |

---

## Архитектурные справочники

### Бот

| Документ | Путь |
|----------|------|
| **Главная инструкция** | `bot_tca_arch-main/BOT_INSTRUCTION.md` |
| Архитектура | `bot_tca_arch-main/docs/README.md` |
| Виджеты | `bot_tca_arch-main/docs/handler.md` |
| Ноды (Trigger/Code/Answer) | `bot_tca_arch-main/docs/node.md` |
| API-клиенты (service/) | `bot_tca_arch-main/docs/service.md` |
| Трассируемость | `bot_tca_arch-main/docs/traceability.md` |
| Тесты | `bot_tca_arch-main/docs/tests.md` |
| Формат PRD | `bot_tca_arch-main/docs/BRD Template.md` |

### Бэкенд

| Документ | Путь |
|----------|------|
| **Главная инструкция** | `backend_arch-main/BACKEND_INSTRUCTION.md` |
| Архитектура | `backend_arch-main/docs/README.md` |
| Чеклист создания модуля | `backend_arch-main/docs/09-checklist.md` |
| Пример создания сущности | `backend_arch-main/docs/10-example.md` |
| Трассируемость | `backend_arch-main/docs/11-traceability.md` |
| Тесты | `backend_arch-main/docs/12-tests.md` |
