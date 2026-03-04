"""
Основная конфигурация бота.

Содержит настройки:
- BOT_TOKEN: Токен Telegram бота
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    Класс конфигурации бота.

    Attributes:
        BOT_TOKEN: Токен Telegram бота из BotFather
        BACKEND_URL: Базовый URL бэкенд-сервиса
    """

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    def validate(self) -> None:
        """
        Проверить обязательные настройки.

        Raises:
            ValueError: Если BOT_TOKEN не указан
        """
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не указан в переменных окружения")


config = Config()
