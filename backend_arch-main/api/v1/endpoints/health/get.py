"""
Health GET Endpoints — проверка состояния сервиса.

## Endpoints
- GET /health — полная проверка с информацией
- GET /health/live — liveness probe (сервис запущен)
- GET /health/ready — readiness probe (сервис готов принимать трафик)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema import HealthCheckResponseSchema
from service import HealthService

router = APIRouter()
service = HealthService()


@router.get(
    "",
    response_model=HealthCheckResponseSchema,
    summary="Полная проверка состояния",
    description="""
    ## Бизнес-логика
    Проверяет состояние сервиса и всех его зависимостей:
    - Подключение к базе данных
    - Версия приложения
    
    ## Использование
    - Мониторинг состояния сервиса
    - Dashboard и алертинг
    """,
)
async def health_check(
    session: AsyncSession = Depends(db_connect.get_session),
) -> HealthCheckResponseSchema:
    """
    Полная проверка состояния сервиса.
    
    ## Выходные данные
    - HealthCheckResponseSchema с детальной информацией
    """
    return await service.check_health(session)


@router.get(
    "/live",
    summary="Liveness probe",
    description="""
    ## Бизнес-логика
    Простая проверка — сервис запущен и отвечает.
    Не проверяет зависимости.
    
    ## Использование
    - Kubernetes livenessProbe
    - Быстрая проверка доступности
    """,
)
async def liveness() -> dict:
    """
    Liveness probe — сервис жив.
    
    ## Выходные данные
    - {"status": "alive"}
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    response_model=HealthCheckResponseSchema,
    summary="Readiness probe",
    description="""
    ## Бизнес-логика
    Проверяет готовность сервиса принимать трафик:
    - Подключение к БД установлено
    
    ## Использование
    - Kubernetes readinessProbe
    - Балансировщики нагрузки
    """,
)
async def readiness(
    session: AsyncSession = Depends(db_connect.get_session),
) -> HealthCheckResponseSchema:
    """
    Readiness probe — сервис готов.
    
    ## Выходные данные
    - HealthCheckResponseSchema
    
    ## HTTP коды
    - 200: готов
    - 503: не готов (БД недоступна)
    """
    from fastapi import HTTPException
    
    result = await service.check_health(session)
    
    if result.status != "healthy":
        raise HTTPException(status_code=503, detail=result.error)
    
    return result
