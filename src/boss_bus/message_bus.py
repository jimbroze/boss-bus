"""The main entrypoint to the Boss-Bus package.

Classes:

    MessageBus
"""
from __future__ import annotations

from typing import Any, Sequence, Type

from boss_bus.command_bus import (
    Command,
    CommandBus,
    CommandHandler,
    SpecificCommand,
)
from boss_bus.event_bus import Event, EventBus
from boss_bus.interface import SupportsHandle  # noqa: TCH001


class MessageBus:
    """Forwards events and commands to their associated buses.

    Example:
        >>> from tests.examples import ExampleCommand, ExampleCommandHandler
        >>> bus = MessageBus()
        >>> test_handler = ExampleCommandHandler()
        >>> test_command = ExampleCommand("Testing...")
        >>>
        >>> bus.execute(test_command, test_handler)
        Testing...
    """

    def __init__(
        self, command_bus: CommandBus | None = None, event_bus: EventBus | None = None
    ) -> None:
        """Creates a Message Bus."""
        self.command_bus = command_bus if command_bus is not None else CommandBus()
        self.event_bus = event_bus if event_bus is not None else EventBus()

    def register(
        self,
        message_type: Type[Event] | Type[SpecificCommand],
        handlers: Sequence[SupportsHandle] | CommandHandler[SpecificCommand],
    ) -> None:
        """Register handlers that will dispatch an event or command."""
        if issubclass(message_type, Event):
            return self._register_event(message_type, handlers)
        if issubclass(message_type, Command):
            return self._register_command(message_type, handlers)
        raise TypeError("register() arg 1 must be an Event or a Command")

    def deregister(
        self,
        message_type: Type[Event] | Type[SpecificCommand],
        handlers: Sequence[SupportsHandle] | None = None,
    ) -> None:
        """Remove registered handlers for an event or command."""
        if issubclass(message_type, Event):
            return self._deregister_event(message_type, handlers)
        if issubclass(message_type, Command):
            return self._deregister_command(message_type)
        raise TypeError("deregister() arg 1 must be an Event or a Command class")

    def execute(
        self,
        command: SpecificCommand,
        handler: CommandHandler[SpecificCommand] | None = None,
    ) -> None:
        """Forwards a command to a CommandBus for execution.

        Example:
            >>> from tests.examples import ExampleCommand, ExampleCommandHandler
            >>> bus = MessageBus()
            >>> test_handler = ExampleCommandHandler()
            >>> test_command = ExampleCommand("Testing...")
            >>>
            >>> bus.execute(test_command, test_handler)
            Testing...
        """
        self.command_bus.execute(command, handler)

    def dispatch(
        self, event: Event, handlers: Sequence[SupportsHandle] | None = None
    ) -> None:
        """Forwards an event to an EventBus for dispatching.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler
            >>> bus = MessageBus()
            >>> test_handler = ExampleEventHandler()
            >>> test_event = ExampleEvent("Testing...")
            >>>
            >>> bus.dispatch(test_event, [test_handler])
            Testing...
        """
        self.event_bus.dispatch(event, handlers)

    def _register_event(
        self,
        message_type: Type[Event],
        handlers: Any,
    ) -> None:
        """Register handlers that will dispatch a type of Event."""
        self.event_bus.add_handlers(message_type, handlers)

    def _register_command(
        self,
        message_type: Type[SpecificCommand],
        handler: Any,
    ) -> None:
        """Register a handler that will dispatch a type of Command."""
        self.command_bus.register_handler(message_type, handler)

    def _deregister_event(
        self,
        message_type: Type[Event],
        handlers: Any,
    ) -> None:
        """Remove handlers that are registered to dispatch an Event."""
        self.event_bus.remove_handlers(message_type, handlers)

    def _deregister_command(self, message_type: Type[SpecificCommand]) -> None:
        """Remove a handler that is registered to execute a Command."""
        self.command_bus.remove_handler(message_type)
