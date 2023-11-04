from boss_bus.message_bus import MessageBus
from tests.examples import ExampleCommand, ExampleCommandHandler


class TestMessageBus:
    def test_execute_executes_a_command(self) -> None:
        command = ExampleCommand("Test the bus")
        handler = ExampleCommandHandler()
        bus = MessageBus()

        bus.execute(command, handler)
