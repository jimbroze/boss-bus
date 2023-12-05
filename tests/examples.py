import time

from boss_bus.bus import MessageBus
from boss_bus.command import Command, CommandHandler
from boss_bus.event import Event, EventHandler


class ExampleEvent(Event):
    """A type of event purely for use in tests."""

    def __init__(self, event_data: str):
        """Creates an event for tests."""
        self.event_data = event_data

    def print_event_data(self) -> None:
        print(self.event_data)


class ExampleEventHandler(EventHandler[ExampleEvent]):
    """An event handler purely for use in tests."""

    def handle(self, event: ExampleEvent) -> None:
        """Handle a test event."""
        event.print_event_data()


class OtherEventHandler(EventHandler[ExampleEvent]):
    """An event handler purely for use in tests."""

    def handle(self, event: ExampleEvent) -> None:
        """Handle a test event."""


class PrintCommand(Command):
    """A command purely for use in tests."""

    def __init__(self, command_data: str):
        """Creates a command for tests."""
        self.command_data = command_data

    def print_command_data(self) -> None:
        print(self.command_data)


class PrintCommandHandler(CommandHandler[PrintCommand]):
    """A command handler purely for use in tests."""

    def handle(self, command: PrintCommand) -> None:
        """Handle a test command."""
        command.print_command_data()


class ReturnCommand(Command):
    """A command purely for use in tests."""

    def __init__(self, command_data: str):
        """Creates a command for tests."""
        self.command_data = command_data


class ReturnCommandHandler(CommandHandler[ReturnCommand]):
    """A command handler purely for use in tests."""

    def handle(self, command: ReturnCommand) -> str:
        """Handle a test command."""
        return command.command_data


class NestedCommand(Command):
    """A command purely for use in tests."""

    def __init__(self, command_data: str):
        """Creates a command for tests."""
        self.command_data = command_data


class NestedCommandHandler(CommandHandler[NestedCommand]):
    """A command handler purely for use in tests."""

    def __init__(self, message_bus: MessageBus):
        """Creates a command for tests."""
        self.message_bus = message_bus

    def handle(self, command: NestedCommand) -> str:
        """Handle a test command."""
        result: str = self.message_bus.execute(
            ReturnCommand(command.command_data), ReturnCommandHandler()
        )
        return result


class ReturnTimeCommand(Command):
    pass


class ReturnTimeCommandHandler(CommandHandler[ReturnTimeCommand]):
    def handle(self, command: ReturnTimeCommand) -> float:  # noqa: ARG002
        """Handle a test command."""
        time.sleep(0.05)
        return time.time()
