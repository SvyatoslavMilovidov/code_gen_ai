"""
HealthSchema — схемы для healthcheck endpoint.

## Бизнес-контекст
Определяет структуру ответа для проверки состояния сервиса.
Используется для мониторинга и балансировщиков нагрузки.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheckResponseSchema(BaseModel):
    """
    Схема ответа healthcheck.

    ## Выходные данные
    - status: статус сервиса (healthy/unhealthy)
    - version: версия приложения
    - timestamp: время проверки
    - database: статус подключения к БД
    """

    status: str = Field(..., description="Статус сервиса", examples=["healthy"])
    version: str = Field(..., description="Версия приложения", examples=["1.0.0"])
    timestamp: datetime = Field(..., description="Время проверки")
    database: str = Field(..., description="Статус БД", examples=["connected"])
    error: Optional[str] = Field(None, description="Сообщение об ошибке")
