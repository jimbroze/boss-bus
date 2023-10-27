"""Base Interfaces for message bus classes.

Classes:

    IMessage
    IMessageHandler
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class IMessage:
    """A message which will be passed to a handler for handling."""

    pass


class IMessageHandler(ABC):
    """A message handler that handles messages."""

    @abstractmethod
    def handle(self, message: IMessage):
        """Perform actions using a provided message."""
        raise NotImplementedError
