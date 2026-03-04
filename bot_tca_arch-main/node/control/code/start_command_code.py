"""
Code для команды /start.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

Задача: Зарегистрировать пользователя через бэкенд API
и подготовить данные для приветственного сообщения.

Используется в виджетах:
- handler/v1/user/control/F001/start_command_widget.py
"""

import logging

from aiogram.fsm.context import FSMContext

from core.vocab import DEFAULT_LANGUAGE
from service.api import UserAPI

logger = logging.getLogger(__name__)


class StartCommandCode:
    """
    Code для команды /start.

    ## Трассируемость
    Feature: F001
    Scenarios: SC001, SC002

    Бизнес-логика:
    1. Получить данные от Trigger
    2. Вызвать UserAPI.get_or_create (регистрация через бэкенд)
    3. Роутинг: новый → welcome_new, существующий → welcome_back

    Используемые сервисы:
    - UserAPI (service/api/user_api.py)

    Условия роутинга к Answer:
    - SC001: is_new=True  → "welcome_new"
    - SC002: is_new=False → "welcome_back"
    """

    def __init__(self):
        self._user_api = UserAPI()

    async def run(self, trigger_data: dict, state: FSMContext, **kwargs) -> dict:
        """
        Выполнить бизнес-логику и выбрать Answer.

        Args:
            trigger_data: Данные от Trigger
            state: FSM контекст

        Returns:
            dict: {answer_name, data}
        """
        result = await self._execute_business_logic(trigger_data, state, **kwargs)
        return await self._route_to_answer(result)

    async def _execute_business_logic(
        self,
        trigger_data: dict,
        state: FSMContext,
        **kwargs,
    ) -> dict:
        telegram_id = trigger_data["telegram_id"]
        username = trigger_data.get("username")
        user_lang = kwargs.get("user_lang", DEFAULT_LANGUAGE)

        is_new = False
        try:
            _user_data, is_new = await self._user_api.get_or_create(
                telegram_id=telegram_id,
                username=username,
            )
        except Exception:
            logger.exception("UserAPI.get_or_create failed for tg_id=%s", telegram_id)

        return {
            "telegram_id": telegram_id,
            "user_lang": user_lang,
            "is_new": is_new,
        }

    async def _route_to_answer(self, result: dict) -> dict:
        answer_name = "welcome_new" if result["is_new"] else "welcome_back"
        return {"answer_name": answer_name, "data": result}
