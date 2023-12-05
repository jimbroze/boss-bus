import logging
import multiprocessing
import threading
import time

from _pytest.logging import LogCaptureFixture
from tests.examples import (
    ExampleEvent,
    ExampleEventHandler,
    PrintCommand,
    PrintCommandHandler,
    ReturnTimeCommand,
    ReturnTimeCommandHandler,
)
from tests.middleware.examples import (
    LockSleepCommand,
    LockSleepCommandHandler,
    LoggingCommandHandler,
    LoggingEventHandler,
    LogTestCommand,
    LogTestEvent,
    NestedLockingEvent,
    NestedLockingEventHandler,
)

from boss_bus.bus import MessageBus
from boss_bus.middleware.lock import BusLocker
from boss_bus.middleware.log import MessageLogger


class TestMessageBusLogger:
    def test_log_commands_log_before_and_after_execution(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus(middleware=[MessageLogger()])

        bus.execute(LogTestCommand("Logging..."), LoggingCommandHandler())
        assert len(caplog.record_tuples) == 3
        assert caplog.record_tuples[1][2] == "Logging..."

    def test_none_log_commands_do_not_log_messages(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus(middleware=[MessageLogger()])

        bus.execute(PrintCommand("Logging..."), PrintCommandHandler())
        assert len(caplog.record_tuples) == 0

    def test_log_events_log_before_and_after_execution(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus(middleware=[MessageLogger()])

        bus.dispatch(LogTestEvent("Logging..."), [LoggingEventHandler()])
        assert len(caplog.record_tuples) == 3
        assert caplog.record_tuples[1][2] == "Logging..."

    def test_none_log_events_do_not_log_messages(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus(middleware=[MessageLogger()])

        bus.dispatch(ExampleEvent("Logging..."), [ExampleEventHandler()])
        assert len(caplog.record_tuples) == 0

    def test_middleware_handle_in_correct_order(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        logger_first = logging.getLogger("first")
        logger_second = logging.getLogger("second")
        message_logger_first = MessageLogger(logger_first)
        message_logger_second = MessageLogger(logger_second)
        bus = MessageBus(middleware=[message_logger_first, message_logger_second])

        bus.dispatch(LogTestEvent("Logging..."), [LoggingEventHandler()])
        assert caplog.record_tuples[0][0] == "first"
        assert caplog.record_tuples[1][0] == "second"
        assert caplog.record_tuples[3][0] == "second"
        assert caplog.record_tuples[4][0] == "first"

    def test_nested_lock_event_is_postponed_until_after_initial_event(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus(middleware=[BusLocker()])

        bus.register_event(NestedLockingEvent, [NestedLockingEventHandler])  # type: ignore[misc]
        bus.dispatch(NestedLockingEvent())

        assert (
            caplog.text.index("Pre-nested call")
            < caplog.text.index("Post-nested call")
            < caplog.text.index("Nested call")
        )

    def test_locked_message_bus_waits_to_execute_command_on_a_different_thread(
        self,
    ) -> None:
        bus = MessageBus(middleware=[BusLocker()])
        bus_unlock_time = multiprocessing.Value("d", 0)
        command_1 = LockSleepCommand(0.4, bus_unlock_time)

        thread_1 = threading.Thread(
            target=bus.execute, args=(command_1, LockSleepCommandHandler())
        )
        thread_1.start()
        bus_lock_time = time.time()

        command_2_time = bus.execute(ReturnTimeCommand(), ReturnTimeCommandHandler())
        thread_1.join(timeout=3)

        assert bus_lock_time < bus_unlock_time.value < command_2_time  # type: ignore[attr-defined]

    def test_locked_message_bus_waits_to_execute_command_on_a_different_process(
        self,
    ) -> None:
        bus = MessageBus(middleware=[BusLocker()])
        bus_unlock_time = multiprocessing.Value("d", 0)
        command_1 = LockSleepCommand(0.6, bus_unlock_time)

        process_1 = multiprocessing.Process(
            target=bus.execute, args=(command_1, LockSleepCommandHandler())
        )
        process_1.start()
        bus_lock_time = time.time()

        time.sleep(0.2)

        command_2_time = bus.execute(ReturnTimeCommand(), ReturnTimeCommandHandler())
        process_1.join(timeout=4)

        assert bus_lock_time < bus_unlock_time.value < command_2_time  # type: ignore[attr-defined]
