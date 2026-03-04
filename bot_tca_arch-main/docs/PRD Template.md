# Product Requirements Document — формат PRD

## Назначение

PRD — единый источник правды о продукте. Файл `prd.json` размещается в корне проекта и содержит описание всех фич, BDD-сценариев и тест-кейсов.

Из PRD берутся:
- **Feature ID** (`F001`, `F002`, ...) — для нейминга директорий виджетов и тестов
- **Scenario ID** (`SC001`, `SC002`, ...) — для нейминга тестовых модулей и docstring
- **BDD-блоки** (Given / When / Then) — для генерации тел тестов
- **Test cases** — для data-driven тестов

---

## JSON-схема PRD

```json
{
  "product_name": "string",
  "product_overview": "string",
  "features": [
    {
      "feature_id": "string",
      "general_info": {
        "name": "string",
        "overview": "string"
      },
      "goal_and_context": {
        "business_goal": "string",
        "user_problem": "string"
      },
      "actors_and_roles": {
        "primary_user": "string",
        "secondary_user": "string | null",
        "system_service": "string | null"
      },
      "business_rules": [
        {
          "rule_id": "string",
          "description": "string"
        }
      ],
      "acceptance_criteria": [
        {
          "scenario_id": "string",
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
        {
          "nfr_id": "string",
          "type": "string",
          "description": "string"
        }
      ],
      "test_cases": [
        {
          "test_id": "string",
          "scenario_id": "string",
          "setup": "string",
          "action": "string",
          "assertion": "string",
          "examples": [
            {
              "input": "object",
              "expected": "object"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Описание полей

### Корневой уровень

| Поле | Тип | Описание |
|------|-----|----------|
| `product_name` | string | Название продукта |
| `product_overview` | string | Краткое описание продукта |
| `features` | array | Список фич продукта |

### Feature

| Поле | Тип | Описание |
|------|-----|----------|
| `feature_id` | string | Уникальный ID фичи: `F001`, `F002`, ... |
| `general_info.name` | string | Название фичи |
| `general_info.overview` | string | Краткое описание фичи |
| `goal_and_context.business_goal` | string | Какую бизнес-цель решает. Какие метрики / KPI улучшает |
| `goal_and_context.user_problem` | string | Какую боль пользователя решает |
| `actors_and_roles.primary_user` | string | Основной пользователь |
| `actors_and_roles.secondary_user` | string \| null | Косвенный участник |
| `actors_and_roles.system_service` | string \| null | Внешние системы |

### Business Rules

| Поле | Тип | Описание |
|------|-----|----------|
| `rule_id` | string | ID правила: `BR001`, `BR002`, ... |
| `description` | string | Формализованное правило (без UI, только логика) |

### Acceptance Criteria (BDD-сценарии)

Каждый сценарий описывает **одно бизнес-поведение**.

| Поле | Тип | Описание |
|------|-----|----------|
| `scenario_id` | string | ID сценария: `SC001`, `SC002`, ... |
| `user_story` | string | User story: «Я, как пользователь, хочу...» |
| `bdd.given` | string | Начальные условия |
| `bdd.and_preconditions` | array | Дополнительные предусловия |
| `bdd.when` | string | Действие пользователя или системы |
| `bdd.then` | string | Ожидаемый результат |
| `bdd.and_postconditions` | array | Дополнительные постусловия |

### Non-Functional Requirements

| Поле | Тип | Описание |
|------|-----|----------|
| `nfr_id` | string | ID требования: `NFR001`, ... |
| `type` | string | Тип: Performance, Security, Scalability, Auditability, Availability |
| `description` | string | Описание требования |

### Test Cases

Каждый тест-кейс привязан к сценарию через `scenario_id`.

| Поле | Тип | Описание |
|------|-----|----------|
| `test_id` | string | ID теста: `T001`, `T002`, ... |
| `scenario_id` | string | Ссылка на сценарий (`SC001`) |
| `setup` | string | Подготовка состояния (из `Given`) |
| `action` | string | Выполняемое действие (из `When`) |
| `assertion` | string | Проверка результата (из `Then`) |
| `examples` | array | Данные для data-driven тестов |

---

## Пример PRD

```json
{
  "product_name": "Manager Bot",
  "product_overview": "Telegram-бот для управления заметками и задачами",
  "features": [
    {
      "feature_id": "F001",
      "general_info": {
        "name": "Управление заметками",
        "overview": "Пользователь может создавать, просматривать и удалять текстовые заметки"
      },
      "goal_and_context": {
        "business_goal": "Увеличить retention за счёт полезного инструмента",
        "user_problem": "Нет удобного способа фиксировать мысли прямо в Telegram"
      },
      "actors_and_roles": {
        "primary_user": "Авторизованный пользователь бота",
        "secondary_user": null,
        "system_service": "PostgreSQL"
      },
      "business_rules": [
        {
          "rule_id": "BR001",
          "description": "Заметка не может быть пустой"
        },
        {
          "rule_id": "BR002",
          "description": "Максимум 1000 заметок на пользователя"
        }
      ],
      "acceptance_criteria": [
        {
          "scenario_id": "SC001",
          "user_story": "Как пользователь, я хочу создать текстовую заметку",
          "bdd": {
            "given": "Пользователь авторизован",
            "and_preconditions": ["Пользователь на главном экране"],
            "when": "Нажимает «Создать заметку» и вводит текст",
            "then": "Заметка сохранена в БД",
            "and_postconditions": ["Бот показывает подтверждение"]
          }
        },
        {
          "scenario_id": "SC002",
          "user_story": "Как пользователь, я получаю ошибку при пустой заметке",
          "bdd": {
            "given": "Пользователь на экране создания заметки",
            "and_preconditions": [],
            "when": "Отправляет пустое сообщение",
            "then": "Бот показывает ошибку «Заметка не может быть пустой»",
            "and_postconditions": []
          }
        },
        {
          "scenario_id": "SC003",
          "user_story": "Как пользователь, я хочу видеть список своих заметок",
          "bdd": {
            "given": "У пользователя есть заметки",
            "and_preconditions": [],
            "when": "Нажимает «Мои заметки»",
            "then": "Бот показывает список заметок с датами",
            "and_postconditions": []
          }
        },
        {
          "scenario_id": "SC004",
          "user_story": "Как пользователь, я вижу сообщение о пустом списке",
          "bdd": {
            "given": "У пользователя нет заметок",
            "and_preconditions": [],
            "when": "Нажимает «Мои заметки»",
            "then": "Бот показывает «У вас пока нет заметок»",
            "and_postconditions": []
          }
        },
        {
          "scenario_id": "SC005",
          "user_story": "Как пользователь, я хочу удалить заметку",
          "bdd": {
            "given": "Пользователь видит список заметок",
            "and_preconditions": [],
            "when": "Нажимает «Удалить» на заметке",
            "then": "Заметка удалена из БД",
            "and_postconditions": ["Список обновлён"]
          }
        }
      ],
      "non_functional_requirements": [
        {
          "nfr_id": "NFR001",
          "type": "Performance",
          "description": "Отклик бота < 2 секунд"
        },
        {
          "nfr_id": "NFR002",
          "type": "Security",
          "description": "Пользователь видит только свои заметки"
        }
      ],
      "test_cases": [
        {
          "test_id": "T001",
          "scenario_id": "SC001",
          "setup": "Создать авторизованного пользователя",
          "action": "Отправить текст заметки",
          "assertion": "Заметка сохранена, бот ответил подтверждением",
          "examples": [
            {"input": {"text": "Купить молоко"}, "expected": {"status": "created"}},
            {"input": {"text": "Длинный текст на 500 символов..."}, "expected": {"status": "created"}}
          ]
        },
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
      ]
    }
  ]
}
```

---

## Связь PRD с кодом

### В боте

- **Feature ID** → имя директории виджетов: `handler/v1/user/{tag}/F001/`
- **Feature ID** → имя директории тестов: `tests/F001_notes/`
- **Scenario ID** → docstring виджетов и нод
- **Scenario ID** → имя тестового модуля: `test_SC001_create_text_note.py`

### В бэкенде

- **Feature ID** → имя директории тестов: `tests/F001_notes/`
- **Feature ID + Scenario ID** → docstring сервисов и эндпоинтов
- **Scenario ID** → имя тестового модуля: `test_SC001_create_text_note.py`

Подробнее см. [traceability.md](traceability.md).
