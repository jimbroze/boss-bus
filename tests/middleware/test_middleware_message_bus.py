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
