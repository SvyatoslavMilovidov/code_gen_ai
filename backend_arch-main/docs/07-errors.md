# Обработка ошибок

[← Назад к оглавлению](README.md)

---

## Иерархия исключений

```python
# core/exceptions.py

class AppException(Exception):
    """Базовое исключение приложения."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppException):
    """Ресурс не найден."""
    
    def __init__(self, resource: str, id: int):
        super().__init__(
            message=f"{resource} с ID {id} не найден",
            code="NOT_FOUND",
        )


class ValidationError(AppException):
    """Ошибка валидации."""
    
    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR")


class ExternalServiceError(AppException):
    """Ошибка внешнего сервиса."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"Ошибка {service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
        )


class LimitExceededError(AppException):
    """Превышен лимит."""
    
    def __init__(self, resource: str, limit: int):
        super().__init__(
            message=f"Превышен лимит {resource}: {limit}",
            code="LIMIT_EXCEEDED",
        )
```

## Обработчики в API

```python
# api/v1/exception_handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    """Обработчик бизнес-исключений."""
    
    status_codes = {
        "NOT_FOUND": 404,
        "VALIDATION_ERROR": 400,
        "LIMIT_EXCEEDED": 429,
        "EXTERNAL_SERVICE_ERROR": 502,
    }
    
    return JSONResponse(
        status_code=status_codes.get(exc.code, 500),
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )
```

## Регистрация обработчиков

```python
# core/loader.py

from fastapi import FastAPI
from core.exceptions import AppException
from api.v1.exception_handlers import app_exception_handler

app = FastAPI(...)

app.add_exception_handler(AppException, app_exception_handler)
```

## Использование в сервисах

```python
# service/candidate/candidate_service.py

from core.exceptions import NotFoundError, LimitExceededError


class CandidateService:
    
    async def get_by_id(
        self,
        candidate_id: int,
        session: AsyncSession,
    ) -> CandidateModel:
        """Получить кандидата по ID."""
        
        candidate = await self.repo.get_by_id(candidate_id, session)
        
        if not candidate:
            raise NotFoundError("Candidate", candidate_id)
        
        return candidate
    
    async def create_candidate(
        self,
        data: CandidateCreateSchema,
        session: AsyncSession,
    ) -> CandidateModel:
        """Создать кандидата."""
        
        # Проверка лимита
        current_count = await self.repo.count_by_settings(
            data.settings_id, session
        )
        settings = await self.settings_repo.get_by_id(
            data.settings_id, session
        )
        
        if current_count >= settings.candidat_need:
            raise LimitExceededError("candidates", settings.candidat_need)
        
        # ... создание
```

## Формат ответа об ошибке

```json
{
    "error": {
        "code": "NOT_FOUND",
        "message": "Candidate с ID 123 не найден"
    }
}
```

## Таблица HTTP кодов

| Код ошибки | HTTP статус | Описание |
|------------|-------------|----------|
| `NOT_FOUND` | 404 | Ресурс не найден |
| `VALIDATION_ERROR` | 400 | Ошибка валидации входных данных |
| `LIMIT_EXCEEDED` | 429 | Превышен лимит |
| `EXTERNAL_SERVICE_ERROR` | 502 | Ошибка внешнего сервиса |
| `UNKNOWN_ERROR` | 500 | Неизвестная ошибка |

## Правила

### 1. Бросай исключения в Service

```python
# ✅ Правильно — исключение в сервисе
class CandidateService:
    async def get_by_id(self, id, session):
        candidate = await self.repo.get_by_id(id, session)
        if not candidate:
            raise NotFoundError("Candidate", id)
        return candidate
```

### 2. Не бросай HTTPException в Service

```python
# ❌ Неправильно — HTTPException в сервисе
from fastapi import HTTPException

class CandidateService:
    async def get_by_id(self, id, session):
        candidate = await self.repo.get_by_id(id, session)
        if not candidate:
            raise HTTPException(404)  # ❌ Привязка к HTTP!
```

### 3. API преобразует исключения

```python
# api/v1/endpoints/candidate/get.py

@router.get("/{id}")
async def get_candidate(id: int, session: AsyncSession = Depends(...)):
    # Исключение NotFoundError автоматически преобразуется в 404
    # благодаря зарегистрированному обработчику
    return await service.get_by_id(id, session)
```

---

[Далее: API версионирование →](08-api-versioning.md)
