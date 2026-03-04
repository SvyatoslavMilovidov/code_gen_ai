# Слой model/

[← Назад к оглавлению](../README.md)

---

**Назначение:** ORM модели SQLAlchemy, представляющие таблицы в базе данных.

## Правила

1. Каждая модель — отдельный файл с суффиксом `_model.py`
2. Класс модели имеет суффикс `Model` (например, `CandidateModel`)
3. Связанные модели группируются в подпапки по сущностям
4. Базовая модель `BaseModel` содержит общие поля (id, created_at, updated_at)
5. Перечисления (Enum) выносятся в `enums.py`

## Структура

```
model/
├── __init__.py              # Экспорт всех моделей
├── base_model.py            # Базовая модель
├── enums.py                 # Все перечисления
│
├── candidate/               # Группа по сущности
│   ├── __init__.py         # Экспорт моделей группы
│   ├── candidate_model.py  # Основная модель
│   └── evaluation_model.py # Связанная модель
│
└── search/
    ├── __init__.py
    ├── settings_model.py
    └── task_model.py
```

## Пример base_model.py

```python
"""
BaseModel — базовый класс для всех ORM моделей.

## Бизнес-контекст
Определяет общие поля и поведение для всех сущностей:
автоматические временные метки, стандартный первичный ключ.

## Выходные данные
- Base: декларативная база SQLAlchemy
- BaseModel: миксин с общими полями
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel:
    """Миксин с общими полями для всех моделей."""
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Пример модели

```python
"""
CandidateModel — модель кандидата.

## Бизнес-контекст
Представляет кандидата, найденного через один из источников поиска.
Хранит профильные данные и связь с настройками поиска.

## Поля
- settings_id: привязка к поисковому запросу
- source_type: источник (LinkedIn, HH)
- full_name: ФИО кандидата
- profile_url: ссылка на профиль
- status: статус обработки (OK, DELETED, RESERVE)

## Связи
- settings: SearchSettingsModel (Many-to-One)
- evaluations: List[EvaluationModel] (One-to-Many)
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from model.base_model import Base, BaseModel
from model.enums import CandidateStatusEnum, SourceTypeEnum


class CandidateModel(Base, BaseModel):
    __tablename__ = "candidates"
    
    settings_id = Column(Integer, ForeignKey("search_settings.id"), nullable=False)
    source_type = Column(Enum(SourceTypeEnum), nullable=False)
    full_name = Column(String(255), nullable=False)
    profile_url = Column(String(500), unique=True, nullable=False)
    status = Column(Enum(CandidateStatusEnum), default=CandidateStatusEnum.OK)
    
    # Relationships
    settings = relationship("SearchSettingsModel", back_populates="candidates")
    evaluations = relationship("EvaluationModel", back_populates="candidate")
```

## Пример enums.py

```python
"""
Enums — перечисления для всех моделей.

## Бизнес-контекст
Централизованное хранение всех статусов и типов,
используемых в моделях данных.
"""

from enum import Enum


class CandidateStatusEnum(str, Enum):
    """Статус кандидата в системе."""
    
    OK = "OK"              # Активный кандидат
    DELETED = "DELETED"    # Удалён пользователем
    RESERVE = "RESERVE"    # В резерве (не показывается)


class SourceTypeEnum(str, Enum):
    """Источник поиска кандидата."""
    
    LINKEDIN = "LINKEDIN"
    HH = "HH"


class TaskStatusEnum(str, Enum):
    """Статус фоновой задачи."""
    
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```

## Пример __init__.py

```python
"""
Model — ORM модели приложения.

Экспортирует все модели для удобного импорта:
    from model import CandidateModel, SearchSettingsModel
"""

from .base_model import Base, BaseModel
from .enums import CandidateStatusEnum, SourceTypeEnum, TaskStatusEnum

from .candidate.candidate_model import CandidateModel
from .candidate.evaluation_model import EvaluationModel
from .search.settings_model import SearchSettingsModel
from .search.task_model import SearchTaskModel

__all__ = [
    "Base",
    "BaseModel",
    "CandidateStatusEnum",
    "SourceTypeEnum",
    "TaskStatusEnum",
    "CandidateModel",
    "EvaluationModel",
    "SearchSettingsModel",
    "SearchTaskModel",
]
```

## Документирование модели

Обязательные секции в docstring:

| Секция | Описание |
|--------|----------|
| **Бизнес-контекст** | Что представляет модель в бизнес-терминах |
| **Поля** | Список полей с описанием |
| **Связи** | Relationships с другими моделями |

---

[Далее: Слой schema/ →](schema.md)
