"""Classes that load dependencies and use them to instantiate classes.

Class loading classes should implement the Interface (ClassLoader)
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol

if TYPE_CHECKING:
    from boss_bus.interface import SpecificMessage


class Middleware(Protocol):
    """Performs actions before or after message handling."""

    def handle(
        self,
        message: SpecificMessage,
        next_middleware: Callable[[SpecificMessage], Any],
    ) -> Any:
        """Perform actions before or after message handling."""
