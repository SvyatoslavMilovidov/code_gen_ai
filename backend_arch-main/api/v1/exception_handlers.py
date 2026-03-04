"""
Exception Handlers — обработчики исключений для API.

## Бизнес-контекст
Преобразует бизнес-исключения в HTTP ответы.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Обработчик бизнес-исключений.
    
    ## Входные данные
    - request: HTTP запрос
    - exc: исключение AppException
    
    ## Обработка
    Маппинг кодов ошибок на HTTP статусы.
    
    ## Выходные данные
    - JSONResponse с кодом и сообщением ошибки
    """
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


def register_exception_handlers(app):
    """Зарегистрировать все обработчики исключений."""
    app.add_exception_handler(AppException, app_exception_handler)
