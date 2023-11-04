from boss_bus.command_bus import Command, CommandHandler
from boss_bus.event_bus import Event
from boss_bus.interface import SupportsHandle


class TestEvent(Event):
    """A type of event purely for use in tests."""

    def __init__(self, event_data: str):
        """Creates an event for tests."""
        self.event_data = event_data

    def print_event_data(self) -> None:
        print(self.event_data)


class TestEventHandler(SupportsHandle):
    """An event handler purely for use in tests."""

    def handle(self, event: TestEvent) -> None:
        """Handle a test event."""
        event.print_event_data()


class TestCommand(Command):
    """A type of command purely for use in tests."""

    def __init__(self, command_data: str):
        """Creates a command for tests."""
        self.command_data = command_data

    def print_command_data(self) -> None:
        print(self.command_data)


class TestCommandHandler(CommandHandler[TestCommand]):
    """A command handler purely for use in tests."""

    def handle(self, command: TestCommand) -> None:
        """Handle a test command."""
        command.print_command_data()
