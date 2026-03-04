"""
Тест SC001 — Новый пользователь: /start → регистрация + приветствие.

## Трассируемость
Feature: F001 — Базовые команды
Scenario: SC001 — Новый пользователь отправляет /start

## BDD
Given: Пользователь не существует в БД (UserAPI возвращает is_new=True)
When:  Отправляет /start
Then:  StartCommandCode вызывает UserAPI, роутит на welcome_new,
       WelcomeAnswer отправляет приветствие для нового пользователя
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_start_code_routes_to_welcome_new(mock_message, mock_state):
    """
    Given: UserAPI.get_or_create возвращает is_new=True.
    When:  StartCommandCode.run вызывается с trigger_data.
    Then:  answer_name == "welcome_new", data содержит is_new=True.
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
        code._user_api.get_or_create = AsyncMock(return_value=({"id": 1}, True))

        result = await code.run(trigger_data, mock_state)

    assert result["answer_name"] == "welcome_new"
    assert result["data"]["is_new"] is True


@pytest.mark.asyncio
async def test_welcome_answer_shows_new_user_text(mock_message):
    """
    Given: data содержит is_new=True.
    When:  WelcomeAnswer.run вызывается.
    Then:  Отправляется сообщение welcome_new.
    """
    from node.control.answer.welcome_answer import WelcomeAnswer
    from core.vocab import MESSAGES

    answer = WelcomeAnswer()
    await answer.run(
        event=mock_message,
        user_lang="ru",
        data={"is_new": True, "telegram_id": 123, "user_lang": "ru"},
    )

    mock_message.answer.assert_called_once_with(text=MESSAGES["welcome_new"]["ru"])
