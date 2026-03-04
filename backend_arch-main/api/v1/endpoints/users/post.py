"""
Users POST Endpoints — создание / получение пользователя.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

## Endpoints
- POST /users — get_or_create по telegram_id
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.user.user_schema import (
    UserCreateSchema,
    UserGetOrCreateResponseSchema,
    UserResponseSchema,
)
from service.user.user_service import UserService

router = APIRouter()
service = UserService()


@router.post(
    "",
    response_model=UserGetOrCreateResponseSchema,
    summary="Создать или получить пользователя",
    description="""
    ## Бизнес-логика
    Ищет пользователя по telegram_id.
    Если не найден — создаёт нового.

    ## Трассируемость
    - SC001: новый пользователь → 201
    - SC002: существующий → 200
    """,
)
async def create_or_get_user(
    body: UserCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> UserGetOrCreateResponseSchema:
    """
    Get-or-create пользователя по telegram_id.

    ## Выходные данные
    - UserGetOrCreateResponseSchema с флагом is_new
    """
    user, is_new = await service.get_or_create(
        telegram_id=body.telegram_id,
        username=body.username,
        session=session,
    )
    user_response = UserResponseSchema.model_validate(user)
    return UserGetOrCreateResponseSchema(user=user_response, is_new=is_new)
