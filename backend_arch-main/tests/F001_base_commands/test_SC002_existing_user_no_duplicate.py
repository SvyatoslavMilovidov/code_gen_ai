"""
Тест SC002 — Существующий пользователь не дублируется.

## Трассируемость
Feature: F001 — Базовые команды
Scenario: SC002 — Существующий пользователь: /start → приветствие (без дубликата)

## BDD
Given: Пользователь уже существует в БД
When:  POST /api/v1/users с тем же telegram_id
Then:  Возвращаются данные существующего пользователя, is_new=False
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_existing_user_no_duplicate(client: AsyncClient):
    """
    Given: Пользователь telegram_id=123 уже в БД.
    When:  POST /api/v1/users с telegram_id=123 повторно.
    Then:  is_new=False, id совпадает, дубликат не создан.
    """
    payload = {"telegram_id": 123, "username": "john"}

    # Given: создаём пользователя
    first = await client.post("/api/v1/users", json=payload)
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["is_new"] is True

    # When: повторный запрос
    second = await client.post("/api/v1/users", json=payload)

    # Then: тот же пользователь, is_new=False
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["is_new"] is False
    assert second_body["user"]["id"] == first_body["user"]["id"]
    assert second_body["user"]["telegram_id"] == 123
