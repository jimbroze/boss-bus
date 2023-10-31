"""Interfaces for a form of message bus that handles events.

Events can have multiple handlers.

Classes:

    Event
    EventBus
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from typeguard import typechecked

if TYPE_CHECKING:
    from boss_bus.interface import IMessageHandler


class Event:
    """A form of message which can have multiple handlers."""


class EventBus:
    """Dispatches events to their associated handlers."""

    def __init__(self) -> None:
        """Creates an Event Bus."""
        self._handlers: dict[type[Event], list[IMessageHandler]] = defaultdict(list)

    def add_handlers(
        self, event_type: type[Event], handlers: list[IMessageHandler]
    ) -> None:
        """Register handlers that will dispatch a type of Event."""
        if not isinstance(event_type, type):
            raise TypeError(
                f"event_type passed to add_handlers must be a type. Got '{type(event_type)}"
            )

        if len(handlers) == 0:
            raise TypeError("add_handlers() requires at least one handler")

        self._handlers[event_type].extend(handlers)

    @typechecked
    def dispatch(
        self, event: Event, handlers: list[IMessageHandler] | None = None
    ) -> None:
        """Dispatch a provided event to the given handlers."""
        if handlers is None:
            handlers = []

        matched_handlers = self._handlers[type(event)]
        handlers.extend(matched_handlers)

        for handler in handlers:  # pragma: no branch
            handler.handle(event)
