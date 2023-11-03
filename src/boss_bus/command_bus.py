"""Interfaces for a form of message bus that executes commands.

Commands can only have one handler.

Classes:

    Command
    CommandBus
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import signature
from typing import Any, Generic, Type, TypeVar

from typeguard import typechecked

from boss_bus.handler import MissingHandlerError
from boss_bus.interface import SupportsHandle


class Command:
    """A form of message which only has one handler."""


SpecificCommand = TypeVar("SpecificCommand", bound=Command)


class CommandHandler(ABC, SupportsHandle, Generic[SpecificCommand]):
    """A form of message which only has one handler."""

    @abstractmethod
    def handle(self, command: SpecificCommand) -> None:
        """Perform actions using a specific command."""


class TooManyHandlersError(Exception):
    """Only one handler can be used with a command."""


class InvalidHandlerError(Exception):
    """The handler does not match the command."""


def _validate_handler(
    command_type: type[Command], handler: CommandHandler[Any]
) -> None:
    if (
        command_type.__name__
        != signature(handler.handle).parameters["command"].annotation
    ):
        raise InvalidHandlerError(
            f"The handler '{handler}' does not match the command '{command_type.__name__}'"
        )


class CommandBus:
    """Executes commands using their associated handler."""

    def __init__(self) -> None:
        """Creates a Command Bus."""
        self._handlers: dict[type[Command], CommandHandler[Any]] = {}

    @typechecked
    def register_handler(
        self,
        command_type: Type[SpecificCommand],  # noqa: UP006
        handler: CommandHandler[SpecificCommand],
    ) -> None:
        """Register a single handler that will execute a type of Command."""
        _validate_handler(command_type, handler)

        self._handlers[command_type] = handler

    @typechecked
    def remove_handler(
        self,
        command_type: Type[SpecificCommand],  # noqa: UP006
    ) -> None:
        """Remove a previously registered handler."""
        if command_type not in self._handlers:
            raise MissingHandlerError(
                f"A handler has not been registered for the command '{command_type.__name__}'"
            )

        del self._handlers[command_type]

    @typechecked
    def execute(
        self,
        command: SpecificCommand,
        handler: CommandHandler[SpecificCommand] | None = None,
    ) -> None:
        """Execute a provided command using its handler."""
        # print(check_type(handler, CommandHandler[SpecificCommand]))
        if handler:
            _validate_handler(type(command), handler)

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
