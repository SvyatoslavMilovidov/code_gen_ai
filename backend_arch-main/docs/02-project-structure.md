# Структура проекта

[← Назад к оглавлению](README.md)

---

## Полная структура

```
service_name/
├── main.py                    # Точка входа
├── alembic.ini               # Конфигурация миграций
├── requirements.txt          # Зависимости
│
├── core/                     # Ядро приложения
│   ├── __init__.py
│   ├── config.py            # Конфигурация
│   ├── database.py          # Подключение к БД
│   └── loader.py            # Инициализация FastAPI
│
├── model/                    # ORM модели
│   ├── __init__.py          # Экспорт всех моделей
│   ├── base_model.py        # Базовая модель
│   ├── enums.py             # Перечисления
│   │
│   ├── candidate/           # Группа: кандидаты
│   │   ├── __init__.py
│   │   ├── candidate_model.py
│   │   └── evaluation_model.py
│   │
│   └── search/              # Группа: поиск
│       ├── __init__.py
│       ├── settings_model.py
│       └── task_model.py
│
├── schema/                   # Pydantic схемы
│   ├── __init__.py
│   │
│   ├── candidate/
│   │   ├── __init__.py
│   │   ├── candidate_schema.py
│   │   └── evaluation_schema.py
│   │
│   └── search/
│       ├── __init__.py
│       └── settings_schema.py
│
├── repository/               # Репозитории (доступ к данным)
│   ├── __init__.py
│   ├── base_repository.py   # Базовый репозиторий
│   │
│   ├── candidate/
│   │   ├── __init__.py
│   │   ├── candidate_repository.py
│   │   └── evaluation_repository.py
│   │
│   └── search/
│       ├── __init__.py
│       └── settings_repository.py
│
├── service/                  # Бизнес-логика
│   ├── __init__.py
│   │
│   ├── candidate/
│   │   ├── __init__.py
│   │   ├── candidate_service.py
│   │   └── evaluation_service.py
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   └── settings_service.py
│   │
│   └── providers/           # Внешние интеграции
│       ├── __init__.py
│       ├── base_provider.py
│       └── linkedin_provider.py
│
├── api/                      # HTTP API
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── include_router.py
│       └── endpoints/
│           ├── __init__.py
│           ├── candidate/
│           │   ├── __init__.py
│           │   ├── get.py
│           │   ├── post.py
│           │   └── delete.py
│           └── search/
│               ├── __init__.py
│               └── post.py
│
└── migrations/               # Миграции Alembic
    ├── env.py
    └── versions/
```

## Описание папок

| Папка | Назначение | Подробнее |
|-------|------------|-----------|
| `core/` | Ядро: конфиг, БД, FastAPI | [→ core](layers/core.md) |
| `model/` | ORM модели SQLAlchemy | [→ model](layers/model.md) |
| `schema/` | Pydantic схемы | [→ schema](layers/schema.md) |
| `repository/` | Слой доступа к данным | [→ repository](layers/repository.md) |
| `service/` | Бизнес-логика | [→ service](layers/service.md) |
| `api/` | HTTP endpoints | [→ api](layers/api.md) |
| `migrations/` | Миграции Alembic | — |

## Группировка по сущностям

Внутри каждого слоя файлы группируются в подпапки по главной сущности:

```
{layer}/
├── __init__.py              # Экспорт всех классов слоя
├── base_{layer}.py          # Базовый класс (если есть)
│
├── {entity1}/               # Группа по сущности
│   ├── __init__.py
│   ├── {entity1}_{layer}.py
│   └── {related}_{layer}.py
│
└── {entity2}/
    ├── __init__.py
    └── {entity2}_{layer}.py
```

### Пример группировки

Если есть сущности `Candidate` и `CandidateEvaluation`:

```
model/
  candidate/
    candidate_model.py       # Основная сущность
    evaluation_model.py      # Связанная сущность

repository/
  candidate/
    candidate_repository.py
    evaluation_repository.py

service/
  candidate/
    candidate_service.py
    evaluation_service.py
```

---

[Далее: Слой core/ →](layers/core.md)
