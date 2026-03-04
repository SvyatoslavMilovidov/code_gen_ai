# Трассируемость: PRD → Код → Тесты

## Назначение

Каждая строчка кода должна быть привязана к бизнес-требованию. Трассируемость позволяет:
- Понять, зачем существует модуль
- Найти все компоненты, реализующие конкретный сценарий
- Убедиться, что каждый сценарий покрыт тестами
- Оценить impact при изменении требований

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

Feature ID — глобально уникален в рамках продукта.
Scenario ID — уникален в рамках фичи.

---

## Источник правды: prd.json

Файл `prd.json` в корне проекта — единственный источник ID.

```
prd.json
  └─ features[].feature_id              → F001
       └─ acceptance_criteria[].scenario_id  → SC001, SC002, ...
       └─ test_cases[].test_id               → T001, T002, ...
```

Подробнее о формате: [BRD Template.md](BRD%20Template.md)

---

## Где указывать ID в коде

### Виджеты (handler/)

**Директория** именуется по Feature ID:

```
handler/v1/user/{tag}/{Feature ID}/{widget}_widget.py
handler/v1/user/notes/F001/create_note_widget.py
```

**Docstring** содержит Feature ID и список Scenario ID:

```python
"""
Виджет: Создание заметки.

Feature: F001 — Управление заметками
Scenarios: SC001, SC002

SC001 — успешное создание → answer: note_created
SC002 — пустой текст → answer: note_empty_error
"""
```

**ANSWER_REGISTRY** содержит привязку к Scenario ID в комментариях:

```python
ANSWER_REGISTRY = {
    "note_created": NoteCreatedAnswer(),        # SC001
    "note_empty_error": NoteEmptyErrorAnswer(),  # SC002
}
```

### Ноды (node/)

Директория **без** Feature ID. Привязка **только в docstring**:

```python
"""
Code для создания заметки.

Feature: F001
Scenarios: SC001, SC002

SC001 — текст не пустой → answer_name: "note_created"
SC002 — текст пустой → answer_name: "note_empty_error"
"""
```

### Сервисы (service/)

Привязка **только в docstring** (сервис может обслуживать несколько фич):

```python
"""
Сервис работы с заметками.

Features: F001
Scenarios: SC001, SC002, SC005
"""
```

### Колбеки и состояния (callback/, state/)

Привязка **только в docstring**:

```python
"""
Колбеки для управления заметками.

Feature: F001
"""
```

### Тесты (tests/)

**Директория** именуется по Feature ID. **Файл** — по Scenario ID:

```
tests/F001_notes/test_SC001_create_text_note.py
tests/F001_notes/test_SC002_create_empty_note_error.py
```

**Docstring** теста содержит полный BDD-сценарий:

```python
"""
Feature: F001 — Управление заметками
Scenario: SC001 — Пользователь создаёт текстовую заметку

Given: Пользователь авторизован
And: Пользователь на главном экране
When: Нажимает «Создать заметку» и вводит текст
Then: Заметка сохранена в БД
And: Бот показывает подтверждение
"""
```

---

## Матрица трассируемости (пример)

| Scenario | Виджет | Trigger | Code | Answer | Тест |
|----------|--------|---------|------|--------|------|
| F001.SC001 | create_note_widget | create_note_trigger | create_note_code | note_created_answer | test_SC001_... |
| F001.SC002 | create_note_widget | create_note_trigger | create_note_code | note_empty_error_answer | test_SC002_... |
| F001.SC003 | list_notes_widget | list_notes_trigger | list_notes_code | notes_list_answer | test_SC003_... |
| F001.SC004 | list_notes_widget | list_notes_trigger | list_notes_code | notes_empty_answer | test_SC004_... |
| F001.SC005 | delete_note_widget | delete_note_trigger | delete_note_code | note_deleted_answer | test_SC005_... |

---

## Правила

1. **Каждый сценарий из PRD должен иметь тест** — `tests/{Feature ID}_{name}/test_{Scenario ID}_{name}.py`
2. **Каждый виджет должен ссылаться на Feature и Scenarios** — в docstring модуля
3. **Каждый Answer должен быть привязан к Scenario** — в комментарии ANSWER_REGISTRY или docstring
4. **Запрещены «сироты»** — код без привязки к PRD, или сценарий без теста
