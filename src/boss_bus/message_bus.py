"""The main entrypoint to the Boss-Bus package.

Classes:

    MessageBus
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Type, Union

from typeguard import typeguard_ignore

from boss_bus.command_bus import (
    CommandBus,
    CommandHandler,
    SpecificCommand,
)
from boss_bus.event_bus import Event, EventBus
from boss_bus.interface import SupportsHandle  # noqa: TCH001
from boss_bus.loader.instantiator import ClassInstantiator

if TYPE_CHECKING:
    from boss_bus.loader import ClassLoader


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
        self,
        class_loader: ClassLoader | None = None,
        command_bus: CommandBus | None = None,
        event_bus: EventBus | None = None,
    ):
        """Creates a Message Bus."""
        self.loader = class_loader if class_loader is not None else ClassInstantiator()
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

    def register_event(
        self,
        message_type: Type[Event],
        handlers: Sequence[Type[SupportsHandle] | SupportsHandle],
    ) -> None:
        """Register handlers that will dispatch a type of Event."""
        loaded_handlers = [self.loader.load(handler) for handler in handlers]
        self.event_bus.add_handlers(message_type, loaded_handlers)

    @typeguard_ignore
    def register_command(
        self,
        message_type: Type[SpecificCommand],
        handler: Union[
            Type[CommandHandler[SpecificCommand]], CommandHandler[SpecificCommand]
        ],
    ) -> None:
        """Register a handler that will dispatch a type of Command."""
        loaded_handler = self.loader.load(handler)
        self.command_bus.register_handler(message_type, loaded_handler)

    def deregister_event(
        self,
        message_type: Type[Event],
        handlers: Sequence[SupportsHandle],
    ) -> None:
        """Remove handlers that are registered to dispatch an Event."""
        self.event_bus.remove_handlers(message_type, handlers)

    def deregister_command(self, message_type: Type[SpecificCommand]) -> None:
        """Remove a handler that is registered to execute a Command."""
        self.command_bus.remove_handler(message_type)
