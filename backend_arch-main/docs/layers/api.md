# Слой api/

[← Назад к оглавлению](../README.md)

---

**Назначение:** HTTP endpoints. Приём запросов, валидация, вызов сервисов, формирование ответов.

## Правила

1. Версионирование: `api/v1/`, `api/v2/`
2. Endpoints группируются по ресурсам в подпапках
3. Каждый HTTP метод — отдельный файл (`get.py`, `post.py`, `put.py`, `delete.py`)
4. Роутер ресурса в `router.py` или `__init__.py`
5. Общий роутер версии в `include_router.py`

## Структура

```
api/
├── __init__.py              # Экспорт app
│
└── v1/
    ├── __init__.py
    ├── include_router.py    # Подключение всех роутеров
    │
    └── endpoints/
        ├── __init__.py      # Экспорт роутеров
        │
        ├── candidate/
        │   ├── __init__.py  # Роутер ресурса
        │   ├── get.py       # GET endpoints
        │   ├── post.py      # POST endpoints
        │   └── delete.py    # DELETE endpoints
        │
        └── search/
            ├── __init__.py
            ├── get.py
            └── post.py
```

## Пример роутера ресурса

```python
# api/v1/endpoints/candidate/__init__.py

"""
Candidate Router — роутер для работы с кандидатами.

## Бизнес-контекст
Объединяет все endpoints для управления кандидатами:
- Получение списка и деталей
- Создание новых
- Удаление

## Префикс
/api/v1/candidates
"""

from fastapi import APIRouter

from .get import router as get_router
from .post import router as post_router
from .delete import router as delete_router

router = APIRouter(prefix="/candidates", tags=["Candidates"])

router.include_router(get_router)
router.include_router(post_router)
router.include_router(delete_router)
```

## Пример GET endpoints

```python
# api/v1/endpoints/candidate/get.py

"""
Candidate GET Endpoints — получение кандидатов.

## Endpoints
- GET /candidates — список с фильтрацией
- GET /candidates/{id} — детали кандидата
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema import CandidateResponseSchema, CandidateFilterSchema
from service import CandidateService

router = APIRouter()
service = CandidateService()


@router.get(
    "",
    response_model=List[CandidateResponseSchema],
    summary="Получить список кандидатов",
    description="""
    ## Бизнес-логика
    Возвращает список кандидатов с фильтрацией по:
    - settings_id: ID настроек поиска
    - status: статус кандидата
    - source_type: источник (LinkedIn/HH)
    
    ## Пагинация
    - limit: максимум записей (1-100, по умолчанию 50)
    - offset: смещение (по умолчанию 0)
    """,
)
async def get_candidates(
    settings_id: int = Query(..., description="ID настроек поиска"),
    status: str = Query(None, description="Фильтр по статусу"),
    source_type: str = Query(None, description="Фильтр по источнику"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(db_connect.get_session),
):
    """
    Получить список кандидатов.
    
    ## Входные данные
    - settings_id: ID настроек (обязательно)
    - status, source_type: опциональные фильтры
    - limit, offset: пагинация
    
    ## Выходные данные
    - List[CandidateResponseSchema]
    """
    filters = CandidateFilterSchema(
        settings_id=settings_id,
        status=status,
        source_type=source_type,
        limit=limit,
        offset=offset,
    )
    
    return await service.get_candidates(filters, session)


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponseSchema,
    summary="Получить кандидата по ID",
)
async def get_candidate(
    candidate_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
):
    """
    Получить детали кандидата.
    
    ## Входные данные
    - candidate_id: ID кандидата (path parameter)
    
    ## Выходные данные
    - CandidateResponseSchema
    
    ## Ошибки
    - 404: кандидат не найден
    """
    candidate = await service.get_by_id(candidate_id, session)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return CandidateResponseSchema.model_validate(candidate)
```

## Пример POST endpoints

```python
# api/v1/endpoints/candidate/post.py

"""
Candidate POST Endpoints — создание кандидатов.

## Endpoints
- POST /candidates — создать кандидата
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema import CandidateCreateSchema, CandidateResponseSchema
from service import CandidateService

router = APIRouter()
service = CandidateService()


@router.post(
    "",
    response_model=CandidateResponseSchema,
    status_code=201,
    summary="Создать кандидата",
)
async def create_candidate(
    data: CandidateCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
):
    """
    Создать нового кандидата.
    
    ## Входные данные
    - data: CandidateCreateSchema в теле запроса
    
    ## Выходные данные
    - CandidateResponseSchema (201 Created)
    
    ## Ошибки
    - 400: невалидные данные
    - 409: кандидат уже существует
    """
    try:
        candidate = await service.create_candidate(data, session)
        
        if not candidate:
            raise HTTPException(
                status_code=409,
                detail="Candidate already exists or limit reached"
            )
        
        return CandidateResponseSchema.model_validate(candidate)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Пример include_router.py

```python
"""
Include Router — подключение всех роутеров API v1.

## Бизнес-контекст
Централизованное подключение всех ресурсных роутеров
к основному приложению FastAPI.
"""

from core import app

from .endpoints import (
    candidate_router,
    search_router,
    settings_router,
)

# Prefix для всей версии API
API_PREFIX = "/api/v1"

app.include_router(candidate_router, prefix=API_PREFIX)
app.include_router(search_router, prefix=API_PREFIX)
app.include_router(settings_router, prefix=API_PREFIX)
```

## Документирование endpoints

Используй `summary` и `description` для OpenAPI:

```python
@router.get(
    "/items",
    summary="Краткое описание для списка",  # Показывается в заголовке
    description="""
    ## Развёрнутое описание
    
    Markdown поддерживается.
    
    - Пункт 1
    - Пункт 2
    """,
    response_description="Список элементов",
)
async def get_items():
    """Docstring для внутренней документации."""
    pass
```

## Что должно быть в API

✅ Правильно:
- Валидация входных данных (через Schema)
- Вызов сервисов
- Преобразование ошибок в HTTP коды
- Формирование ответа

❌ Неправильно:
- Бизнес-логика (это service)
- Прямые запросы к БД (это repository)
- Сложные вычисления

---

[Назад к оглавлению →](../README.md)
