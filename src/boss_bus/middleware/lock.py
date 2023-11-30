"""Enable automated logging within message handling."""

from __future__ import annotations

from typing import Any, Callable

from boss_bus.command_bus import Command
from boss_bus.event_bus import Event
from boss_bus.interface import Message, SpecificMessage
from boss_bus.middleware.middleware import Middleware


class LockingMessage(Message):
    """A message that must be handled completely before other messages can be handled."""


class LockingCommand(LockingMessage, Command):
    """A form of command that must finish being handled before other commands can be executed."""


class LockingEvent(LockingMessage, Event):
    """A form of event that must finish being handled before other events can be dispatched."""


class BusLocker(Middleware):
    """Locks a MessageBus to prevent messages from being handled."""

    def __init__(self):
        """Creates a middleware class that can lock buses while messages are being handled."""
        self.bus_locked: bool = False
        self.queue: list[tuple[SpecificMessage, Callable[[SpecificMessage], Any]]] = []

    def handle(
        self,
        message: SpecificMessage,
        next_middleware: Callable[[SpecificMessage], Any],
    ) -> Any:
        """Locks a message bus while a message is being handled."""
        print(self.bus_locked)
        if self.bus_locked:
            self.queue.append((message, next_middleware))
            return None

        if not isinstance(message, LockingMessage):
            return next_middleware(message)

        self.bus_locked = True
        result = next_middleware(message)
        self.bus_locked = False

        for msg, handler in self.queue:
            handler(msg)

        return result
