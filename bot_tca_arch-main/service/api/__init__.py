"""
HTTP-клиенты к бэкенд-сервисам.

Features: F001
Scenarios: SC001, SC002

Содержит:
- user_api: регистрация и получение пользователей через бэкенд
"""

from service.api.user_api import UserAPI

__all__ = ["UserAPI"]
