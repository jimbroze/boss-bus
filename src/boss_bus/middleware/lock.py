"""Enable automated logging within message handling."""

from __future__ import annotations

import os
import threading
import time
from multiprocessing import Value
from typing import TYPE_CHECKING, Any, Callable, Tuple

from boss_bus.command import Command
from boss_bus.event import Event
from boss_bus.interface import Message, MessageT
from boss_bus.middleware.middleware import Middleware

if TYPE_CHECKING:
    import ctypes
    from ctypes import c_ulong
    from multiprocessing.sharedctypes import SynchronizedBase


class LockingMessage(Message):
    """A message that must be handled completely before other messages can be handled."""

    locking_message = True


class LockingCommand(LockingMessage, Command):
    """A form of command that must finish being handled before other commands can be executed."""


class LockingEvent(LockingMessage, Event):
    """A form of event that must finish being handled before other events can be dispatched."""


def get_thread_id() -> int:
    """Return an ID representing the current process & thread."""
    return int(str(os.getpid()) + str(threading.get_ident()))


MessageHandlerTuple = Tuple[MessageT, Callable[[MessageT], Any]]


class BusLocker(Middleware):
    """Locks a MessageBus to prevent messages from being handled."""

    message_id: str = "locking_message"
    timeout_attr: str = "locking_timeout"

    def __init__(self, timeout: float = 5):
        """Creates a middleware class that can lock buses while messages are being handled.

        timeout sets the maximum time that a message will be paused for.
        After this, the lock will be ignored and handling will continue.
        """
        self.default_timeout = timeout
        self.timeout: SynchronizedBase[ctypes.c_double] = Value("d", timeout)
        self.locking_thread: SynchronizedBase[c_ulong] = Value("L", 0)
        self.queue: list[MessageHandlerTuple[Any]] = []

    def handle(
        self,
        message: MessageT,
        next_middleware: Callable[[MessageT], Any],
    ) -> Any:
        """Locks a message bus while a message is being handled."""
        thread_id = get_thread_id()

        if self.bus_locked:
            if self._in_locking_thread(thread_id):
                self._postpone_handling(message, next_middleware)
                return None

            self._wait_for_unlock(message)

        if not self.message_applicable(message):
            return next_middleware(message)

        self._lock_bus(thread_id, message)
        result = next_middleware(message)
        self._unlock_bus()

        self._handle_queue()
        return result

    def _in_locking_thread(self, thread_id: int) -> bool:
        return self.locking_thread.value == thread_id  # type: ignore[attr-defined, no-any-return]

    def _postpone_handling(
        self,
        message: MessageT,
        next_middleware: Callable[[MessageT], Any],
    ) -> None:
        self.queue.append((message, next_middleware))

    def _wait_for_unlock(self, message: Message) -> None:
        timeout = time.time() + getattr(  # type: ignore[operator]
            message, self.timeout_attr, self.timeout.value  # type: ignore[attr-defined]
        )
        while self.bus_locked:
            if time.time() > timeout:
                break

    def _lock_bus(self, thread_id: int, message: Message) -> None:
        self.timeout.value = getattr(message, self.timeout_attr, self.default_timeout)  # type: ignore[attr-defined]
        self.locking_thread.value = thread_id  # type: ignore[attr-defined]

    def _unlock_bus(self) -> None:
        self.locking_thread.value = 0  # type: ignore[attr-defined]

    def _handle_queue(self) -> None:
        for msg, handler in self.queue:
            handler(msg)

    @property
    def bus_locked(self) -> bool:
        """Whether new messages will be processed immediately."""
        return self.locking_thread.value != 0  # type: ignore[attr-defined, no-any-return]
