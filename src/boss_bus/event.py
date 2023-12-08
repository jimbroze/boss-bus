"""Classes for a form of message bus that handles events.

Events can have multiple handlers but cannot return a value.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Generic, Sequence, Type, TypeVar

from boss_bus._utils.typing import get_annotations, type_matches
from boss_bus.interface import (
    InvalidHandlerError,
    Message,
    MissingHandlerError,
    SupportsHandle,
)


class Event(Message):
    """A form of message which can have multiple handlers."""

    message_type: str = "event"


EventT = TypeVar("EventT", bound=Event)


class EventHandler(ABC, SupportsHandle, Generic[EventT]):
    """A form of message handler to be used with events."""

    @abstractmethod
    def handle(self, command: EventT) -> Any:
        """Perform actions using a specific event."""


class MissingEventError(Exception):
    """The requested Event could not be found."""


def _validate_handler(event_type: Type[Event], handler: EventHandler[Any]) -> None:
    if isinstance(handler, type):
        raise InvalidHandlerError(
            f"The handler '{getattr(handler, '__name__', handler)}' "
            f"must be instantiated to be registered with the event bus"
        )
    if not type_matches(get_annotations(handler.handle)["event"], event_type):
        raise InvalidHandlerError(
            f"The handler '{getattr(handler, '__name__', handler)}' does "
            f"not match the event '{getattr(event_type, '__name__', event_type)}'"
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
        self._handlers: dict[type[Event], list[EventHandler[Any]]] = defaultdict(list)

    def add_handlers(
        self,
        event_type: Type[EventT],
        handlers: Sequence[EventHandler[EventT]],
    ) -> None:
        """Registers event handlers that will dispatch a type of Event.

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
            _validate_handler(event_type, handler)
            self._handlers[event_type].append(handler)

    def remove_handlers(
        self,
        event_type: Type[EventT],
        handlers: Sequence[EventHandler[EventT]] | None = None,
    ) -> None:
        """Removes previously registered event handlers.

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
            _validate_handler(event_type, handler)
            matching_handlers = [
                registered_handler
                for registered_handler in self._handlers[event_type]
                if type(handler) is type(registered_handler)
            ]

            if not matching_handlers:
                raise MissingHandlerError(
                    f"The handler '{handler}' has not been registered for event "
                    f"'{getattr(event_type, '__name__', event_type)}'"
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

    def dispatch(
        self, event: EventT, handlers: Sequence[EventHandler[EventT]] | None = None
    ) -> None:
        """Calls the handle methods on an event's handlers.

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
