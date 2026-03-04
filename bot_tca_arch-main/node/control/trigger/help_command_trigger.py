"""
Trigger для команды /help.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC003

Используется в виджетах:
- handler/v1/user/control/F001/help_command_widget.py
"""

from aiogram.types import Message
from aiogram.fsm.context import FSMContext


class HelpCommandTrigger:
    """
    Trigger для обработки команды /help.

    ## Трассируемость
    Feature: F001
    Scenarios: SC003

    Выполняет визуальные операции:
    - Извлечение базовых данных пользователя
    """
    
    async def run(self, event: Message, state: FSMContext) -> dict:
        """
        Выполнить визуальные операции.
        
        Args:
            event: Message событие от Telegram
            state: FSM контекст
            
        Returns:
            dict: Данные для передачи в Code
            {
                "telegram_id": int - ID пользователя в Telegram,
                "event": Message - оригинальное событие
            }
        """
        telegram_id = event.from_user.id
        
        return {
            "telegram_id": telegram_id,
            "event": event,
        }
