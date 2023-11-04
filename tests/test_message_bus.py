from boss_bus.command_bus import CommandBus
from boss_bus.message_bus import MessageBus
from tests.examples import ExampleCommand, ExampleCommandHandler


class TestMessageBus:
    def test_can_created_with_custom_command_bus(self) -> None:
        command_bus = CommandBus()
        bus = MessageBus(command_bus=command_bus)

        bus.command_bus = command_bus

    def test_execute_executes_a_command(self) -> None:
        command = ExampleCommand("Test the bus")
        handler = ExampleCommandHandler()
        bus = MessageBus()

        bus.execute(command, handler)
