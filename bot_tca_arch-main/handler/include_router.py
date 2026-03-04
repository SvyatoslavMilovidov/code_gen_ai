"""
Подключение роутеров к диспетчеру.

Регистрирует все роутеры виджетов в основном диспетчере.
"""

from core.loader import dp
from handler.v1.user import control_router

# Импортируем виджеты для регистрации хендлеров
from handler.v1.user import control  # noqa: F401


def include_routers() -> None:
    """
    Подключить все роутеры к диспетчеру.
    
    Вызывается при старте бота для регистрации всех обработчиков.
    """
    dp.include_router(control_router)
