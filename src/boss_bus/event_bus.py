"""Interfaces for a form of message bus that handles events.

Events can have multiple handlers.

Classes:

    Event
    EventBus
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Sequence, Type

from typeguard import TypeCheckError, typechecked

from boss_bus.handler import MissingHandlerError
from boss_bus.interface import SupportsHandle


class Event:
    """A form of message which can have multiple handlers."""


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
        >>> from tests.examples import TestEvent, TestEventHandler
        >>> bus = EventBus()
        >>> test_handler = TestEventHandler()
        >>> test_event = TestEvent("Testing...")
        >>>
        >>> bus.add_handlers(TestEvent, [test_handler])
        >>> bus.dispatch(test_event)
        Testing...
    """

    def __init__(self) -> None:
        """Creates an Event Bus."""
        self._handlers: dict[type[Event], list[SupportsHandle]] = defaultdict(list)

    @typechecked
    def add_handlers(
        self,
        event_type: Type[Event],  # noqa: UP006
        handlers: Sequence[SupportsHandle],
    ) -> None:
        """Register handlers that will dispatch a type of Event."""
        for handler in handlers:  # pragma: no branch
            _validate_handler(handler)
            self._handlers[event_type].append(handler)

    @typechecked
    def remove_handlers(
        self,
        event_type: Type[Event],  # noqa: UP006
        handlers: Sequence[SupportsHandle] | None = None,
    ) -> None:
        """Remove previously registered handlers."""
        if handlers is None:
            handlers = []

        for handler in handlers:
            _validate_handler(handler)

            if handler not in self._handlers[event_type]:
                raise MissingHandlerError(
                    f"The handler '{handler}' has not been registered for event '{event_type.__name__}'"
                )

            self._handlers[event_type].remove(handler)

        if len(handlers) == 0:  # pragma: no branch
            self._handlers[event_type] = []

    @typechecked
    def dispatch(
        self, event: Event, handlers: Sequence[SupportsHandle] | None = None
    ) -> None:
        """Dispatch events to their handlers.

        Handlers can be dispatched directly or pre-registered with 'add_handlers'.
        Previously registered handlers dispatch first.

        Example:
            >>> from tests.examples import TestEvent, TestEventHandler
            >>> bus = EventBus()
            >>> test_handler = TestEventHandler()
            >>> test_event = TestEvent("Testing...")
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
