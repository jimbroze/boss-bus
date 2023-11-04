import pytest
from typeguard import TypeCheckError

from boss_bus.command_bus import CommandBus
from boss_bus.event_bus import EventBus
from boss_bus.message_bus import MessageBus
from tests.examples import (
    ExampleCommand,
    ExampleCommandHandler,
    ExampleEvent,
    ExampleEventHandler,
)


class TestMessageBus:
    def test_can_created_with_custom_command_and_event_bus(self) -> None:
        command_bus = CommandBus()
        event_bus = EventBus()
        bus = MessageBus(command_bus=command_bus, event_bus=event_bus)

        assert bus.command_bus == command_bus
        assert bus.event_bus == event_bus

    def test_execute_executes_a_command(self) -> None:
        command = ExampleCommand("Test the bus")
        handler = ExampleCommandHandler()
        bus = MessageBus()

        bus.execute(command, handler)

    def test_an_event_cannot_be_executed(self) -> None:
        event = ExampleEvent("Test the bus")
        handler = ExampleEventHandler()
        bus = MessageBus()

        with pytest.raises(TypeCheckError):
            bus.execute(event, handler)  # type: ignore[type-var, arg-type]

    def test_an_event_can_be_dispatched(self) -> None:
        event = ExampleEvent("Test the bus")
        handler = ExampleEventHandler()
        bus = MessageBus()

        bus.dispatch(event, [handler])

    def test_a_command_cannot_be_dispatched(self) -> None:
        command = ExampleCommand("Test the bus")
        handler = ExampleCommandHandler()
        bus = MessageBus()

        with pytest.raises(TypeCheckError):
            bus.dispatch(command, handler)  # type: ignore[arg-type]
