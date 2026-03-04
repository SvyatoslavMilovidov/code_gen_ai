"""
Точка входа в приложение Echo Bot.

Запуск:
    python app.py

Требования:
    - Установить переменную окружения BOT_TOKEN
    - Установить зависимости: pip install -r requirements.txt
"""

import asyncio
import logging
import sys

from core.config import config
from core.loader import bot, dp
from handler.include_router import include_routers


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


async def on_startup() -> None:
    """Действия при запуске бота."""
    logger.info("🚀 Бот запускается...")
    
    # Подключаем роутеры
    include_routers()
    
    logger.info("✅ Роутеры подключены")


async def on_shutdown() -> None:
    """Действия при остановке бота."""
    logger.info("🛑 Бот останавливается...")
    await bot.session.close()
    logger.info("✅ Бот остановлен")


async def main() -> None:
    """Главная функция запуска бота."""
    # Проверяем конфигурацию
    config.validate()
    
    # Регистрируем хуки запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Удаляем вебхук (если был) и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("🤖 Echo Bot запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
