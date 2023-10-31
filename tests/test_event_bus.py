from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typeguard import TypeCheckError

from boss_bus.event_bus import Event, EventBus
from boss_bus.interface import IMessageHandler

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


class ExplosionEvent(Event):
    def print_event_data(self) -> None:
        print("It went boom")


class BigExplosionEvent(ExplosionEvent):
    def print_event_data(self) -> None:
        print("It went boom")


class FloodEvent:
    def print_event_data(self) -> None:
        print("It got wet")


class AnyEventHandler(IMessageHandler):
    def handle(self, event: Event) -> None:  # noqa: ARG002
        print("Hi")


class ExplosionEventHandler(IMessageHandler):
    def handle(self, event: ExplosionEvent) -> None:
        event.print_event_data()


class SecondExplosionEventHandler(IMessageHandler):
    def handle(self, event: ExplosionEvent) -> None:
        event.print_event_data()
        print("again")


class TestEventHandler:
    def test_non_specific_event_handler_can_handle_an_event(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler = AnyEventHandler()

        handler.handle(event)

        captured = capsys.readouterr()
        assert captured.out == "Hi\n"

    def test_specific_event_handler_can_handle_a_valid_event(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler = ExplosionEventHandler()

        handler.handle(event)

        captured = capsys.readouterr()
        assert captured.out == "It went boom\n"

    def test_event_handler_does_not_restrict_event_type(
        self, capsys: CaptureFixture[str]
    ) -> None:
        """Remove responsibility from the handlers and allow duck typing.

        This will not pass static type checking but the event type is not enforced
        by handlers at runtime. Specific handlers are created by users so it's
        difficult to enforce type checking. Instead, this responsibility
        is handled by the Event Bus.
        """
        event = FloodEvent()
        handler = ExplosionEventHandler()

        handler.handle(event)  # type: ignore

        captured = capsys.readouterr()
        assert captured.out == "It got wet\n"


class TestEventBus:
    def test_event_bus_can_dispatch_a_non_specific_event(self) -> None:
        event = ExplosionEvent()
        handler = AnyEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler])

    def test_event_bus_can_dispatch_a_valid_event_with_multiple_handlers(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler1, handler2])

        captured = capsys.readouterr()
        assert captured.out == "It went boom\nIt went boom\nagain\n"

    def test_event_bus_can_dispatch_subclasses_of_a_valid_event(self) -> None:
        event = BigExplosionEvent()
        handler = ExplosionEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler])

    def test_event_bus_will_not_dispatch_an_invalid_event(self) -> None:
        event = FloodEvent()
        handler = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(TypeCheckError):
            bus.dispatch(event, [handler])  # type: ignore

    def test_event_bus_will_not_throw_exception_if_dispatching_an_event_with_no_handlers(
        self,
    ) -> None:
        event = ExplosionEvent()
        bus = EventBus()

        bus.dispatch(event, [])

    def test_event_bus_can_dispatch_events_previously_registered(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler1, handler2])

        bus.dispatch(event)

        captured = capsys.readouterr()
        assert captured.out == "It went boom\nIt went boom\nagain\n"

    def test_event_bus_can_combine_registered_and_passed_events(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler1, handler2])

        handler3 = AnyEventHandler()

        bus.dispatch(event, [handler3])

        captured = capsys.readouterr()
        assert captured.out == "Hi\nIt went boom\nIt went boom\nagain\n"

    def test_add_handlers_require_handlers_to_be_provided(self) -> None:
        bus = EventBus()

        with pytest.raises(TypeError) as e:
            bus.add_handlers(ExplosionEvent, [])

        assert str(e.value) == "add_handlers() requires at least one handler"

    def test_add_handlers_require_event_type_to_be_a_type(self) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(TypeError) as e:
            bus.add_handlers(event, [handler1])  # type: ignore

        assert str(e.value) == (
            "event_type passed to add_handlers must be a "
            "type. Got '<class 'tests.test_event_bus.ExplosionEvent'>"
        )
