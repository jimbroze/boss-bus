from __future__ import annotations

import logging
from typing import Any

from boss_bus.command_bus import CommandHandler
from boss_bus.interface import SupportsHandle
from boss_bus.middleware.lock import BusLocker, LockingCommand, LockingEvent
from boss_bus.middleware.log import LoggingCommand, LoggingEvent, LoggingMessage


class LogTestCommand(LoggingCommand):
    def __init__(self, command_data: str):
        """Creates a command for tests."""
        self.command_data = command_data

    def log_command_data(self) -> None:
        logging.info(self.command_data)


class LogErrorCommand(LogTestCommand):
    def log_command_data(self) -> None:
        raise Exception


class LoggingCommandHandler(CommandHandler[LogTestCommand]):
    def handle(self, command: LogTestCommand) -> None:
        command.log_command_data()


class LogTestEvent(LoggingEvent):
    def __init__(self, event_data: str):
        """Creates an event for tests."""
        self.event_data = event_data

    def log_event_data(self) -> None:
        logging.info(self.event_data)


class LogErrorEvent(LogTestEvent):
    def log_event_data(self) -> None:
        raise Exception


class LoggingEventHandler(SupportsHandle):
    def handle(self, event: LogTestEvent) -> None:
        event.log_event_data()


class LockTestCommand(LockingCommand):
    pass


class LockingCommandHandler(CommandHandler[LockTestCommand]):
    def __init__(self, locker: BusLocker):
        self.locker = locker

    def handle(self, command: LockTestCommand) -> None:  # noqa: ARG002
        def bus(c: LoggingMessage) -> Any:
            LoggingCommandHandler().handle(c)  # type: ignore[arg-type]

        logging.info("Pre-nested call")
        self.locker.handle(LogTestCommand("Nested call"), bus)
        logging.info("Post-nested call")


class LockTestEvent(LockingEvent):
    pass


class LockingEventHandler(SupportsHandle):
    def __init__(self, locker: BusLocker):
        self.locker = locker

    def handle(self, event: LockTestEvent) -> None:  # noqa: ARG002
        def bus(e: LoggingMessage) -> Any:
            LoggingEventHandler().handle(e)  # type: ignore[arg-type]

        logging.info("Pre-nested call")
        self.locker.handle(LogTestEvent("Nested call"), bus)
        logging.info("Post-nested call")
