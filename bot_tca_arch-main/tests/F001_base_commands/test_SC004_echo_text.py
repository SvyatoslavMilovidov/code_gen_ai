"""
Тест SC004 — Пользователь отправляет текст → эхо-ответ.

## Трассируемость
Feature: F001 — Базовые команды
Scenario: SC004 — Эхо-ответ на текстовое сообщение

## BDD
Given: Пользователь в любом состоянии
When:  Отправляет текстовое сообщение
Then:  EchoCode роутит на echo,
       EchoAnswer отправляет эхо с префиксом
"""

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text",
    ["Привет!", "Hello world", "12345"],
    ids=["cyrillic", "latin", "numbers"],
)
async def test_echo_code_routes_to_echo(mock_message, mock_state, text: str):
    """
    Given: Пользователь отправляет текст.
    When:  EchoCode.run вызывается.
    Then:  answer_name == "echo", data содержит текст пользователя.
    """
    from node.control.code.echo_code import EchoCode

    trigger_data = {"telegram_id": 123, "text": text, "event": mock_message}

    code = EchoCode()
    result = await code.run(trigger_data, mock_state)

    assert result["answer_name"] == "echo"
    assert result["data"]["text"] == text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, lang, expected_prefix",
    [
        ("Привет!", "ru", "🔊 Эхо: "),
        ("Hello!", "en", "🔊 Echo: "),
    ],
    ids=["ru", "en"],
)
async def test_echo_answer_sends_prefixed_text(
    mock_message,
    text: str,
    lang: str,
    expected_prefix: str,
):
    """
    Given: Данные от Code с текстом.
    When:  EchoAnswer.run вызывается.
    Then:  Отправляется сообщение с префиксом + текст.
    """
    from node.control.answer.echo_answer import EchoAnswer

    answer = EchoAnswer()
    await answer.run(
        event=mock_message,
        user_lang=lang,
        data={"telegram_id": 123, "text": text, "user_lang": lang},
    )

    mock_message.answer.assert_called_once_with(text=f"{expected_prefix}{text}")
