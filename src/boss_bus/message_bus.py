"""The main entrypoint to the Boss-Bus package.

Classes:

    MessageBus
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Sequence, Type, Union

from typeguard import typeguard_ignore

from boss_bus.command_bus import (
    CommandBus,
    CommandHandler,
    SpecificCommand,
)
from boss_bus.event_bus import Event, EventBus, SpecificEvent
from boss_bus.interface import SpecificMessage, SupportsHandle  # noqa: TCH001
from boss_bus.loader.instantiator import ClassInstantiator
from boss_bus.middleware.log import (
    MessageLogger,
)

if TYPE_CHECKING:
    from boss_bus.loader import ClassLoader
    from boss_bus.middleware.middleware import Middleware


class MessageBus:
    """Forwards events and commands to their associated buses.

    Example:
        >>> from tests.examples import PrintCommand, PrintCommandHandler
        >>> bus = MessageBus()
        >>> test_handler = PrintCommandHandler()
        >>> test_command = PrintCommand("Testing...")
        >>>
        >>> bus.execute(test_command, test_handler)
        Testing...
    """

    def __init__(
        self,
        class_loader: ClassLoader | None = None,
        command_bus: CommandBus | None = None,
        event_bus: EventBus | None = None,
        logger: MessageLogger | None = None,
    ):
        """Creates a Message Bus."""
        self.loader = class_loader if class_loader is not None else ClassInstantiator()
        self.command_bus = command_bus if command_bus is not None else CommandBus()
        self.event_bus = event_bus if event_bus is not None else EventBus()
        self.logger = logger if logger is not None else MessageLogger()

    def execute(
        self,
        command: SpecificCommand,
        handler: CommandHandler[SpecificCommand] | None = None,
    ) -> Any:
        """Forwards a command to a CommandBus for execution.

        Example:
            >>> from tests.examples import PrintCommand, PrintCommandHandler
            >>> test_bus = MessageBus()
            >>> test_handler = PrintCommandHandler()
            >>> test_command = PrintCommand("Testing...")
            >>>
            >>> test_bus.execute(test_command, test_handler)
            Testing...
        """

        def bus_closure(c: SpecificCommand) -> Any:
            return self.command_bus.execute(c, handler)

        # noinspection PyTypeChecker
        bus = self.create_middleware_chain(bus_closure, [self.logger])
        return bus(command)

    def dispatch(
        self, event: SpecificEvent, handlers: Sequence[SupportsHandle] | None = None
    ) -> None:
        """Forwards an event to an EventBus for dispatching.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler
            >>> test_bus = MessageBus()
            >>> test_handler = ExampleEventHandler()
            >>> test_event = ExampleEvent("Testing...")
            >>>
            >>> test_bus.dispatch(test_event, [test_handler])
            Testing...
        """

        def bus_closure(e: SpecificEvent) -> None:
            return self.event_bus.dispatch(e, handlers)

        # noinspection PyTypeChecker
        bus = self.create_middleware_chain(bus_closure, [self.logger])
        bus(event)

    def register_event(
        self,
        message_type: Type[Event],
        handlers: Sequence[Type[SupportsHandle] | SupportsHandle],
    ) -> None:
        """Register handlers that can dispatch a type of Event.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler, OtherEventHandler
            >>> bus = MessageBus()
            >>> bus.register_event(ExampleEvent, [ExampleEventHandler, OtherEventHandler])
            >>>
            >>> bus.has_handlers(ExampleEvent)
            2
        """
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
        """Register a handler that can dispatch a type of Command.

        Example:
            >>> from tests.examples import PrintCommand, PrintCommandHandler
            >>> bus = MessageBus()
            >>> bus.register_command(PrintCommand, PrintCommandHandler)
            >>>
            >>> bus.is_registered(PrintCommand)
            True
        """
        loaded_handler = self.loader.load(handler)
        self.command_bus.register_handler(message_type, loaded_handler)

    def deregister_event(
        self,
        message_type: Type[Event],
        handlers: Sequence[Type[SupportsHandle] | SupportsHandle] | None = None,
    ) -> None:
        """Remove handlers that are registered to dispatch an Event.

        If handlers are provided, handlers of that class will be removed.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler, OtherEventHandler
            >>> bus = MessageBus()
            >>> example_handler = ExampleEventHandler()
            >>> bus.register_event(ExampleEvent, [example_handler, OtherEventHandler])
            >>>
            >>> bus.deregister_event(ExampleEvent, [OtherEventHandler])
            >>> bus.has_handlers(ExampleEvent)
            1

        Defaults to removing all handlers for an event if no handlers are provided.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler, OtherEventHandler
            >>> bus = MessageBus()
            >>> bus.register_event(ExampleEvent, [ExampleEventHandler, OtherEventHandler])
            >>>
            >>> bus.deregister_event(ExampleEvent)
            >>> bus.has_handlers(ExampleEvent)
            0
        """
        if handlers is None:
            return self.event_bus.remove_handlers(message_type)

        loaded_handlers = [self.loader.load(handler) for handler in handlers]
        return self.event_bus.remove_handlers(message_type, loaded_handlers)

    def deregister_command(self, message_type: Type[SpecificCommand]) -> None:
        """Remove a handler that is registered to execute a Command.

        Example:
            >>> from tests.examples import PrintCommand, PrintCommandHandler
            >>> bus = MessageBus()
            >>> bus.register_command(PrintCommand, PrintCommandHandler)
            >>>
            >>> bus.deregister_command(PrintCommand)
            >>> bus.is_registered(PrintCommand)
            False
        """
        self.command_bus.remove_handler(message_type)

    def has_handlers(self, event_type: Type[Event]) -> int:
        """Returns the number of handlers registered for a type of event.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler
            >>> bus = MessageBus()
            >>> bus.register_event(ExampleEvent, [ExampleEventHandler])
            >>>
            >>> bus.has_handlers(ExampleEvent)
            1
        """
        return self.event_bus.has_handlers(event_type)

    def is_registered(self, command_type: Type[SpecificCommand]) -> bool:
        """Returns whether a command is registered with the command bus.

        Example:
            >>> from tests.examples import PrintCommand, PrintCommandHandler
            >>> bus = MessageBus()
            >>> bus.register_command(PrintCommand, PrintCommandHandler)
            >>>
            >>> bus.is_registered(PrintCommand)
            True
        """
        return self.command_bus.is_registered(command_type)

    def create_middleware_chain(
        self,
        bus_closure: Callable[[SpecificMessage], Any],
        middlewares: list[Middleware],
    ) -> Callable[[SpecificMessage], Any]:
        """Creates a chain of middleware finishing with a bus."""

        def middleware_closure(
            current_middleware: Middleware,
            next_closure: Callable[[SpecificMessage], Any],
            message: SpecificMessage,
        ) -> Any:
            return current_middleware.handle(message, next_closure)

        next_middleware = bus_closure
        for middleware in reversed(middlewares):
            next_middleware = partial(middleware_closure, middleware, next_middleware)

        return next_middleware
