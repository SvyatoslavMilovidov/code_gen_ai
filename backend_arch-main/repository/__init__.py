"""
Repository — слой доступа к данным.

Экспортирует все репозитории для удобного импорта:
    from repository import BaseRepository
"""

from .base_repository import BaseRepository
from .user.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
]
