"""
Exceptions — базовые исключения приложения.

## Бизнес-контекст
Иерархия исключений для бизнес-ошибок.
Преобразуются в HTTP ответы через exception handlers.
"""


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
