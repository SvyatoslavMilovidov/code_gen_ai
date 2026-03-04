"""
Пользовательские виджеты.

Теги:
- control: Управляющие команды (/start, /help, эхо)
"""

from handler.v1.user.router import control_router

__all__ = ["control_router"]
