# Тестирование

## Назначение

Тесты генерируются на основе BDD-сценариев из `prd.json`. Каждый сценарий = один тестовый модуль. Тесты являются доказательством реализации бизнес-требований.

---

## Структура тестов

```
tests/
├── conftest.py                                  # Глобальные фикстуры
├── F001_notes/                                  # Feature ID + описание
│   ├── conftest.py                              # Фикстуры фичи
│   ├── test_SC001_create_text_note.py
│   ├── test_SC002_create_empty_note_error.py
│   ├── test_SC003_list_notes_with_data.py
│   ├── test_SC004_list_notes_empty.py
│   └── test_SC005_delete_note.py
├── F002_templates/
│   ├── conftest.py
│   ├── test_SC001_create_template.py
│   └── test_SC002_apply_template.py
└── ...
```

### Правила нейминга

| Элемент | Формат | Пример |
|---------|--------|--------|
| Директория фичи | `{Feature ID}_{snake_case_name}/` | `F001_notes/` |
| Тестовый модуль | `test_{Scenario ID}_{snake_case_desc}.py` | `test_SC001_create_text_note.py` |
| Класс тестов | `Test{ScenarioID}{PascalCaseDesc}` | `TestSC001CreateTextNote` |
| Метод теста | `test_{описание_проверки}` | `test_note_is_saved` |

---

## Формат тестового модуля

### Docstring — BDD-сценарий

Каждый тестовый файл начинается с полного BDD-сценария из PRD:

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

### Структура тела — Given / When / Then

```python
import pytest


class TestSC001CreateTextNote:
    """Тесты для SC001 — создание текстовой заметки."""

    @pytest.fixture
    def setup(self, authorized_user):
        """Given: Пользователь авторизован и на главном экране."""
        return authorized_user

    async def test_note_is_saved(self, setup, bot):
        """Заметка сохраняется в БД после отправки текста."""
        user = setup

        # When
        await user.press_button("Создать заметку")
        await user.send("Купить молоко")

        # Then
        response = await bot.last_message()
        assert "сохранена" in response.text.lower()

    async def test_note_appears_in_list(self, setup, bot):
        """Созданная заметка видна в списке."""
        user = setup

        # When
        await user.press_button("Создать заметку")
        await user.send("Купить молоко")

        # Then
        await user.press_button("Мои заметки")
        response = await bot.last_message()
        assert "Купить молоко" in response.text
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
| `acceptance_criteria[].bdd.when` | Действие в тесте |
| `acceptance_criteria[].bdd.then` | Assert |
| `acceptance_criteria[].bdd.and_postconditions` | Дополнительные assert |
| `test_cases[].examples` | `@pytest.mark.parametrize` |

### Пример с parametrize (data-driven)

Если в PRD указаны `examples`:

```json
{
  "test_id": "T002",
  "scenario_id": "SC002",
  "setup": "Пользователь на экране создания",
  "action": "Отправить пустое сообщение",
  "assertion": "Бот показал ошибку",
  "examples": [
    {"input": {"text": ""}, "expected": {"error": "Заметка не может быть пустой"}},
    {"input": {"text": "   "}, "expected": {"error": "Заметка не может быть пустой"}}
  ]
}
```

Генерируется:

```python
"""
Feature: F001 — Управление заметками
Scenario: SC002 — Пользователь пытается создать пустую заметку

Given: Пользователь на экране создания заметки
When: Отправляет пустое сообщение
Then: Бот показывает ошибку «Заметка не может быть пустой»
"""
import pytest


class TestSC002CreateEmptyNoteError:

    @pytest.mark.parametrize("text,expected_error", [
        ("", "Заметка не может быть пустой"),
        ("   ", "Заметка не может быть пустой"),
    ])
    async def test_empty_note_rejected(self, authorized_user, bot, text, expected_error):
        user = authorized_user

        # When
        await user.press_button("Создать заметку")
        await user.send(text)

        # Then
        response = await bot.last_message()
        assert expected_error in response.text
```

---

## Чек-лист добавления тестов

### Для каждого сценария из PRD:

- [ ] Создать директорию `tests/{Feature ID}_{name}/` (если не существует)
- [ ] Создать `conftest.py` с фикстурами фичи (если не существует)
- [ ] Создать файл `test_{Scenario ID}_{name}.py`
- [ ] В docstring указать Feature, Scenario и полный BDD
- [ ] Создать класс `Test{ScenarioID}{Name}`
- [ ] Реализовать тесты по структуре Given / When / Then
- [ ] Если в PRD есть `examples` — использовать `@pytest.mark.parametrize`
- [ ] Убедиться, что assert покрывает `then` и `and_postconditions`

### Проверка покрытия:

- [ ] Для каждого `acceptance_criteria` в PRD существует `test_{scenario_id}_*.py`
- [ ] Каждый тестовый файл ссылается на существующий Scenario ID
- [ ] Нет тестов-сирот (без привязки к сценарию)
