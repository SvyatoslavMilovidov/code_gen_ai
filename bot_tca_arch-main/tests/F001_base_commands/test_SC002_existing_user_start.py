"""
Тест SC002 — Существующий пользователь: /start → приветствие (без дубликата).

## Трассируемость
Feature: F001 — Базовые команды
Scenario: SC002 — Существующий пользователь отправляет /start

## BDD
Given: Пользователь уже существует в БД (UserAPI возвращает is_new=False)
When:  Отправляет /start
Then:  StartCommandCode роутит на welcome_back,
       WelcomeAnswer отправляет приветствие для существующего пользователя
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_start_code_routes_to_welcome_back(mock_message, mock_state):
    """
    Given: UserAPI.get_or_create возвращает is_new=False.
    When:  StartCommandCode.run вызывается.
    Then:  answer_name == "welcome_back", data содержит is_new=False.
    """
    from node.control.code.start_command_code import StartCommandCode

    trigger_data = {
        "telegram_id": 123,
        "username": "testuser",
        "event": mock_message,
    }

    with patch.object(
        StartCommandCode,
        "__init__",
        lambda self: setattr(self, "_user_api", AsyncMock()) or None,
    ):
        code = StartCommandCode()
        code._user_api.get_or_create = AsyncMock(return_value=({"id": 1}, False))

        result = await code.run(trigger_data, mock_state)

    assert result["answer_name"] == "welcome_back"
    assert result["data"]["is_new"] is False


@pytest.mark.asyncio
async def test_welcome_answer_shows_existing_user_text(mock_message):
    """
    Given: data содержит is_new=False.
    When:  WelcomeAnswer.run вызывается.
    Then:  Отправляется сообщение welcome_back.
    """
    from node.control.answer.welcome_answer import WelcomeAnswer
    from core.vocab import MESSAGES

    answer = WelcomeAnswer()
    await answer.run(
        event=mock_message,
        user_lang="ru",
        data={"is_new": False, "telegram_id": 123, "user_lang": "ru"},
    )

    mock_message.answer.assert_called_once_with(text=MESSAGES["welcome_back"]["ru"])
