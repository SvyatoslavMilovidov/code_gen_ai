"""
Фикстуры для тестов F001 — Базовые команды.

## Трассируемость
Feature: F001 — Базовые команды

Используется тестовая БД PostgreSQL.
Переменные окружения TEST_DB_* (или fallback на основные DB_* с суффиксом _test).
"""

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from model.base_model import Base
from core import app, db_connect


def _test_database_url() -> str:
    """Собрать URL тестовой PostgreSQL из переменных окружения."""
    host = os.getenv("TEST_DB_HOST", os.getenv("DB_HOST", "localhost"))
    port = os.getenv("TEST_DB_PORT", os.getenv("DB_PORT", "5432"))
    user = os.getenv("TEST_DB_USER", os.getenv("DB_USER", "postgres"))
    password = os.getenv("TEST_DB_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))
    name = os.getenv("TEST_DB_NAME", os.getenv("DB_NAME", "test_db"))
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


@pytest_asyncio.fixture
async def async_session():
    """Создать PostgreSQL сессию для тестов с автоочисткой таблиц."""
    engine = create_async_engine(_test_database_url(), echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(async_session: AsyncSession):
    """HTTP-клиент для тестирования API с подменённой сессией БД."""

    async def override_get_session():
        yield async_session

    app.dependency_overrides[db_connect.get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
