"""
Виджет: Команда /help.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC003

Показывает справочную информацию о боте.

Доступен из:
1. любое состояние (команда /help доступна всегда)
   - Из какого state: любое (*)
   - Из какого answer: — (команда)

Переводит в:
- Не меняет состояние
"""

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handler.v1.user.router import control_router
from core.vocab import COMMANDS

from node.control.trigger import HelpCommandTrigger
from node.control.code import HelpCommandCode
from node.control.answer import HelpAnswer

ANSWER_REGISTRY = {
    "help": HelpAnswer(),
}


@control_router.message(Command(COMMANDS["help"]))
async def handle_help_command(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Главный хендлер команды /help.

    ## Трассируемость
    Feature: F001
    Scenarios: SC003

    Архитектура:
    1. HelpCommandTrigger — извлечение данных
    2. HelpCommandCode — подготовка данных
    3. HelpAnswer — отображение справки
    """
    trigger = HelpCommandTrigger()
    trigger_data = await trigger.run(message, state)

    code = HelpCommandCode()
    code_result = await code.run(trigger_data, state)

    answer = ANSWER_REGISTRY[code_result["answer_name"]]
    await answer.run(
        event=message,
        user_lang="ru",
        data=code_result["data"],
    )
