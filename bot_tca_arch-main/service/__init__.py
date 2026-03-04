"""
Пакет service — API-клиенты к бэкенд-сервисам.

Бот не содержит прямого доступа к БД и тяжёлой бизнес-логики.
Все данные получаются через HTTP API бэкенд-сервисов.

Структура:
- service/api/ — HTTP-клиенты к REST API
"""

from service.api import UserAPI

__all__ = ["UserAPI"]
