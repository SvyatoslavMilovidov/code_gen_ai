"""
API — HTTP endpoints приложения.

Экспортирует app для использования в main.py
"""

from core import app
from .v1 import include_router  # noqa: F401 — подключает роутеры
from .v1.exception_handlers import register_exception_handlers

register_exception_handlers(app)

__all__ = [
    "app",
]
