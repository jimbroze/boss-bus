from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture
from tests.middleware.examples import (
    LockingCommandHandler,
    LockingEventHandler,
    LockTestCommand,
    LockTestEvent,
    LoggingCommandHandler,
    LogTestCommand,
)

from boss_bus.middleware.lock import BusLocker


class TestLock:
    def test_non_locking_command_does_not_lock_bus(self) -> None:
        locker = BusLocker()
        command = LogTestCommand("")

        def bus(c: LogTestCommand) -> Any:
            LoggingCommandHandler().handle(c)  # type: ignore[arg-type]

        locker.handle(command, bus)

        assert locker.bus_locked is False

    def test_locking_command_postpones_nested_command(
        self, caplog: LogCaptureFixture
    ) -> None:
        locker = BusLocker()
        command = LockTestCommand()
        caplog.set_level(logging.INFO)

        def bus(c: LockTestCommand) -> Any:
            LockingCommandHandler(locker).handle(c)  # type: ignore[arg-type]

        locker.handle(command, bus)

        assert "Pre-nested call" in caplog.record_tuples[0][2]
        assert "Post-nested call" in caplog.record_tuples[1][2]
        assert "Nested call" in caplog.record_tuples[2][2]

    def test_locking_event_postpones_nested_event(
        self, caplog: LogCaptureFixture
    ) -> None:
        locker = BusLocker()
        event = LockTestEvent()
        caplog.set_level(logging.INFO)

        def bus(e: LockTestEvent) -> Any:
            LockingEventHandler(locker).handle(e)  # type: ignore[arg-type]

        locker.handle(event, bus)

        assert "Pre-nested call" in caplog.record_tuples[0][2]
        assert "Post-nested call" in caplog.record_tuples[1][2]
        assert "Nested call" in caplog.record_tuples[2][2]
