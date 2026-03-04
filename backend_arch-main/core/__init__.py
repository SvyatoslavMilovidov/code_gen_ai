"""
Core — ядро приложения.

Экспортирует основные компоненты:
- app: экземпляр FastAPI
- db_connect: менеджер подключения к БД
- configs: конфигурация приложения
"""

from .loader import app, db_connect
from .config import configs

__all__ = [
    "app",
    "db_connect",
    "configs",
]
