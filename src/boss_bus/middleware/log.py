"""Enable automated logging within message handling."""

from __future__ import annotations

import logging
from abc import ABC
from typing import Any, Callable, ClassVar


class LoggingMessage(ABC):
    """A form of message that submits logs when being handled."""

    message_type: str = "message"
    message_verbs: ClassVar[list[str]] = ["handle", "handled", "handling"]

    @property
    def message_name(self) -> str:
        """Defines the name of a message being logged."""
        return type(self).__name__

    def pre_handle_log(self) -> str:
        """Creates some text to be logged before handling."""
        handling = self.message_verbs[2].capitalize()
        message = self.message_type
        name = self.message_name
        return f"{handling} {message} <{name}>"

    def post_handle_log(self) -> str:
        """Creates some text to be logged after handling."""
        handled = self.message_verbs[1]
        message = self.message_type
        name = self.message_name
        return f"Successfully {handled} {message} <{name}>"

    def error_log(self) -> str:
        """Creates some text to be logged if an error is raised."""
        handling = self.message_verbs[2]
        message = self.message_type
        name = self.message_name
        return f"Failed {handling} {message} <{name}>"


class LoggingCommand(LoggingMessage):
    """A form of command that submits logs when being handled."""

    message_type: str = "command"
    message_verbs: ClassVar[list[str]] = ["execute", "executed", "executing"]


class LoggingEvent(LoggingMessage):
    """A form of event that submits logs when being handled."""

    message_type: str = "event"
    message_verbs: ClassVar[list[str]] = ["dispatch", "dispatched", "dispatching"]


class MessageLogger:
    """Connects a logger to be used for automated message logging."""

    def __init__(self, logger: logging.Logger | None = None):
        """Creates a MessageLogger that automates logging during message handling."""
        self.logger = logger if logger is not None else logging.getLogger()

    def handle(
        self, message: LoggingMessage, loaded_bus: Callable[[LoggingMessage], Any]
    ) -> Any:
        """Submits logs and handles messages."""
        self.logger.info(message.pre_handle_log())

        try:
            result = loaded_bus(message)
        except Exception:
            self.logger.exception(message.error_log())
            raise

        self.logger.info(message.post_handle_log())

        return result
