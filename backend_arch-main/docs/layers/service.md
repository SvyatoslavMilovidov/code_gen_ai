# Слой service/

[← Назад к оглавлению](../README.md)

---

**Назначение:** Бизнес-логика приложения. Оркестрация операций, валидация, интеграции.

## Правила

1. Каждый сервис — отдельный файл с суффиксом `_service.py`
2. Класс сервиса имеет суффикс `Service`
3. Сервис может использовать несколько репозиториев
4. Сервис содержит бизнес-логику, не относящуюся к CRUD
5. Внешние интеграции выносятся в подпапку `providers/`
6. Группировка аналогично model/

## Структура

```
service/
├── __init__.py
│
├── candidate/
│   ├── __init__.py
│   ├── candidate_service.py
│   ├── evaluation_service.py
│   └── validator_service.py      # Валидация через GPT
│
├── search/
│   ├── __init__.py
│   ├── settings_service.py
│   └── orchestrator_service.py   # Координация поиска
│
├── providers/                    # Внешние интеграции
│   ├── __init__.py
│   ├── base_provider.py
│   ├── linkedin_provider.py
│   └── hh_provider.py
│
└── integrations/                 # Другие внешние сервисы
    ├── __init__.py
    ├── gpt_service.py
    └── notification_service.py
```

## Пример сервиса

```python
"""
CandidateService — сервис управления кандидатами.

## Бизнес-контекст
Отвечает за жизненный цикл кандидата:
- Создание с дедупликацией
- Валидация релевантности через GPT
- Управление статусами
- Получение с фильтрацией

## Зависимости
- CandidateRepository: персистенция
- ValidatorService: валидация через GPT
- SearchSettingsRepository: проверка лимитов
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from model import CandidateModel, CandidateStatusEnum, SourceTypeEnum
from repository import CandidateRepository, SearchSettingsRepository
from schema import CandidateCreateSchema, CandidateResponseSchema, CandidateFilterSchema
from .validator_service import ValidatorService


class CandidateService:
    """Сервис управления кандидатами."""
    
    def __init__(self):
        self.repo = CandidateRepository()
        self.settings_repo = SearchSettingsRepository()
        self.validator = ValidatorService()
    
    async def create_candidate(
        self,
        data: CandidateCreateSchema,
        session: AsyncSession,
        skip_validation: bool = False,
    ) -> Optional[CandidateModel]:
        """
        Создать нового кандидата.
        
        ## Входные данные
        - data: данные кандидата (CandidateCreateSchema)
        - session: сессия БД
        - skip_validation: пропустить GPT валидацию
        
        ## Обработка
        1. Проверка дубликата по profile_url
        2. Проверка лимитов настроек поиска
        3. Валидация релевантности через GPT (если не skip)
        4. Сохранение в БД
        
        ## Выходные данные
        - CandidateModel: успешно создан
        - None: дубликат, лимит достигнут, или не прошёл валидацию
        
        ## Исключения
        - ValueError: настройки поиска не найдены
        """
        # 1. Проверка дубликата
        existing = await self.repo.get_by_profile_url(
            str(data.profile_url), session
        )
        if existing:
            return None
        
        # 2. Проверка лимитов
        settings = await self.settings_repo.get_by_id(data.settings_id, session)
        if not settings:
            raise ValueError(f"Настройки поиска {data.settings_id} не найдены")
        
        current_count = await self.repo.count_by_settings(
            data.settings_id, session, status=CandidateStatusEnum.OK
        )
        if current_count >= settings.candidat_need:
            return None
        
        # 3. Валидация через GPT
        if not skip_validation:
            is_valid = await self.validator.validate_candidate(
                candidate_data=data.model_dump(),
                vacancy_description=settings.description,
            )
            if not is_valid:
                return None
        
        # 4. Создание
        candidate = await self.repo.create(
            session=session,
            settings_id=data.settings_id,
            source_type=data.source_type,
            full_name=data.full_name,
            profile_url=str(data.profile_url),
            status=CandidateStatusEnum.OK,
        )
        
        return candidate
    
    async def get_candidates(
        self,
        filters: CandidateFilterSchema,
        session: AsyncSession,
    ) -> List[CandidateResponseSchema]:
        """
        Получить список кандидатов с фильтрацией.
        
        ## Входные данные
        - filters: параметры фильтрации
        - session: сессия БД
        
        ## Обработка
        Применяет фильтры и пагинацию к запросу.
        
        ## Выходные данные
        - Список CandidateResponseSchema
        """
        candidates = await self.repo.get_by_settings(
            settings_id=filters.settings_id,
            session=session,
            status=filters.status,
            source_type=filters.source_type,
            limit=filters.limit,
            offset=filters.offset,
        )
        
        return [
            CandidateResponseSchema.model_validate(c)
            for c in candidates
        ]
    
    async def delete_candidate(
        self,
        candidate_id: int,
        session: AsyncSession,
        hard_delete: bool = False,
    ) -> bool:
        """
        Удалить кандидата.
        
        ## Входные данные
        - candidate_id: ID кандидата
        - session: сессия БД
        - hard_delete: физическое удаление (по умолчанию soft)
        
        ## Обработка
        - soft delete: меняет статус на DELETED
        - hard delete: удаляет запись из БД
        
        ## Выходные данные
        - True: успешно удалён
        - False: не найден
        """
        if hard_delete:
            return await self.repo.delete(candidate_id, session)
        
        candidate = await self.repo.update_status(
            candidate_id, CandidateStatusEnum.DELETED, session
        )
        return candidate is not None
```

## Провайдеры (providers/)

Для внешних интеграций используй паттерн Strategy:

```python
"""
BaseProvider — базовый класс провайдера поиска.

## Бизнес-контекст
Определяет унифицированный интерфейс для всех источников
поиска кандидатов (LinkedIn, HH, и т.д.).

## Паттерн
Strategy Pattern — позволяет менять источник поиска
без изменения клиентского кода.

## Методы для реализации
- start_search: запуск асинхронного поиска
- check_limits: проверка доступных лимитов
- validate_params: валидация параметров запроса
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from model import SourceTypeEnum
from schema import UnifiedSearchRequestSchema, UnifiedSearchResponseSchema


class BaseProvider(ABC):
    """Абстрактный базовый класс провайдера."""
    
    source_type: SourceTypeEnum
    
    @abstractmethod
    async def start_search(
        self,
        request: UnifiedSearchRequestSchema,
        session: AsyncSession,
    ) -> UnifiedSearchResponseSchema:
        """
        Запустить асинхронный поиск.
        
        ## Входные данные
        - request: унифицированный запрос на поиск
        - session: сессия БД
        
        ## Выходные данные
        - UnifiedSearchResponseSchema с external_run_id
        """
        pass
    
    async def check_limits(
        self,
        session: AsyncSession,
        provider_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Проверить доступность лимитов.
        
        ## Выходные данные
        - available: bool
        - remaining: int (-1 = unlimited)
        - message: str
        """
        return {
            "available": True,
            "remaining": -1,
            "message": "Limits not implemented",
        }
```

## Что должно быть в сервисе

✅ Бизнес-логика:
- Валидация бизнес-правил
- Оркестрация нескольких репозиториев
- Вызов внешних сервисов
- Преобразование данных

❌ Что НЕ должно быть:
- SQL запросы (это repository)
- HTTP обработка (это api)
- Прямой доступ к БД без репозитория

---

[Далее: Слой api/ →](api.md)
