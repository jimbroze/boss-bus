"""Base Interfaces for message bus classes.

Classes:

    IMessage
    IMessageHandler
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar


class IMessage:
    """A message that should be passed to a handler."""

    pass


MessageType = TypeVar("MessageType", bound=IMessage)


class IMessageHandler(ABC, Generic[MessageType]):
    """A message handler that handles messages."""

    @abstractmethod
    def handle(self, message: MessageType) -> Any:
        """Perform actions using a provided message."""
        raise NotImplementedError
