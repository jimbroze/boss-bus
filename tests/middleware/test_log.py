from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pytest
from tests.middleware.examples import (
    LogErrorCommand,
    LogErrorEvent,
    LoggingCommandHandler,
    LoggingEventHandler,
    LogTestCommand,
    LogTestEvent,
)

from boss_bus.middleware.log import LoggingMessage, MessageLogger

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


class TestLog:
    def test_message_logger_logs_before_and_after_message(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        logger = MessageLogger()
        command = LogTestCommand("Logging...")

        def bus(c: LoggingMessage) -> Any:
            LoggingCommandHandler().handle(c)  # type: ignore[arg-type]

        logger.handle(command, bus)

        assert len(caplog.record_tuples) == 3
        assert caplog.record_tuples[1][2] == "Logging..."

    def test_a_custom_logger_can_be_provided(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        custom_logger = logging.getLogger("test")
        logger = MessageLogger(custom_logger)
        command = LogTestCommand("Logging...")

        def bus(c: LoggingMessage) -> Any:
            LoggingCommandHandler().handle(c)  # type: ignore[arg-type]

        logger.handle(command, bus)

        assert caplog.record_tuples[0][0] == "test"

    def test_commands_log_with_correct_verbs(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        logger = MessageLogger()
        command = LogTestCommand("Logging...")

        def bus(c: LoggingMessage) -> Any:
            LoggingCommandHandler().handle(c)  # type: ignore[arg-type]

        logger.handle(command, bus)

        assert "executing" in caplog.record_tuples[0][2].lower()
        assert "command" in caplog.record_tuples[0][2].lower()
        assert "executed" in caplog.record_tuples[2][2].lower()
        assert "command" in caplog.record_tuples[2][2].lower()

    def test_events_log_with_correct_verbs(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        logger = MessageLogger()
        event = LogTestEvent("Logging...")

        def bus(c: LoggingMessage) -> Any:
            LoggingEventHandler().handle(c)  # type: ignore[arg-type]

        logger.handle(event, bus)

        assert "dispatching" in caplog.record_tuples[0][2].lower()
        assert "event" in caplog.record_tuples[0][2].lower()
        assert "dispatched" in caplog.record_tuples[2][2].lower()
        assert "event" in caplog.record_tuples[2][2].lower()

    def test_commands_log_if_an_error_is_raised(
        self, caplog: LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        logger = MessageLogger()
        command: LoggingMessage = LogErrorCommand("Logging...")

        def bus(c: LoggingMessage) -> Any:
            LoggingCommandHandler().handle(c)  # type: ignore[arg-type]

        with pytest.raises(Exception):  # noqa: B017, PT011
            logger.handle(command, bus)

        assert len(caplog.record_tuples) == 2
        assert "Failed executing" in caplog.record_tuples[1][2]

    def test_events_log_if_an_error_is_raised(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        logger = MessageLogger()
        event = LogErrorEvent("Logging...")

        def bus(e: LoggingMessage) -> Any:
            LoggingEventHandler().handle(e)  # type: ignore[arg-type]

        with pytest.raises(Exception):  # noqa: B017, PT011
            logger.handle(event, bus)

        assert len(caplog.record_tuples) == 2
        assert "Failed dispatching" in caplog.record_tuples[1][2]
