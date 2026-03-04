"""
UserModel — модель пользователя Telegram.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002

## Бизнес-контекст
Хранит данные пользователей, зарегистрированных через Telegram-бот.
Уникальность определяется по telegram_id.

## Поля
- telegram_id: ID пользователя в Telegram (уникальный)
- username: username в Telegram (может быть None)
"""

from sqlalchemy import Column, BigInteger, String
from model.base_model import Base, BaseModel


class UserModel(Base, BaseModel):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
