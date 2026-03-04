"""
Фикстуры для тестов F001 — Базовые команды (Бот).

## Трассируемость
Feature: F001 — Базовые команды
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_message():
    """Мок Telegram Message."""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.text = "Hello"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_state():
    """Мок FSMContext."""
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.set_data = AsyncMock()
    state.clear = AsyncMock()
    return state
