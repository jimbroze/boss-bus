from __future__ import annotations

import logging
import multiprocessing
import threading
import time
from typing import TYPE_CHECKING, Any

from tests.examples import (
    ReturnTimeCommand,
    ReturnTimeCommandHandler,
)

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture
from tests.middleware.examples import (
    LockingCommandHandler,
    LockingEventHandler,
    LockSleepCommand,
    LockSleepCommandHandler,
    LockTestCommand,
    LockTestEvent,
    LoggingCommandHandler,
    LogTestCommand,
)

from boss_bus.middleware.lock import BusLocker

# multiprocessing.set_start_method("fork")


def lock_sleep_command_bus(c: LockSleepCommand) -> Any:
    return LockSleepCommandHandler().handle(c)


class TestLock:
    def test_non_locking_command_does_not_lock_bus(self) -> None:
        locker = BusLocker()
        command = LogTestCommand("")

        def bus(c: LogTestCommand) -> Any:
            LoggingCommandHandler().handle(c)

        locker.handle(command, bus)

        assert locker.bus_locked is False

    def test_locking_command_postpones_nested_command(
        self, caplog: LogCaptureFixture
    ) -> None:
        locker = BusLocker()
        command = LockTestCommand()
        caplog.set_level(logging.INFO)

        def bus(c: LockTestCommand) -> Any:
            LockingCommandHandler(locker).handle(c)

        locker.handle(command, bus)

        assert (
            caplog.text.index("Pre-nested call")
            < caplog.text.index("Post-nested call")
            < caplog.text.index("Nested call")
        )

    def test_locking_event_postpones_nested_event(
        self, caplog: LogCaptureFixture
    ) -> None:
        locker = BusLocker()
        event = LockTestEvent()
        caplog.set_level(logging.INFO)

        def bus(e: LockTestEvent) -> Any:
            LockingEventHandler(locker).handle(e)

        locker.handle(event, bus)

        assert (
            caplog.text.index("Pre-nested call")
            < caplog.text.index("Post-nested call")
            < caplog.text.index("Nested call")
        )

    def test_locked_bus_waits_to_execute_command_on_a_different_thread(self) -> None:
        locker = BusLocker()
        bus_unlock_time = multiprocessing.Value("d", 0)
        command_1 = LockSleepCommand(0.4, bus_unlock_time)
        command_2 = ReturnTimeCommand()

        def bus_2(c: ReturnTimeCommand) -> Any:
            return ReturnTimeCommandHandler().handle(c)

        thread_1 = threading.Thread(
            target=locker.handle, args=(command_1, lock_sleep_command_bus)
        )
        thread_1.start()
        bus_lock_time = time.time()

        command_2_time = locker.handle(command_2, bus_2)
        thread_1.join(timeout=2)

        assert bus_lock_time < bus_unlock_time.value < command_2_time  # type: ignore[attr-defined]

    def test_locked_bus_waits_to_execute_command_on_a_different_process(self) -> None:
        locker = BusLocker()
        bus_unlock_time = multiprocessing.Value("d", 0)
        command_1 = LockSleepCommand(0.4, bus_unlock_time)
        command_2 = ReturnTimeCommand()

        def bus_2(c: ReturnTimeCommand) -> Any:
            return ReturnTimeCommandHandler().handle(c)

        process_1 = multiprocessing.Process(
            target=locker.handle, args=(command_1, lock_sleep_command_bus)
        )
        process_1.start()
        bus_lock_time = time.time()

        time.sleep(0.2)

        command_2_time = locker.handle(command_2, bus_2)
        process_1.join(timeout=3)

        assert bus_lock_time < bus_unlock_time.value < command_2_time  # type: ignore[attr-defined]

    def test_command_execution_times_out_if_bus_is_locked_for_too_long(self) -> None:
        locker = BusLocker(0.4)
        bus_unlock_time = multiprocessing.Value("d", 0)
        command_1 = LockSleepCommand(1, bus_unlock_time)
        command_2 = ReturnTimeCommand()

        def bus_2(c: ReturnTimeCommand) -> Any:
            return ReturnTimeCommandHandler().handle(c)

        process_1 = multiprocessing.Process(
            target=locker.handle, args=(command_1, lock_sleep_command_bus)
        )
        process_1.start()
        bus_lock_time = time.time()

        time.sleep(0.2)

        command_2_time = locker.handle(command_2, bus_2)
        process_1.join(timeout=3)

        assert bus_lock_time < command_2_time < bus_unlock_time.value  # type: ignore[attr-defined]
