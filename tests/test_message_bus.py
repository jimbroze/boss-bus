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

    def test_command_registers_with_the_command_bus(self) -> None:
        handler = ExampleCommandHandler()
        bus = MessageBus()

        bus.register_command(ExampleCommand, handler)

        assert ExampleCommand in bus.command_bus._handlers  # noqa: SLF001

    def test_event_registers_with_the_event_bus(self) -> None:
        handler = ExampleEventHandler()
        bus = MessageBus()

        bus.register_event(ExampleEvent, [handler])

        assert ExampleEvent in bus.event_bus._handlers  # noqa: SLF001

    def test_command_deregisters_with_the_command_bus(self) -> None:
        command_bus = CommandBus()
        bus = MessageBus(command_bus=command_bus)
        handler = ExampleCommandHandler()

        bus.register_command(ExampleCommand, handler)
        bus.deregister_command(ExampleCommand)

        assert ExampleCommand not in command_bus._handlers  # noqa: SLF001

    def test_event_deregisters_with_the_event_bus(self) -> None:
        handler = ExampleEventHandler()
        event_bus = EventBus()
        bus = MessageBus(event_bus=event_bus)

        bus.register_event(ExampleEvent, [handler])
        bus.deregister_event(ExampleEvent, [handler])

        assert handler not in event_bus._handlers.get(ExampleEvent, [])  # noqa: SLF001
