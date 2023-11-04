"""The main entrypoint to the Boss-Bus package.

Classes:

    MessageBus
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from boss_bus.command_bus import CommandBus, CommandHandler, SpecificCommand
from boss_bus.event_bus import Event, EventBus

if TYPE_CHECKING:
    from boss_bus.interface import SupportsHandle


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
        """Dispatch events to their handlers.

        Handlers can be dispatched directly or pre-registered with 'add_handlers'.
        Previously registered handlers dispatch first.

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
