"""Interfaces for a form of message bus that handles events.

Events can have multiple handlers.

Classes:

    Event
    EventBus
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from typeguard import typechecked

if TYPE_CHECKING:
    from boss_bus.interface import IMessageHandler


class Event:
    """A form of message which can have multiple handlers."""


class MissingHandlerError(Exception):
    """An Event Handler has not been provided."""


class EventBus:
    """Dispatches events to their associated handlers."""

    @typechecked
    def dispatch(self, event: Event, handlers: list[IMessageHandler]) -> None:
        """Dispatch a provided event to the given handlers."""
        if len(handlers) == 0:
            raise MissingHandlerError

        for handler in handlers:  # pragma: no branch
            handler.handle(event)
