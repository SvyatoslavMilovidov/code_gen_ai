"""
Include Router — подключение всех роутеров API v1.

## Бизнес-контекст
Централизованное подключение всех ресурсных роутеров
к основному приложению FastAPI.
"""

from core import app
from .endpoints import health_router, users_router

# Health check — без версии в пути (стандарт для k8s/docker)
app.include_router(health_router)

# API v1 endpoints
API_V1_PREFIX = "/api/v1"

app.include_router(users_router, prefix=API_V1_PREFIX)
