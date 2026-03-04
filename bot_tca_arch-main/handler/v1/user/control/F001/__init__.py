"""
Виджеты фичи F001 — Базовые команды.

## Трассируемость
Feature: F001 — Базовые команды
Scenarios: SC001, SC002, SC003, SC004

Содержит виджеты:
- start_command_widget: Обработка /start (SC001, SC002)
- help_command_widget: Обработка /help (SC003)
- echo_widget: Эхо-ответ на текст (SC004)
"""

from handler.v1.user.control.F001 import start_command_widget
from handler.v1.user.control.F001 import help_command_widget
from handler.v1.user.control.F001 import echo_widget
