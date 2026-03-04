"""
Code для эхо-ответа.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC004

Задача: Подготовить текст для эхо-ответа.

Используется в виджетах:
- handler/v1/user/control/F001/echo_widget.py
"""

from aiogram.fsm.context import FSMContext

from core.vocab import DEFAULT_LANGUAGE


class EchoCode:
    """
    Code для эхо-ответа.

    ## Трассируемость
    Feature: F001
    Scenarios: SC004

    Бизнес-логика:
    1. Получить текст от Trigger
    2. Определить язык пользователя
    3. Подготовить данные для Answer

    Условия роутинга к Answer:
    - всегда → "echo" (EchoAnswer)
    """
    
    async def run(self, trigger_data: dict, state: FSMContext, **kwargs) -> dict:
        """
        Выполнить бизнес-логику и выбрать Answer.
        
        Args:
            trigger_data: Данные от Trigger
            {
                "telegram_id": int - ID пользователя в Telegram,
                "text": str - текст сообщения пользователя,
                "event": Message - оригинальное событие
            }
            state: FSM контекст
            **kwargs: Дополнительные параметры
            
        Returns:
            dict: Название Answer + данные для него
        """
        result = await self._execute_business_logic(trigger_data, state, **kwargs)
        return await self._route_to_answer(result)
    
    async def _execute_business_logic(
        self, 
        trigger_data: dict, 
        state: FSMContext,
        **kwargs
    ) -> dict:
        """
        Выполнить всю бизнес-логику.
        
        Returns:
            dict: Результат обработки
            {
                "telegram_id": int - ID пользователя,
                "text": str - текст для эхо,
                "user_lang": str - язык пользователя
            }
        """
        telegram_id = trigger_data["telegram_id"]
        text = trigger_data["text"]
        user_lang = kwargs.get("user_lang", DEFAULT_LANGUAGE)
        
        return {
            "telegram_id": telegram_id,
            "text": text,
            "user_lang": user_lang,
        }
    
    async def _route_to_answer(self, result: dict) -> dict:
        """
        Определить какой Answer использовать.
        
        Returns:
            dict: Название Answer + данные
        """
        return {"answer_name": "echo", "data": result}
