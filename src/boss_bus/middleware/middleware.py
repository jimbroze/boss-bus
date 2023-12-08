"""Interfaces for classes that augment or supplement message handling."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable

from boss_bus.interface import Message, MessageT

HandlerT = Callable[[MessageT], Any]


class Middleware(ABC):
    """Performs actions before or after message handling."""

    @property
    @abstractmethod
    def message_id(self) -> str:
        """The name of a bool attr set on messages that this middleware should use."""

    @abstractmethod
    def handle(
        self,
        message: MessageT,
        next_middleware: HandlerT[MessageT],
    ) -> Any:
        """Performs actions before or after a message is handled.

        Args:
            message (MessageT): The message to be handled by this middleware.
            next_middleware (Callable[[MessageT], Any]): The next handler that the
                message should be passed to.
        """

    def message_applicable(self, message: Message) -> bool:
        """Should the current middleware do anything with this message."""
        return getattr(message, self.message_id, False)


def create_middleware_chain(
    bus_closure: HandlerT[MessageT],
    middlewares: list[Middleware],
) -> HandlerT[MessageT]:
    """Creates a chain of middleware handlers finishing with a command or event bus."""

    def middleware_closure(
        middleware: Middleware,
        next_closure: HandlerT[MessageT],
        message: MessageT,
    ) -> Any:
        return middleware.handle(message, next_closure)

    next_handler = bus_closure
    for one_middleware in reversed(middlewares):
        next_handler = partial(middleware_closure, one_middleware, next_handler)

    return next_handler
