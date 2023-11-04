"""The main entrypoint to the Boss-Bus package.

Classes:

    MessageBus
"""
from __future__ import annotations

from boss_bus.command_bus import CommandBus, CommandHandler, SpecificCommand


class MessageBus:
    """Forwards events and commands to their associated buses.

    Example:
        >>> from tests.examples import ExampleCommand, ExampleCommandHandler
        >>> bus = MessageBus()
        >>> test_handler = ExampleCommandHandler()
        >>> test_command = ExampleCommand("Testing...")
        >>>
        >>> bus.execute(test_command, test_handler)
        Testing...
    """

    def __init__(self, command_bus: CommandBus | None = None) -> None:
        """Creates a Message Bus."""
        self.command_bus = command_bus if command_bus is not None else CommandBus()

    def execute(
        self,
        command: SpecificCommand,
        handler: CommandHandler[SpecificCommand] | None = None,
    ) -> None:
        """Forwards a command to a CommandBus for execution.

        Example:
            >>> from tests.examples import ExampleCommand, ExampleCommandHandler
            >>> bus = MessageBus()
            >>> test_handler = ExampleCommandHandler()
            >>> test_command = ExampleCommand("Testing...")
            >>>
            >>> bus.execute(test_command, test_handler)
            Testing...
        """
        self.command_bus.execute(command, handler)
