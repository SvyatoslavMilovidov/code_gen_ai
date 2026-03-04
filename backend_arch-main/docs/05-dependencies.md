# Слоистая архитектура

[← Назад к оглавлению](README.md)

---

## Иерархия зависимостей

```
API Layer
    ↓ использует
Service Layer
    ↓ использует
Repository Layer
    ↓ использует
Model Layer
    ↓ использует
Core Layer
```

## Правила зависимостей

| Слой | Может использовать | НЕ может использовать |
|------|--------------------|-----------------------|
| **API** | Service, Schema, Core | Repository, Model напрямую |
| **Service** | Repository, Schema, Model, Core, другие Service | API |
| **Repository** | Model, Core | Service, API, Schema |
| **Model** | Core (Base, Enums) | Service, Repository, API |
| **Schema** | Model (только Enums) | Service, Repository |
| **Core** | Ничего из приложения | — |

## Диаграмма зависимостей

```
┌─────────────────────────────────────────────────────┐
│                       API                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ candidate/  │  │  search/    │  │  settings/  │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
└─────────┼────────────────┼────────────────┼─────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────┐
│                     SERVICE                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Candidate   │  │  Search     │  │  Settings   │  │
│  │ Service     │◄─┤ Orchestrator│──►  Service    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                │         │
│         │    ┌───────────┴───────────┐    │         │
│         │    │      Providers        │    │         │
│         │    │ ┌────────┐ ┌────────┐ │    │         │
│         │    │ │LinkedIn│ │   HH   │ │    │         │
│         │    │ └────────┘ └────────┘ │    │         │
│         │    └───────────────────────┘    │         │
└─────────┼────────────────────────────────┼─────────┘
          │                                │
          ▼                                ▼
┌─────────────────────────────────────────────────────┐
│                    REPOSITORY                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Candidate   │  │   Search    │  │  Settings   │  │
│  │ Repository  │  │ Repository  │  │ Repository  │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
└─────────┼────────────────┼────────────────┼─────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────┐
│                      MODEL                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Candidate   │  │   Search    │  │  Settings   │  │
│  │   Model     │  │ TaskModel   │  │   Model     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Примеры правильных и неправильных импортов

### ✅ Правильно

```python
# api/v1/endpoints/candidate/get.py
from service import CandidateService  # API → Service ✅
from schema import CandidateResponseSchema  # API → Schema ✅
from core import db_connect  # API → Core ✅
```

```python
# service/candidate/candidate_service.py
from repository import CandidateRepository  # Service → Repository ✅
from model import CandidateModel  # Service → Model ✅
from schema import CandidateCreateSchema  # Service → Schema ✅
```

```python
# repository/candidate/candidate_repository.py
from model import CandidateModel  # Repository → Model ✅
from core import configs  # Repository → Core ✅
```

### ❌ Неправильно

```python
# api/v1/endpoints/candidate/get.py
from repository import CandidateRepository  # ❌ API → Repository напрямую!
from model import CandidateModel  # ❌ API → Model напрямую!
```

```python
# repository/candidate/candidate_repository.py
from service import CandidateService  # ❌ Repository → Service (обратная зависимость)!
from schema import CandidateSchema  # ❌ Repository → Schema!
```

## Зачем это нужно

### 1. Тестируемость

Каждый слой можно тестировать изолированно, подменяя зависимости.

### 2. Поддерживаемость

Изменения в одном слое не ломают другие.

### 3. Читаемость

Понятно, где искать какую логику.

### 4. Переиспользование

Service можно вызывать из разных API версий, Celery задач и т.д.

---

[Далее: Правила импортов →](06-imports.md)
