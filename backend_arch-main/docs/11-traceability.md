# Трассируемость: PRD → Код → Тесты

[← Назад к оглавлению](README.md)

---

## Назначение

Каждый модуль связан с бизнес-требованием через Feature ID и Scenario ID из `prd.json`.

---

## Канонические ID

| Сущность | Формат | Пример |
|----------|--------|--------|
| Feature | `F{NNN}` | `F001`, `F002` |
| Scenario | `SC{NNN}` | `SC001`, `SC002` |
| Business Rule | `BR{NNN}` | `BR001` |
| Non-Functional Req. | `NFR{NNN}` | `NFR001` |
| Test Case | `T{NNN}` | `T001` |
| Полная ссылка | `F{NNN}.SC{NNN}` | `F001.SC003` |

---

## Источник правды: prd.json

Файл `prd.json` размещается в корне проекта. Формат описан в документации бота: `BRD Template.md`.

```
prd.json
  └─ features[].feature_id              → F001
       └─ acceptance_criteria[].scenario_id  → SC001, SC002, ...
       └─ test_cases[].test_id               → T001, T002, ...
```

---

## Где указывать ID в коде

### В основном коде — только docstring

В бэкенде Feature ID и Scenario ID **не влияют на нейминг** файлов и директорий основного кода. Привязка — только через секцию `## Трассируемость` в docstring.

#### Модель

```python
"""
NoteModel — модель заметки.

## Трассируемость
Feature: F001 — Управление заметками
Scenarios: SC001, SC002, SC003, SC004, SC005

## Бизнес-контекст
Хранит текстовые заметки пользователя.
"""
```

#### Сервис

```python
"""
NoteService — сервис управления заметками.

## Трассируемость
Feature: F001 — Управление заметками
Scenarios: SC001, SC002, SC003, SC004, SC005

## Бизнес-контекст
CRUD-операции над заметками с валидацией.
"""
```

#### API Endpoint

```python
"""
Создание заметки.

## Трассируемость
Feature: F001
Scenarios: SC001, SC002

## Бизнес-логика
SC001 — текст не пустой → заметка создана (201)
SC002 — текст пустой → ошибка валидации (422)
"""
```

#### Инфраструктурные модули

```python
"""
DatabaseConnection — подключение к БД.

## Трассируемость
Infrastructure — не привязан к конкретной фиче
"""
```

### В тестах — Feature ID и Scenario ID в нейминге

```
tests/
├── conftest.py
├── F001_notes/
│   ├── conftest.py
│   ├── test_SC001_create_note.py
│   ├── test_SC002_create_empty_note.py
│   ├── test_SC003_list_notes.py
│   ├── test_SC004_list_notes_empty.py
│   └── test_SC005_delete_note.py
└── F002_auth/
    ├── conftest.py
    └── test_SC001_login.py
```

Подробнее о тестах: [12-tests.md](12-tests.md)

---

## Матрица трассируемости (пример)

| Scenario | Model | Service | API Endpoint | Тест |
|----------|-------|---------|-------------|------|
| F001.SC001 | note_model | note_service.create | POST /notes | test_SC001_create_note |
| F001.SC002 | note_model | note_service.create | POST /notes | test_SC002_create_empty_note |
| F001.SC003 | note_model | note_service.get_list | GET /notes | test_SC003_list_notes |

---

## Правила

1. **Секция `## Трассируемость`** обязательна в docstring каждого модуля
2. **Feature ID** — указывается всегда (или `Infrastructure` для базовых модулей)
3. **Scenario ID** — указывается для модулей, обслуживающих конкретные сценарии
4. **Каждый сценарий из PRD должен иметь тест**
5. **Запрещены сироты** — код без привязки к PRD, или сценарий без теста

---

[Далее: Тестирование →](12-tests.md)
