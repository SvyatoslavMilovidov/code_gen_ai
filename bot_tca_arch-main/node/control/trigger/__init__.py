"""
Trigger компоненты тега control.

Содержит:
- StartCommandTrigger: Обработка команды /start
- HelpCommandTrigger: Обработка команды /help
- EchoTrigger: Обработка текстовых сообщений для эхо
"""

from node.control.trigger.start_command_trigger import StartCommandTrigger
from node.control.trigger.help_command_trigger import HelpCommandTrigger
from node.control.trigger.echo_trigger import EchoTrigger

__all__ = ["StartCommandTrigger", "HelpCommandTrigger", "EchoTrigger"]
