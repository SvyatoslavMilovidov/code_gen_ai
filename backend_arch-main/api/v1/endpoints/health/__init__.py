"""
Health Router — роутер для healthcheck.

## Бизнес-контекст
Предоставляет endpoints для проверки состояния сервиса:
- Kubernetes liveness/readiness probes
- Мониторинг и алертинг
- Балансировщики нагрузки

## Endpoints
- GET /health — полная проверка
- GET /health/live — liveness probe (быстрая)
- GET /health/ready — readiness probe (с проверкой БД)
"""

from fastapi import APIRouter

from .get import router as get_router

router = APIRouter(prefix="/health", tags=["Health"])

router.include_router(get_router)
