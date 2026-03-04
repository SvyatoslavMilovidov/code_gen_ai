"""
Answer: Экран эхо-ответа.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC004

Состояние экрана: Показывается после получения текстового сообщения.
Отображение: Эхо-ответ с префиксом и текстом пользователя.

Используется в виджетах:
- handler/v1/user/control/F001/echo_widget.py
"""

from aiogram.types import Message

from core.vocab import MESSAGES


class EchoAnswer:
    """
    Answer для эхо-ответа.

    ## Трассируемость
    Feature: F001
    Scenarios: SC004

    Используемые тексты:
    - MESSAGES["echo_prefix"] — префикс для эхо
    """

    async def run(
        self,
        event: Message,
        user_lang: str,
        data: dict,
        **kwargs,
    ) -> None:
        """
        Отрисовать эхо-ответ.

        Args:
            event: Message для отправки ответа
            user_lang: Язык пользователя
            data: Данные от Code (содержит text)
        """
        text = self._build_text(data, user_lang)
        await event.answer(text=text)

    def _build_text(self, data: dict, user_lang: str) -> str:
        prefix = MESSAGES["echo_prefix"][user_lang]
        user_text = data["text"]
        return f"{prefix}{user_text}"
