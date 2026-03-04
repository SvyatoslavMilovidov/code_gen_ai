"""
BaseModel — базовый класс для всех ORM моделей.

## Бизнес-контекст
Определяет общие поля и поведение для всех сущностей:
- Автоматический первичный ключ
- Временные метки создания и обновления

## Выходные данные
- Base: декларативная база SQLAlchemy
- BaseModel: миксин с общими полями
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel:
    """Миксин с общими полями для всех моделей."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
