"""
Users Router — роутер для управления пользователями.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

## Endpoints
- POST /users — get_or_create пользователя по telegram_id
"""

from fastapi import APIRouter

from .post import router as post_router

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(post_router)
