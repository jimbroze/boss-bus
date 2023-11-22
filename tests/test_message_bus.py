import pytest
from _pytest.capture import CaptureFixture
from typeguard import TypeCheckError

from boss_bus.command_bus import CommandBus
from boss_bus.event_bus import EventBus
from boss_bus.message_bus import MessageBus
from tests.examples import (
    ExampleEvent,
    ExampleEventHandler,
    OtherEventHandler,
    PrintCommand,
    PrintCommandHandler,
    ReturnCommand,
    ReturnCommandHandler,
)


class TestMessageBus:
    def test_can_created_with_custom_command_and_event_bus(self) -> None:
        command_bus = CommandBus()
        event_bus = EventBus()
        bus = MessageBus(command_bus=command_bus, event_bus=event_bus)

        assert bus.command_bus == command_bus
        assert bus.event_bus == event_bus

    def test_execute_executes_a_command(self) -> None:
        command = PrintCommand("Test the bus")
        handler = PrintCommandHandler()
        bus = MessageBus()

        bus.execute(command, handler)

    def test_execute_can_return_a_value(self) -> None:
        command = ReturnCommand("Test the bus")
        handler = ReturnCommandHandler()
        bus = MessageBus()

        result = bus.execute(command, handler)

        assert result == "Test the bus"

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
        command = PrintCommand("Test the bus")
        handler = PrintCommandHandler()
        bus = MessageBus()

        with pytest.raises(TypeCheckError):
            bus.dispatch(command, handler)  # type: ignore[arg-type, type-var]

    def test_command_registers_with_the_command_bus(self) -> None:
        handler = PrintCommandHandler()
        bus = MessageBus()

        bus.register_command(PrintCommand, handler)

        assert PrintCommand in bus.command_bus._handlers  # noqa: SLF001

    def test_event_registers_with_the_event_bus(self) -> None:
        handler = ExampleEventHandler()
        bus = MessageBus()

        bus.register_event(ExampleEvent, [handler])

        assert ExampleEvent in bus.event_bus._handlers  # noqa: SLF001

    def test_command_deregisters_with_the_command_bus(self) -> None:
        command_bus = CommandBus()
        bus = MessageBus(command_bus=command_bus)
        handler = PrintCommandHandler()

        bus.register_command(PrintCommand, handler)
        bus.deregister_command(PrintCommand)

        assert PrintCommand not in command_bus._handlers  # noqa: SLF001

    def test_event_deregisters_with_the_event_bus(self) -> None:
        handler = ExampleEventHandler()
        event_bus = EventBus()
        bus = MessageBus(event_bus=event_bus)

        bus.register_event(ExampleEvent, [handler])
        bus.deregister_event(ExampleEvent, [handler])

        assert handler not in event_bus._handlers.get(ExampleEvent, [])  # noqa: SLF001

    def test_all_events_deregister_if_no_handlers_provided(self) -> None:
        event_bus = EventBus()
        bus = MessageBus(event_bus=event_bus)

        bus.register_event(ExampleEvent, [ExampleEventHandler, OtherEventHandler])

        bus.deregister_event(ExampleEvent)

        assert bus.has_handlers(ExampleEvent) == 0

    def test_is_registered_returns_false_for_command_not_registered(self) -> None:
        bus = MessageBus()

        assert bus.is_registered(ReturnCommand) is False

    def test_has_handlers_returns_zero_for_event_not_registered(self) -> None:
        bus = MessageBus()

        assert bus.has_handlers(ExampleEvent) == 0

    def test_default_loader_instantiates_event_classes(
        self, capsys: CaptureFixture[str]
    ) -> None:
        bus = MessageBus()
        event = ExampleEvent("Testing...")

        bus.register_event(ExampleEvent, [ExampleEventHandler])
        bus.dispatch(event)

        captured = capsys.readouterr()
        assert captured.out == "Testing...\n"

    def test_default_loader_instantiates_command_classes(
        self, capsys: CaptureFixture[str]
    ) -> None:
        bus = MessageBus()
        command = PrintCommand("Testing...")

        bus.register_command(PrintCommand, PrintCommandHandler)
        bus.execute(command)

        captured = capsys.readouterr()
        assert captured.out == "Testing...\n"

    def test_default_loader_can_be_used_to_deregister_events(self) -> None:
        bus = MessageBus()

        bus.register_event(ExampleEvent, [ExampleEventHandler(), OtherEventHandler()])
        bus.deregister_event(ExampleEvent, [ExampleEventHandler])

        assert bus.has_handlers(ExampleEvent) == 1
