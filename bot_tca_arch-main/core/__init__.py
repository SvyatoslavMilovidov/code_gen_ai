"""
Пакет core - основные настройки и конфигурация бота.

Содержит:
- config: Конфигурация из переменных окружения
- loader: Инициализация бота и диспетчера
- vocab: Словари текстов и сообщений
"""

from core.config import config
from core.loader import bot, dp

__all__ = ["config", "bot", "dp"]
