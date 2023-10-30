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
    """A form of message which handles events."""


class EventBus:
    """Dispatches events to their associated handlers."""

    @typechecked
    def dispatch(self, event: Event, handlers: list[IMessageHandler]) -> None:
        """Dispatch a provided event to the given handlers."""
        for handler in handlers:
            handler.handle(event)
