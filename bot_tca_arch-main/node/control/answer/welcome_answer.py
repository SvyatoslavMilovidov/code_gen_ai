"""
Answer: Приветственный экран.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001 (welcome_new), SC002 (welcome_back)

Состояние экрана: Показывается после команды /start.
Отображение: Разное приветствие для нового и существующего пользователя.

Используется в виджетах:
- handler/v1/user/control/F001/start_command_widget.py
"""

from aiogram.types import Message

from core.vocab import MESSAGES


class WelcomeAnswer:
    """
    Answer для приветственного экрана.

    ## Трассируемость
    Feature: F001
    Scenarios: SC001, SC002

    Используемые тексты:
    - MESSAGES["welcome_new"] — SC001: приветствие нового пользователя
    - MESSAGES["welcome_back"] — SC002: приветствие существующего
    """

    async def run(
        self,
        event: Message,
        user_lang: str,
        data: dict,
        **kwargs,
    ) -> None:
        """
        Отрисовать приветственный экран.

        Args:
            event: Message для отправки ответа
            user_lang: Язык пользователя
            data: Данные от Code (содержит is_new)
        """
        text = self._build_text(data, user_lang)
        await event.answer(text=text)

    def _build_text(self, data: dict, user_lang: str) -> str:
        is_new = data.get("is_new", True)
        key = "welcome_new" if is_new else "welcome_back"
        return MESSAGES[key][user_lang]
