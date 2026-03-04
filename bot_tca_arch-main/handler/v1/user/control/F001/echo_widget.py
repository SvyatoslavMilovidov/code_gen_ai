"""
Виджет: Эхо-ответ.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC004

Повторяет текстовое сообщение пользователя.

Доступен из:
1. любое состояние (обрабатывает любой текст)
   - Из какого state: любое (*)
   - Из какого answer: — (текстовое сообщение)

Переводит в:
- Не меняет состояние
"""

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import F

from handler.v1.user.router import control_router

from node.control.trigger import EchoTrigger
from node.control.code import EchoCode
from node.control.answer import EchoAnswer

ANSWER_REGISTRY = {
    "echo": EchoAnswer(),
}


@control_router.message(F.text)
async def handle_echo(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Главный хендлер эхо-ответа.

    ## Трассируемость
    Feature: F001
    Scenarios: SC004

    Архитектура:
    1. EchoTrigger — извлечение текста сообщения
    2. EchoCode — подготовка данных для эхо
    3. EchoAnswer — отправка эхо-ответа
    """
    trigger = EchoTrigger()
    trigger_data = await trigger.run(message, state)

    code = EchoCode()
    code_result = await code.run(trigger_data, state)

    answer = ANSWER_REGISTRY[code_result["answer_name"]]
    await answer.run(
        event=message,
        user_lang="ru",
        data=code_result["data"],
    )
