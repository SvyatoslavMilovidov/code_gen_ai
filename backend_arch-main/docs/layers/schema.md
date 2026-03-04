# Слой schema/

[← Назад к оглавлению](../README.md)

---

**Назначение:** Pydantic схемы для валидации входных/выходных данных API.

## Правила

1. Каждая схема — отдельный файл с суффиксом `_schema.py`
2. Классы схем имеют суффиксы по назначению:
   - `Create` — для создания (POST)
   - `Update` — для обновления (PUT/PATCH)
   - `Response` — для ответа API
   - `Filter` — для фильтрации (query params)
   - `Base` — базовая схема с общими полями
3. Группировка по сущностям аналогично model/
4. Базовые схемы выносятся в `base_schema.py`

## Структура

```
schema/
├── __init__.py
├── base_schema.py           # Базовые схемы
│
├── candidate/
│   ├── __init__.py
│   ├── candidate_schema.py
│   └── evaluation_schema.py
│
└── search/
    ├── __init__.py
    └── settings_schema.py
```

## Суффиксы схем

| Суффикс | Назначение | HTTP метод |
|---------|------------|------------|
| `CreateSchema` | Создание ресурса | POST |
| `UpdateSchema` | Обновление (все поля опциональны) | PUT/PATCH |
| `ResponseSchema` | Ответ API | GET, POST, PUT |
| `FilterSchema` | Query параметры | GET (list) |
| `BaseSchema` | Общие поля | — |

## Пример схемы

```python
"""
CandidateSchema — схемы для работы с кандидатами.

## Бизнес-контекст
Определяет структуры данных для API операций с кандидатами:
создание, обновление, отображение.

## Схемы
- CandidateCreateSchema: создание нового кандидата
- CandidateUpdateSchema: обновление существующего
- CandidateResponseSchema: ответ API
- CandidateFilterSchema: фильтрация списка
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from model.enums import CandidateStatusEnum, SourceTypeEnum


class CandidateBaseSchema(BaseModel):
    """Базовые поля кандидата."""
    
    full_name: str = Field(..., min_length=1, max_length=255, description="ФИО кандидата")
    profile_url: HttpUrl = Field(..., description="Ссылка на профиль")
    source_type: SourceTypeEnum = Field(..., description="Источник")


class CandidateCreateSchema(CandidateBaseSchema):
    """
    Схема создания кандидата.
    
    ## Входные данные
    - settings_id: ID настроек поиска (обязательно)
    - full_name: ФИО (обязательно)
    - profile_url: URL профиля (обязательно, уникальный)
    - source_type: источник (обязательно)
    
    ## Валидация
    - profile_url должен быть валидным URL
    - full_name от 1 до 255 символов
    """
    
    settings_id: int = Field(..., gt=0, description="ID настроек поиска")


class CandidateUpdateSchema(BaseModel):
    """
    Схема обновления кандидата.
    
    ## Входные данные
    Все поля опциональны — обновляются только переданные.
    
    - status: новый статус
    - full_name: обновлённое ФИО
    """
    
    status: Optional[CandidateStatusEnum] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)


class CandidateResponseSchema(CandidateBaseSchema):
    """
    Схема ответа API для кандидата.
    
    ## Выходные данные
    Полная информация о кандидате включая:
    - Все базовые поля
    - ID и временные метки
    - Текущий статус
    """
    
    id: int
    settings_id: int
    status: CandidateStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CandidateFilterSchema(BaseModel):
    """
    Схема фильтрации списка кандидатов.
    
    ## Входные данные (query params)
    - settings_id: фильтр по настройкам поиска
    - status: фильтр по статусу
    - source_type: фильтр по источнику
    - limit/offset: пагинация
    """
    
    settings_id: Optional[int] = None
    status: Optional[CandidateStatusEnum] = None
    source_type: Optional[SourceTypeEnum] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
```

## Валидация полей

Используй встроенные валидаторы Pydantic:

```python
from pydantic import Field, HttpUrl, EmailStr, validator

class ExampleSchema(BaseModel):
    # Числа с ограничениями
    age: int = Field(..., ge=0, le=120)
    
    # Строки с длиной
    name: str = Field(..., min_length=1, max_length=255)
    
    # URL и Email
    website: HttpUrl
    email: EmailStr
    
    # Кастомный валидатор
    @validator("name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()
```

## Config для ORM

Для схем ответа добавляй `from_attributes`:

```python
class ResponseSchema(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True  # Позволяет создавать из ORM модели
```

---

[Далее: Слой repository/ →](repository.md)
