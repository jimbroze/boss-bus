"""Base Interfaces for message bus classes."""

from __future__ import annotations

from abc import ABC
from typing import Any, Protocol, TypeVar, runtime_checkable


class Message(ABC):
    """An abstract DTO that gets passed to handlers."""

    message_type: str = "message"

    @property
    def message_name(self) -> str:
        """Defines the name of a message being logged."""
        msg_type = type(self)
        return getattr(msg_type, "__name__", str(msg_type))


MessageT = TypeVar("MessageT", bound=Message)


@runtime_checkable
class SupportsHandle(Protocol):
    """An interface that requires a handler method."""

    def handle(self, message: Any) -> Any:
        """Performs actions using a message."""
        ...


class MissingHandlerError(Exception):
    """The requested Handler could not be found."""


class InvalidHandlerError(Exception):
    """The message and handler do not match."""
