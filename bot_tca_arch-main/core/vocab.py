"""
Словари и тексты для пользовательского интерфейса.

Организованы по функциональным областям.
Поддержка мультиязычности через словари с ключами языков.
"""

# Команды бота
COMMANDS = {
    "start": "start",
    "help": "help",
}

# Сообщения бота
MESSAGES = {
    "welcome_new": {
        "ru": "👋 Привет! Добро пожаловать!\n\nЯ эхо-бот. Отправь мне любое текстовое сообщение, и я повторю его.",
        "en": "👋 Hello! Welcome!\n\nI'm an echo bot. Send me any text message and I'll repeat it.",
    },
    "welcome_back": {
        "ru": "👋 С возвращением!\n\nОтправь мне текст — я повторю его.",
        "en": "👋 Welcome back!\n\nSend me text — I'll repeat it.",
    },
    "echo_prefix": {
        "ru": "🔊 Эхо: ",
        "en": "🔊 Echo: ",
    },
    "help": {
        "ru": "ℹ️ <b>Справка</b>\n\nЯ простой эхо-бот. Отправь мне текст — я повторю его.\n\nКоманды:\n/start - начать работу\n/help - эта справка",
        "en": "ℹ️ <b>Help</b>\n\nI'm a simple echo bot. Send me text — I'll repeat it.\n\nCommands:\n/start - start\n/help - this help",
    },
}

# Кнопки (если понадобятся)
BUTTONS = {
    "back": {
        "ru": "◀️ Назад",
        "en": "◀️ Back",
    },
}

# Язык по умолчанию
DEFAULT_LANGUAGE = "ru"
