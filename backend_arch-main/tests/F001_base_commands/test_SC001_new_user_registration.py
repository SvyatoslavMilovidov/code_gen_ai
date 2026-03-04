"""
Тест SC001 — Регистрация нового пользователя.

## Трассируемость
Feature: F001 — Базовые команды
Scenario: SC001 — Новый пользователь: /start → регистрация в БД + приветствие

## BDD
Given: Пользователь не существует в БД
When:  POST /api/v1/users с telegram_id
Then:  Пользователь создан в БД, is_new=True
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "telegram_id, username",
    [
        (123, "john"),
        (456, None),
    ],
    ids=["with_username", "without_username"],
)
async def test_new_user_created(
    client: AsyncClient,
    telegram_id: int,
    username: str | None,
):
    """
    Given: Пустая БД (пользователь не существует).
    When:  POST /api/v1/users с telegram_id и username.
    Then:  Ответ содержит is_new=True и данные пользователя.
    """
    payload = {"telegram_id": telegram_id, "username": username}

    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["is_new"] is True
    assert body["user"]["telegram_id"] == telegram_id
    assert body["user"]["username"] == username
    assert "id" in body["user"]
    assert "created_at" in body["user"]
