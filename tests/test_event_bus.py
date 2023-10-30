from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typeguard import TypeCheckError

from boss_bus.event_bus import Event, EventBus, MissingHandlerError
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
    def test_event_bus_can_handle_a_non_specific_event(self) -> None:
        event = ExplosionEvent()
        handler = AnyEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler])

    def test_event_bus_can_handle_a_valid_event_with_multiple_handlers(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler1, handler2])

        captured = capsys.readouterr()
        assert captured.out == "It went boom\nIt went boom\nagain\n"

    def test_event_bus_can_handle_subclasses_of_a_valid_event(self) -> None:
        event = BigExplosionEvent()
        handler = ExplosionEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler])

    def test_event_bus_will_not_handle_an_invalid_event(self) -> None:
        event = FloodEvent()
        handler = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(TypeCheckError):
            bus.dispatch(event, [handler])  # type: ignore

    def test_event_bus_will_throw_exception_if_handling_a_missing_handler(self) -> None:
        event = ExplosionEvent()
        bus = EventBus()

        with pytest.raises(MissingHandlerError):
            bus.dispatch(event, [])
