"""
Тест SC003 — Пользователь отправляет /help → справка.

## Трассируемость
Feature: F001 — Базовые команды
Scenario: SC003 — Команда /help

## BDD
Given: Пользователь в любом состоянии
When:  Отправляет /help
Then:  HelpCommandCode роутит на help,
       HelpAnswer отправляет справочное сообщение
"""

import pytest


@pytest.mark.asyncio
async def test_help_code_routes_to_help(mock_message, mock_state):
    """
    Given: Любой пользователь.
    When:  HelpCommandCode.run вызывается.
    Then:  answer_name == "help".
    """
    from node.control.code.help_command_code import HelpCommandCode

    trigger_data = {"telegram_id": 123, "event": mock_message}

    code = HelpCommandCode()
    result = await code.run(trigger_data, mock_state)

    assert result["answer_name"] == "help"


@pytest.mark.asyncio
async def test_help_answer_sends_help_text(mock_message):
    """
    Given: Данные от Code.
    When:  HelpAnswer.run вызывается.
    Then:  Отправляется справочное сообщение.
    """
    from node.control.answer.help_answer import HelpAnswer
    from core.vocab import MESSAGES

    answer = HelpAnswer()
    await answer.run(
        event=mock_message,
        user_lang="ru",
        data={"telegram_id": 123, "user_lang": "ru"},
    )

    mock_message.answer.assert_called_once_with(text=MESSAGES["help"]["ru"])
