"""Interfaces for classes that augment or supplement message handling."""

from __future__ import annotations

from functools import partial
from typing import Any, Callable, Protocol, runtime_checkable

from boss_bus.interface import Message, MessageT  # noqa: TCH001


@runtime_checkable
class Middleware(Protocol):
    """Performs actions before or after message handling."""

    message_id: str

    def handle(
        self,
        message: MessageT,
        next_middleware: Callable[[MessageT], Any],
    ) -> Any:
        """Perform actions before or after message handling."""

    def message_applicable(self, message: Message) -> bool:
        """Should the current middleware do anything with this message."""
        return getattr(message, self.message_id, False)


def create_middleware_chain(
    bus_closure: Callable[[MessageT], Any],
    middlewares: list[Middleware],
) -> Callable[[MessageT], Any]:
    """Creates a chain of middleware finishing with a bus."""

    def middleware_closure(
        current_middleware: Middleware,
        next_closure: Callable[[MessageT], Any],
        message: MessageT,
    ) -> Any:
        return current_middleware.handle(message, next_closure)

    next_middleware = bus_closure
    for middleware in reversed(middlewares):
        next_middleware = partial(middleware_closure, middleware, next_middleware)

    return next_middleware
