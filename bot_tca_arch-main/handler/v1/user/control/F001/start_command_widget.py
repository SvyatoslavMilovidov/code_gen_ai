"""
Виджет: Команда /start.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001 (новый пользователь), SC002 (существующий пользователь)

Точка входа в бота. Регистрирует пользователя через бэкенд API
и показывает приветственное сообщение.

Доступен из:
1. entry (команда /start)
   - Из какого state: любое (*)
   - Из какого answer: — (команда)

Переводит в:
- Остается в idle состоянии
"""

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handler.v1.user.router import control_router
from core.vocab import COMMANDS

from node.control.trigger import StartCommandTrigger
from node.control.code import StartCommandCode
from node.control.answer import WelcomeAnswer

ANSWER_REGISTRY = {
    "welcome_new": WelcomeAnswer(),   # SC001 — новый пользователь
    "welcome_back": WelcomeAnswer(),  # SC002 — существующий пользователь
}


@control_router.message(Command(COMMANDS["start"]))
async def handle_start_command(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Главный хендлер команды /start.

    ## Трассируемость
    Feature: F001
    Scenarios: SC001, SC002

    Архитектура:
    1. StartCommandTrigger — сброс FSM, извлечение данных
    2. StartCommandCode — вызов UserAPI.get_or_create
    3. WelcomeAnswer — отображение приветствия (разное для нового/существующего)
    """
    trigger = StartCommandTrigger()
    trigger_data = await trigger.run(message, state)

    code = StartCommandCode()
    code_result = await code.run(trigger_data, state)

    answer = ANSWER_REGISTRY[code_result["answer_name"]]
    await answer.run(
        event=message,
        user_lang="ru",
        data=code_result["data"],
    )
