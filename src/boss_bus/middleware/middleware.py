"""Classes that load dependencies and use them to instantiate classes.

Class loading classes should implement the Interface (ClassLoader)
"""
from __future__ import annotations

from functools import partial
from typing import Any, Callable, Protocol, runtime_checkable

from boss_bus.interface import SpecificMessage  # noqa: TCH001


@runtime_checkable
class Middleware(Protocol):
    """Performs actions before or after message handling."""

    def handle(
        self,
        message: SpecificMessage,
        next_middleware: Callable[[SpecificMessage], Any],
    ) -> Any:
        """Perform actions before or after message handling."""


def create_middleware_chain(
    bus_closure: Callable[[SpecificMessage], Any],
    middlewares: list[Middleware],
) -> Callable[[SpecificMessage], Any]:
    """Creates a chain of middleware finishing with a bus."""

    def middleware_closure(
        current_middleware: Middleware,
        next_closure: Callable[[SpecificMessage], Any],
        message: SpecificMessage,
    ) -> Any:
        return current_middleware.handle(message, next_closure)

    next_middleware = bus_closure
    for middleware in reversed(middlewares):
        next_middleware = partial(middleware_closure, middleware, next_middleware)

    return next_middleware
