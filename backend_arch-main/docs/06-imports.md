# Правила импортов

[← Назад к оглавлению](README.md)

---

## Абсолютные vs относительные

| Контекст | Тип импорта | Пример |
|----------|-------------|--------|
| Между разделами | Абсолютные | `from model import CandidateModel` |
| Внутри раздела | Относительные | `from .validator_service import ValidatorService` |

### Пример

```python
# service/candidate/candidate_service.py

# Абсолютные — из других разделов
from model import CandidateModel, CandidateStatusEnum
from repository import CandidateRepository
from schema import CandidateCreateSchema

# Относительные — из того же раздела
from .validator_service import ValidatorService
```

## Порядок импортов

```python
# 1. Стандартная библиотека
from typing import List, Optional
from datetime import datetime

# 2. Сторонние библиотеки
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Локальные модули (абсолютные)
from model import CandidateModel
from repository import CandidateRepository
from service import CandidateService

# 4. Локальные модули (относительные)
from .utils import format_response
```

## __init__.py для экспорта

Каждый раздел имеет `__init__.py` для удобного импорта:

```python
# repository/__init__.py

from .candidate.candidate_repository import CandidateRepository
from .candidate.evaluation_repository import EvaluationRepository
from .search.settings_repository import SearchSettingsRepository

__all__ = [
    "CandidateRepository",
    "EvaluationRepository",
    "SearchSettingsRepository",
]
```

### Преимущество

Можно импортировать короче:

```python
# ✅ Короткий импорт
from repository import CandidateRepository

# ❌ Длинный импорт (без __init__.py)
from repository.candidate.candidate_repository import CandidateRepository
```

## Пример __init__.py для разных слоёв

### model/__init__.py

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

### service/__init__.py

```python
"""
Service — бизнес-логика приложения.
"""

from .candidate.candidate_service import CandidateService
from .candidate.evaluation_service import EvaluationService
from .search.settings_service import SearchSettingsService
from .search.orchestrator_service import SearchOrchestrator

__all__ = [
    "CandidateService",
    "EvaluationService",
    "SearchSettingsService",
    "SearchOrchestrator",
]
```

### api/v1/endpoints/__init__.py

```python
"""
Endpoints — HTTP роутеры для API v1.
"""

from .candidate import router as candidate_router
from .search import router as search_router
from .settings import router as settings_router

__all__ = [
    "candidate_router",
    "search_router",
    "settings_router",
]
```

## Циклические импорты

### Проблема

```python
# service/a_service.py
from service.b_service import BService  # Импорт B

# service/b_service.py
from service.a_service import AService  # Импорт A — циклическая зависимость!
```

### Решения

**1. Ленивый импорт:**

```python
# service/a_service.py
class AService:
    def method(self):
        from service.b_service import BService  # Импорт внутри метода
        return BService().do_something()
```

**2. Dependency Injection:**

```python
# service/a_service.py
class AService:
    def __init__(self, b_service=None):
        self.b_service = b_service or BService()
```

**3. Вынести общую логику:**

```python
# service/common/shared_logic.py — общий модуль
# service/a_service.py — импортирует shared_logic
# service/b_service.py — импортирует shared_logic
```

---

[Далее: Обработка ошибок →](07-errors.md)
