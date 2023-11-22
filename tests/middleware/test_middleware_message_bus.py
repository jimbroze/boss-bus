import logging

from _pytest.logging import LogCaptureFixture
from tests.examples import (
    ExampleEvent,
    ExampleEventHandler,
    PrintCommand,
    PrintCommandHandler,
)
from tests.middleware.examples import (
    LoggingCommandHandler,
    LoggingEventHandler,
    LogTestCommand,
    LogTestEvent,
)

from boss_bus.message_bus import MessageBus
from boss_bus.middleware.log import MessageLogger


class TestMessageBusLogger:
    def test_log_commands_log_before_and_after_execution(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus()

        bus.execute(LogTestCommand("Logging..."), LoggingCommandHandler())
        assert len(caplog.record_tuples) == 3
        assert caplog.record_tuples[1][2] == "Logging..."

    def test_none_log_commands_do_not_log_messages(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus()

        bus.execute(PrintCommand("Logging..."), PrintCommandHandler())
        assert len(caplog.record_tuples) == 0

    def test_log_events_log_before_and_after_execution(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus()

        bus.dispatch(LogTestEvent("Logging..."), [LoggingEventHandler()])
        assert len(caplog.record_tuples) == 3
        assert caplog.record_tuples[1][2] == "Logging..."

    def test_none_log_events_do_not_log_messages(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        bus = MessageBus()

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
        print(caplog.record_tuples)
        assert caplog.record_tuples[0][0] == "first"
        assert caplog.record_tuples[1][0] == "second"
        assert caplog.record_tuples[3][0] == "second"
        assert caplog.record_tuples[4][0] == "first"
