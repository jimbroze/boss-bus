"""Interfaces for a form of message bus that handles events.

Events can have multiple handlers.

Classes:

    Event
    EventBus
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Sequence, Type

from typeguard import typechecked

from boss_bus.handler import MissingHandlerError

if TYPE_CHECKING:
    from boss_bus.interface import IMessageHandler


class Event:
    """A form of message which can have multiple handlers."""


class MissingEventError(Exception):
    """The requested Error could not be found."""


class EventBus:
    """Dispatches events to their associated handlers."""

    def __init__(self) -> None:
        """Creates an Event Bus."""
        self._handlers: dict[type[Event], list[IMessageHandler]] = defaultdict(list)

    @typechecked
    def add_handlers(
        self,
        event_type: Type[Event],  # noqa: UP006
        handlers: Sequence[IMessageHandler],
    ) -> None:
        """Register handlers that will dispatch a type of Event."""
        if len(handlers) == 0:
            raise TypeError("add_handlers() requires at least one handler")

        self._handlers[event_type].extend(handlers)

    @typechecked
    def remove_handlers(
        self,
        event_type: Type[Event],  # noqa: UP006
        handlers: Sequence[IMessageHandler] | None = None,
    ) -> None:
        """Remove previously registered handlers."""
        if handlers is None:
            handlers = []

        if event_type not in self._handlers:
            raise MissingEventError(f"The event '{event_type}' has not been registered")

        for handler in handlers:
            if handler not in self._handlers[event_type]:
                raise MissingHandlerError(
                    f"The handler '{handler}' has not been registered for event '{event_type.__name__}'"
                )

            self._handlers[event_type].remove(handler)

        if (  # pragma: no branch
            len(handlers) == 0 or len(self._handlers[event_type]) == 0
        ):
            del self._handlers[event_type]

    @typechecked
    def dispatch(
        self, event: Event, handlers: Sequence[IMessageHandler] | None = None
    ) -> None:
        """Dispatch events to their handlers.

        Previously registered handlers dispatch first.
        """
        if handlers is None:
            handlers = []

        matched_handlers = self._handlers[type(event)]
        matched_handlers.extend(handlers)

        for handler in matched_handlers:  # pragma: no branch
            handler.handle(event)
