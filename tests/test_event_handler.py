from __future__ import annotations

from typing import TYPE_CHECKING

from boss_bus.event_bus import (
    Event,
)
from boss_bus.interface import IMessageHandler

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


class ExplosionEvent(Event):
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
        pass


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
        by handlers at runtime. Specific handlers are created by users, so it's
        difficult to enforce type checking. Instead, this responsibility
        is handled by the Event Bus.
        """
        event = FloodEvent()
        handler = ExplosionEventHandler()

        handler.handle(event)  # type: ignore

        captured = capsys.readouterr()
        assert captured.out == "It got wet\n"
