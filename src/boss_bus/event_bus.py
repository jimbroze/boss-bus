"""Interfaces for a form of message bus that handles events.

Events can have multiple handlers.

Classes:

    Event
    EventHandler
"""

from __future__ import annotations

from abc import abstractmethod

from .interface import IMessage
from .interface import IMessageHandler


class Event(IMessage):
    """A form of message which handles events."""

    pass


class EventHandler(IMessageHandler):
    """A form of message handler which performs operations using events."""

    @abstractmethod
    def handle(self, event: Event):
        """Dispatch a provided event."""
        raise NotImplementedError
