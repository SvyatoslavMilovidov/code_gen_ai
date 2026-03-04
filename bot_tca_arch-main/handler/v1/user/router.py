"""
Роутеры для пользовательских виджетов.

Создает роутеры для каждого тега:
- control_router: Управляющие команды
"""

from aiogram import Router

# Роутер для тега control
control_router = Router(name="control")
