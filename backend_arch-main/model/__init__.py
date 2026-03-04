"""
Model — ORM модели приложения.

Экспортирует все модели для удобного импорта:
    from model import Base, ExampleModel
"""

from .base_model import Base, BaseModel
from .enums import ExampleStatusEnum
from .user.user_model import UserModel

__all__ = [
    "Base",
    "BaseModel",
    "ExampleStatusEnum",
    "UserModel",
]
