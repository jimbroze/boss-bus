"""Interfaces for a form of message bus that handles events.

Events can have multiple handlers.

Classes:

    Event
    EventBus
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Sequence, Type, TypeVar

from typeguard import TypeCheckError, typechecked

from boss_bus.interface import Message, MissingHandlerError, SupportsHandle


class Event(Message):
    """A form of message which can have multiple handlers."""

    message_type: str = "event"


SpecificEvent = TypeVar("SpecificEvent", bound=Event)


class MissingEventError(Exception):
    """The requested Error could not be found."""


def _validate_handler(handler: Any) -> None:
    if isinstance(handler, type):
        raise TypeCheckError(
            f"'handlers' must be an instance of {SupportsHandle.__name__}"
        )


class EventBus:
    """Dispatches events to their associated handlers.

    Example:
        >>> from tests.examples import ExampleEvent, ExampleEventHandler
        >>> bus = EventBus()
        >>> test_handler = ExampleEventHandler()
        >>> test_event = ExampleEvent("Testing...")
        >>>
        >>> bus.add_handlers(ExampleEvent, [test_handler])
        >>> bus.dispatch(test_event)
        Testing...
    """

    def __init__(self) -> None:
        """Creates an Event Bus."""
        self._handlers: dict[type[Event], list[SupportsHandle]] = defaultdict(list)

    @typechecked
    def add_handlers(
        self,
        event_type: Type[Event],
        handlers: Sequence[SupportsHandle],
    ) -> None:
        """Register handlers that will dispatch a type of Event.

        Handlers must be objects with a handle() method.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler, OtherEventHandler
            >>> bus = EventBus()
            >>> bus.add_handlers(ExampleEvent, [ExampleEventHandler(), OtherEventHandler()])
            >>>
            >>> bus.has_handlers(ExampleEvent)
            2
        """
        for handler in handlers:  # pragma: no branch
            _validate_handler(handler)
            self._handlers[event_type].append(handler)

    @typechecked
    def remove_handlers(
        self,
        event_type: Type[Event],
        handlers: Sequence[SupportsHandle] | None = None,
    ) -> None:
        """Remove previously registered handlers.

        If handlers are provided, handlers of this class will be removed.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler, OtherEventHandler
            >>> bus = EventBus()
            >>> handler1 = ExampleEventHandler()
            >>> bus.add_handlers(ExampleEvent, [handler1, OtherEventHandler()])
            >>>
            >>> bus.remove_handlers(ExampleEvent, [handler1])
            >>> bus.has_handlers(ExampleEvent)
            1

        Defaults to removing all handlers for an event if no handlers are provided.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler, OtherEventHandler
            >>> bus = EventBus()
            >>> handler1 = ExampleEventHandler()
            >>> bus.add_handlers(ExampleEvent, [handler1, OtherEventHandler()])
            >>>
            >>> bus.remove_handlers(ExampleEvent)
            >>> bus.has_handlers(ExampleEvent)
            0
        """
        if handlers is None:
            self._handlers[event_type] = []
            return

        for handler in handlers:  # pragma: no branch
            _validate_handler(handler)

            matching_handlers = [
                registered_handler
                for registered_handler in self._handlers[event_type]
                if type(handler) == type(registered_handler)
            ]

            if not matching_handlers:
                raise MissingHandlerError(
                    f"The handler '{handler}' has not been registered for event '{event_type.__name__}'"
                )

            for matched_handler in matching_handlers:
                self._handlers[event_type].remove(matched_handler)

    def has_handlers(self, event_type: Type[Event]) -> int:
        """Returns the number of handlers registered for a type of event.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler
            >>> bus = EventBus()
            >>> bus.add_handlers(ExampleEvent, [ExampleEventHandler()])
            >>>
            >>> bus.has_handlers(ExampleEvent)
            1
        """
        return len(self._handlers[event_type])

    @typechecked
    def dispatch(
        self, event: Event, handlers: Sequence[SupportsHandle] | None = None
    ) -> None:
        """Dispatch events to their handlers.

        Handlers can be dispatched directly or pre-registered with 'add_handlers'.
        Previously registered handlers dispatch first.

        Example:
            >>> from tests.examples import ExampleEvent, ExampleEventHandler
            >>> bus = EventBus()
            >>> test_handler = ExampleEventHandler()
            >>> test_event = ExampleEvent("Testing...")
            >>>
            >>> bus.dispatch(test_event, [test_handler])
            Testing...
        """
        if handlers is None:
            handlers = []

        matched_handlers = self._handlers[type(event)]
        matched_handlers.extend(handlers)

        for handler in matched_handlers:  # pragma: no branch
            handler.handle(event)
