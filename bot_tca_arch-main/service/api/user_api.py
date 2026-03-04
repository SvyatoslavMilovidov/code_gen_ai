"""
HTTP-клиент для работы с пользователями через бэкенд-сервис.

Features: F001
Scenarios: SC001, SC002

SC001 — POST /api/v1/users → создание нового пользователя.
SC002 — POST /api/v1/users → возврат существующего (без дубликата).
"""

import httpx

from core.config import config


class UserAPI:
    """Клиент к API пользователей бэкенд-сервиса."""

    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or config.BACKEND_URL

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
    ) -> tuple[dict, bool]:
        """
        Создать или получить пользователя через бэкенд.

        Args:
            telegram_id: ID пользователя в Telegram.
            username: username пользователя.

        Returns:
            tuple[dict, bool]: (данные пользователя, is_new).
        """
        async with httpx.AsyncClient(base_url=self._base_url) as client:
            response = await client.post(
                "/api/v1/users",
                json={
                    "telegram_id": telegram_id,
                    "username": username,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["user"], data["is_new"]
