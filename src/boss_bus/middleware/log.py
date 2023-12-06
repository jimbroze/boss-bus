"""Enable automated logging within message handling."""

from __future__ import annotations

import logging
from abc import ABC
from typing import Any, ClassVar, cast

from boss_bus.command import Command
from boss_bus.event import Event
from boss_bus.interface import Message, MessageT
from boss_bus.middleware.middleware import HandlerT, Middleware


class LoggingMessage(Message, ABC):
    """A form of message that submits logs when being handled."""

    logging_message = True
    message_verbs: ClassVar[list[str]] = ["handle", "handled", "handling"]

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


class LoggingCommand(LoggingMessage, Command):
    """A form of command that submits logs when being handled."""

    message_verbs: ClassVar[list[str]] = ["execute", "executed", "executing"]


class LoggingEvent(LoggingMessage, Event):
    """A form of event that submits logs when being handled."""

    message_verbs: ClassVar[list[str]] = ["dispatch", "dispatched", "dispatching"]


class MessageLogger(Middleware):
    """Connects a logger to be used for automated message logging."""

    message_id = "logging_message"

    def __init__(self, logger: logging.Logger | None = None):
        """Creates a MessageLogger that automates logging during message handling."""
        self.logger = logger if logger is not None else logging.getLogger()

    def handle(
        self,
        message: MessageT,
        next_middleware: HandlerT[MessageT],
    ) -> Any:
        """Submits logs and handles messages."""
        if not self.message_applicable(message):
            return next_middleware(message)
        msg = cast(LoggingMessage, message)

        self.logger.info(msg.pre_handle_log())

        try:
            result = next_middleware(message)
        except Exception:
            self.logger.exception(msg.error_log())
            raise

        self.logger.info(msg.post_handle_log())

        return result
