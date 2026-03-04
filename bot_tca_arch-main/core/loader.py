"""
Загрузчик и инициализация компонентов бота.

Создает:
- bot: Экземпляр Telegram бота
- dp: Диспетчер для обработки событий
"""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import config


# Инициализация бота
bot = Bot(token=config.BOT_TOKEN)

# Инициализация диспетчера с хранилищем FSM в памяти
dp = Dispatcher(storage=MemoryStorage())
