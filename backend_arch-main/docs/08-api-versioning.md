# API версионирование

[← Назад к оглавлению](README.md)

---

## Структура версий

```
api/
├── __init__.py
├── v1/                      # Версия 1 (стабильная)
│   ├── __init__.py
│   ├── include_router.py
│   └── endpoints/
│       └── ...
│
└── v2/                      # Версия 2 (новая)
    ├── __init__.py
    ├── include_router.py
    └── endpoints/
        └── ...
```

## Правила версионирования

| Изменение | Действие |
|-----------|----------|
| Breaking change | Новая major версия (v1 → v2) |
| Новый endpoint | Добавить в текущую версию |
| Deprecated endpoint | Пометить, не удалять |
| Удаление endpoint | Только в новой major версии |

## Когда создавать новую версию

**v2 нужна при:**
- Изменение структуры ответа
- Изменение обязательных параметров
- Удаление полей из ответа
- Изменение типов данных

**v2 НЕ нужна при:**
- Добавление нового endpoint
- Добавление опционального параметра
- Добавление нового поля в ответ

## Пометка deprecated

```python
from fastapi import APIRouter, Query
import warnings

router = APIRouter()


@router.get(
    "/old-endpoint",
    deprecated=True,  # Помечает в OpenAPI
    summary="[DEPRECATED] Старый метод",
    description="Используйте GET /new-endpoint вместо этого.",
)
async def old_endpoint():
    """Deprecated: будет удалён в v2."""
    warnings.warn("old_endpoint is deprecated", DeprecationWarning)
    # ... логика
```

## Подключение версий

```python
# api/__init__.py

from core import app

# Подключаем все версии API
from .v1 import include_router as v1_router
from .v2 import include_router as v2_router

# v1 — /api/v1/...
# v2 — /api/v2/...
```

## URL схема

```
/api/v1/candidates          # Версия 1
/api/v1/candidates/{id}

/api/v2/candidates          # Версия 2
/api/v2/candidates/{id}
```

## Политика поддержки

| Событие | Срок |
|---------|------|
| Выход v2 | Начало deprecated периода для v1 |
| v1 deprecated | Минимум 6 месяцев поддержки |
| Удаление v1 | После deprecated периода |

## Миграция между версиями

### В документации v2

```python
@router.get(
    "/candidates",
    description="""
    ## Изменения относительно v1
    
    - Поле `full_name` переименовано в `name`
    - Добавлено обязательное поле `source_id`
    - Удалено поле `legacy_status`
    
    ## Миграция
    
    ```diff
    - GET /api/v1/candidates
    + GET /api/v2/candidates
    ```
    """,
)
async def get_candidates():
    pass
```

## Общие компоненты

Если логика одинакова между версиями, выноси в service:

```
service/
  candidate/
    candidate_service.py     # Общая логика

api/
  v1/endpoints/candidate/    # Старый формат ответа
  v2/endpoints/candidate/    # Новый формат ответа
```

Разница только в Schema и маппинге:

```python
# api/v1/endpoints/candidate/get.py
from schema.v1 import CandidateResponseV1Schema

@router.get("", response_model=List[CandidateResponseV1Schema])
async def get_candidates(...):
    candidates = await service.get_candidates(...)
    return [CandidateResponseV1Schema.from_model(c) for c in candidates]

# api/v2/endpoints/candidate/get.py
from schema.v2 import CandidateResponseV2Schema

@router.get("", response_model=List[CandidateResponseV2Schema])
async def get_candidates(...):
    candidates = await service.get_candidates(...)
    return [CandidateResponseV2Schema.from_model(c) for c in candidates]
```

---

[Далее: Чеклист →](09-checklist.md)
