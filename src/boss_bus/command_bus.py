"""Interfaces for a form of message bus that executes commands.

Commands can only have one handler.

Classes:

    Command
    CommandBus
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

from typeguard import typechecked

from boss_bus.handler import MissingHandlerError

if TYPE_CHECKING:
    from boss_bus.interface import IMessageHandler


class Command:
    """A form of message which only has one handler."""


class MissingCommandError(Exception):
    """The requested Error could not be found."""


class TooManyHandlersError(Exception):
    """Only one handler can be used with a command."""


class CommandBus:
    """Executes commands using their associated handler."""

    def __init__(self) -> None:
        """Creates a Command Bus."""
        self._handlers: dict[type[Command], IMessageHandler] = {}

    @typechecked
    def register_handler(
        self,
        command_type: Type[Command],  # noqa: UP006
        handler: IMessageHandler,
    ) -> None:
        """Register a single handler that will execute a type of Command."""
        self._handlers[command_type] = handler

    @typechecked
    def execute(self, command: Command, handler: IMessageHandler | None = None) -> None:
        """Execute a provided command using its handler."""
        if hasattr(handler, "__iter__"):
            raise TooManyHandlersError("Only one handler can execute a command")

        matched_handler = self._handlers.get(type(command), handler)

        if handler and handler != matched_handler:
            raise TooManyHandlersError(
                f"A handler has already been registered for the command '{type(command).__name__}'"
            )

        if not matched_handler:
            raise MissingHandlerError(
                f"A handler has not been registered for the command '{type(command).__name__}'"
            )

        matched_handler.handle(command)
