# Пример создания сущности

[← Назад к оглавлению](README.md)

---

Создадим сущность **Vacancy** (вакансия) от модели до API.

## 1. Модель

```python
# model/vacancy/vacancy_model.py

"""
VacancyModel — модель вакансии.

## Бизнес-контекст
Представляет вакансию, для которой ищутся кандидаты.
Содержит описание позиции и требования.

## Поля
- title: название вакансии
- description: описание
- requirements: требования
- status: статус (ACTIVE, CLOSED)
"""

from sqlalchemy import Column, String, Text, Enum

from model.base_model import Base, BaseModel
from model.enums import VacancyStatusEnum


class VacancyModel(Base, BaseModel):
    __tablename__ = "vacancies"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    status = Column(Enum(VacancyStatusEnum), default=VacancyStatusEnum.ACTIVE)
```

### Добавить Enum

```python
# model/enums.py

class VacancyStatusEnum(str, Enum):
    """Статус вакансии."""
    
    ACTIVE = "ACTIVE"    # Активная
    CLOSED = "CLOSED"    # Закрыта
```

### Экспорт

```python
# model/vacancy/__init__.py
from .vacancy_model import VacancyModel

# model/__init__.py
from .vacancy.vacancy_model import VacancyModel
from .enums import VacancyStatusEnum
```

## 2. Схема

```python
# schema/vacancy/vacancy_schema.py

"""
VacancySchema — схемы для работы с вакансиями.

## Бизнес-контекст
Валидация данных для API операций с вакансиями.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from model.enums import VacancyStatusEnum


class VacancyBaseSchema(BaseModel):
    """Базовые поля вакансии."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Название")
    description: Optional[str] = Field(None, description="Описание")
    requirements: Optional[str] = Field(None, description="Требования")


class VacancyCreateSchema(VacancyBaseSchema):
    """
    Схема создания вакансии.
    
    ## Входные данные
    - title: название (обязательно)
    - description: описание (опционально)
    - requirements: требования (опционально)
    """
    pass


class VacancyUpdateSchema(BaseModel):
    """
    Схема обновления вакансии.
    
    ## Входные данные
    Все поля опциональны.
    """
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    status: Optional[VacancyStatusEnum] = None


class VacancyResponseSchema(VacancyBaseSchema):
    """
    Схема ответа API.
    
    ## Выходные данные
    Полная информация о вакансии.
    """
    
    id: int
    status: VacancyStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Экспорт

```python
# schema/vacancy/__init__.py
from .vacancy_schema import (
    VacancyCreateSchema,
    VacancyUpdateSchema,
    VacancyResponseSchema,
)

# schema/__init__.py
from .vacancy.vacancy_schema import (
    VacancyCreateSchema,
    VacancyUpdateSchema,
    VacancyResponseSchema,
)
```

## 3. Репозиторий

```python
# repository/vacancy/vacancy_repository.py

"""
VacancyRepository — репозиторий вакансий.

## Бизнес-контекст
CRUD операции с таблицей vacancies.

## Зависимости
- VacancyModel: ORM модель
- BaseRepository: базовые операции
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model import VacancyModel, VacancyStatusEnum
from repository.base_repository import BaseRepository


class VacancyRepository(BaseRepository[VacancyModel]):
    """Репозиторий вакансий."""
    
    def __init__(self):
        super().__init__(VacancyModel)
    
    async def get_active(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[VacancyModel]:
        """
        Получить активные вакансии.
        
        ## Выходные данные
        - Список VacancyModel со статусом ACTIVE
        """
        result = await session.execute(
            select(VacancyModel)
            .where(VacancyModel.status == VacancyStatusEnum.ACTIVE)
            .order_by(VacancyModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
```

### Экспорт

```python
# repository/vacancy/__init__.py
from .vacancy_repository import VacancyRepository

# repository/__init__.py
from .vacancy.vacancy_repository import VacancyRepository
```

## 4. Сервис

```python
# service/vacancy/vacancy_service.py

"""
VacancyService — сервис управления вакансиями.

## Бизнес-контекст
Управление жизненным циклом вакансий:
- Создание новых вакансий
- Обновление и закрытие
- Получение списков

## Зависимости
- VacancyRepository: персистенция
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from model import VacancyModel, VacancyStatusEnum
from repository import VacancyRepository
from schema import VacancyCreateSchema, VacancyUpdateSchema
from core.exceptions import NotFoundError


class VacancyService:
    """Сервис вакансий."""
    
    def __init__(self):
        self.repo = VacancyRepository()
    
    async def create(
        self,
        data: VacancyCreateSchema,
        session: AsyncSession,
    ) -> VacancyModel:
        """
        Создать вакансию.
        
        ## Входные данные
        - data: VacancyCreateSchema
        - session: сессия БД
        
        ## Выходные данные
        - VacancyModel
        """
        return await self.repo.create(
            session=session,
            **data.model_dump(),
        )
    
    async def get_by_id(
        self,
        vacancy_id: int,
        session: AsyncSession,
    ) -> VacancyModel:
        """
        Получить вакансию по ID.
        
        ## Исключения
        - NotFoundError: вакансия не найдена
        """
        vacancy = await self.repo.get_by_id(vacancy_id, session)
        if not vacancy:
            raise NotFoundError("Vacancy", vacancy_id)
        return vacancy
    
    async def get_active(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[VacancyModel]:
        """Получить активные вакансии."""
        return await self.repo.get_active(session, limit, offset)
    
    async def close(
        self,
        vacancy_id: int,
        session: AsyncSession,
    ) -> VacancyModel:
        """
        Закрыть вакансию.
        
        ## Бизнес-логика
        Меняет статус на CLOSED.
        """
        vacancy = await self.get_by_id(vacancy_id, session)
        vacancy.status = VacancyStatusEnum.CLOSED
        await session.flush()
        await session.refresh(vacancy)
        return vacancy
```

### Экспорт

```python
# service/vacancy/__init__.py
from .vacancy_service import VacancyService

# service/__init__.py
from .vacancy.vacancy_service import VacancyService
```

## 5. API

### Роутер

```python
# api/v1/endpoints/vacancy/__init__.py

"""
Vacancy Router — роутер для работы с вакансиями.

## Префикс
/api/v1/vacancies
"""

from fastapi import APIRouter

from .get import router as get_router
from .post import router as post_router

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])

router.include_router(get_router)
router.include_router(post_router)
```

### GET endpoints

```python
# api/v1/endpoints/vacancy/get.py

"""
Vacancy GET Endpoints.

## Endpoints
- GET /vacancies — список активных
- GET /vacancies/{id} — детали
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema import VacancyResponseSchema
from service import VacancyService

router = APIRouter()
service = VacancyService()


@router.get(
    "",
    response_model=List[VacancyResponseSchema],
    summary="Получить активные вакансии",
)
async def get_vacancies(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(db_connect.get_session),
):
    vacancies = await service.get_active(session, limit, offset)
    return [VacancyResponseSchema.model_validate(v) for v in vacancies]


@router.get(
    "/{vacancy_id}",
    response_model=VacancyResponseSchema,
    summary="Получить вакансию по ID",
)
async def get_vacancy(
    vacancy_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
):
    vacancy = await service.get_by_id(vacancy_id, session)
    return VacancyResponseSchema.model_validate(vacancy)
```

### POST endpoints

```python
# api/v1/endpoints/vacancy/post.py

"""
Vacancy POST Endpoints.

## Endpoints
- POST /vacancies — создать
- POST /vacancies/{id}/close — закрыть
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema import VacancyCreateSchema, VacancyResponseSchema
from service import VacancyService

router = APIRouter()
service = VacancyService()


@router.post(
    "",
    response_model=VacancyResponseSchema,
    status_code=201,
    summary="Создать вакансию",
)
async def create_vacancy(
    data: VacancyCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
):
    vacancy = await service.create(data, session)
    return VacancyResponseSchema.model_validate(vacancy)


@router.post(
    "/{vacancy_id}/close",
    response_model=VacancyResponseSchema,
    summary="Закрыть вакансию",
)
async def close_vacancy(
    vacancy_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
):
    vacancy = await service.close(vacancy_id, session)
    return VacancyResponseSchema.model_validate(vacancy)
```

### Подключение роутера

```python
# api/v1/endpoints/__init__.py
from .vacancy import router as vacancy_router

# api/v1/include_router.py
from .endpoints import vacancy_router

app.include_router(vacancy_router, prefix="/api/v1")
```

## 6. Миграция

```bash
alembic revision --autogenerate -m "Add vacancies table"
alembic upgrade head
```

---

**Готово!** Сущность Vacancy полностью создана и доступна через API.

[← Назад к оглавлению](README.md)
