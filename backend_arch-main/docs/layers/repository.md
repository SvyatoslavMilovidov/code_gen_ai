# Слой repository/

[← Назад к оглавлению](../README.md)

---

**Назначение:** Слой доступа к данным. Инкапсулирует все операции с БД.

## Правила

1. Каждый репозиторий — отдельный файл с суффиксом `_repository.py`
2. Класс репозитория имеет суффикс `Repository`
3. Репозиторий работает только с одной моделью (или тесно связанными)
4. Методы — чистые CRUD операции, **без бизнес-логики**
5. Все методы принимают `session: AsyncSession` как параметр
6. Группировка аналогично model/

## Структура

```
repository/
├── __init__.py
├── base_repository.py       # Базовый репозиторий с общими методами
│
├── candidate/
│   ├── __init__.py
│   ├── candidate_repository.py
│   └── evaluation_repository.py
│
└── search/
    ├── __init__.py
    └── settings_repository.py
```

## Пример base_repository.py

```python
"""
BaseRepository — базовый класс репозитория.

## Бизнес-контекст
Предоставляет стандартные CRUD операции для всех репозиториев.
Использует Generic для типизации модели.

## Методы
- get_by_id: получение по ID
- get_all: получение списка с пагинацией
- create: создание записи
- update: обновление записи
- delete: удаление записи
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD операциями."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get_by_id(
        self,
        id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """
        Получить запись по ID.
        
        ## Входные данные
        - id: идентификатор записи
        - session: сессия БД
        
        ## Выходные данные
        - Модель или None если не найдена
        """
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ModelType]:
        """
        Получить список записей с пагинацией.
        
        ## Входные данные
        - session: сессия БД
        - limit: максимум записей (по умолчанию 50)
        - offset: смещение (по умолчанию 0)
        
        ## Выходные данные
        - Список моделей
        """
        result = await session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
    
    async def create(
        self,
        session: AsyncSession,
        **kwargs,
    ) -> ModelType:
        """
        Создать новую запись.
        
        ## Входные данные
        - session: сессия БД
        - **kwargs: поля модели
        
        ## Обработка
        1. Создание экземпляра модели
        2. Добавление в сессию
        3. Flush для получения ID
        4. Refresh для актуальных данных
        
        ## Выходные данные
        - Созданная модель с ID
        """
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance
    
    async def delete(
        self,
        id: int,
        session: AsyncSession,
    ) -> bool:
        """
        Удалить запись по ID.
        
        ## Входные данные
        - id: идентификатор записи
        - session: сессия БД
        
        ## Выходные данные
        - True если удалено, False если не найдено
        """
        result = await session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0
```

## Пример конкретного репозитория

```python
"""
CandidateRepository — репозиторий для работы с кандидатами.

## Бизнес-контекст
Инкапсулирует все операции с таблицей candidates.
Предоставляет специфичные для кандидатов методы поиска и фильтрации.

## Зависимости
- CandidateModel: ORM модель
- BaseRepository: базовые CRUD операции
"""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from model import CandidateModel, CandidateStatusEnum, SourceTypeEnum
from .base_repository import BaseRepository


class CandidateRepository(BaseRepository[CandidateModel]):
    """Репозиторий кандидатов."""
    
    def __init__(self):
        super().__init__(CandidateModel)
    
    async def get_by_profile_url(
        self,
        profile_url: str,
        session: AsyncSession,
    ) -> Optional[CandidateModel]:
        """
        Найти кандидата по URL профиля.
        
        ## Входные данные
        - profile_url: URL профиля (уникальный)
        - session: сессия БД
        
        ## Бизнес-логика
        Используется для дедупликации — проверки существования
        кандидата перед добавлением.
        
        ## Выходные данные
        - CandidateModel или None
        """
        result = await session.execute(
            select(CandidateModel).where(
                CandidateModel.profile_url == profile_url
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_settings(
        self,
        settings_id: int,
        session: AsyncSession,
        status: Optional[CandidateStatusEnum] = None,
        source_type: Optional[SourceTypeEnum] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CandidateModel]:
        """
        Получить кандидатов по настройкам поиска с фильтрацией.
        
        ## Входные данные
        - settings_id: ID настроек поиска
        - session: сессия БД
        - status: фильтр по статусу (опционально)
        - source_type: фильтр по источнику (опционально)
        - limit/offset: пагинация
        
        ## Выходные данные
        - Список CandidateModel
        """
        conditions = [CandidateModel.settings_id == settings_id]
        
        if status:
            conditions.append(CandidateModel.status == status)
        if source_type:
            conditions.append(CandidateModel.source_type == source_type)
        
        result = await session.execute(
            select(CandidateModel)
            .where(and_(*conditions))
            .order_by(CandidateModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def count_by_settings(
        self,
        settings_id: int,
        session: AsyncSession,
        status: Optional[CandidateStatusEnum] = None,
    ) -> int:
        """
        Подсчитать кандидатов по настройкам.
        
        ## Входные данные
        - settings_id: ID настроек поиска
        - session: сессия БД
        - status: фильтр по статусу (опционально)
        
        ## Выходные данные
        - Количество кандидатов (int)
        """
        from sqlalchemy import func
        
        conditions = [CandidateModel.settings_id == settings_id]
        if status:
            conditions.append(CandidateModel.status == status)
        
        result = await session.execute(
            select(func.count(CandidateModel.id)).where(and_(*conditions))
        )
        return result.scalar() or 0
```

## Что НЕ должно быть в репозитории

❌ Бизнес-логика:
```python
# НЕПРАВИЛЬНО — это бизнес-логика
async def create_if_not_exists(self, data, session):
    existing = await self.get_by_url(data.url, session)
    if existing:
        return None  # Бизнес-решение!
    return await self.create(session, **data)
```

✅ Правильно — только CRUD:
```python
# ПРАВИЛЬНО — репозиторий
async def get_by_url(self, url, session):
    ...

async def create(self, session, **kwargs):
    ...

# Бизнес-логика в Service
async def create_candidate(self, data, session):
    existing = await self.repo.get_by_url(data.url, session)
    if existing:
        return None
    return await self.repo.create(session, **data)
```

---

[Далее: Слой service/ →](service.md)
