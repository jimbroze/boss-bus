from __future__ import annotations

from _pytest.capture import CaptureFixture

from boss_bus.event_bus import Event
from boss_bus.interface import IMessageHandler


class ExplosionEvent(Event):
    def print_event_data(self) -> None:
        print("It went boom")


class FloodEvent:
    def print_event_data(self) -> None:
        print("It got wet")


class ExplosionEventHandler(IMessageHandler):
    def handle(self, event: ExplosionEvent) -> None:
        event.print_event_data()


class TestEventHandler:
    def test_event_handler_handles_a_valid_event(
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

        While this will not pass static type checking, the event type is not enforced
        at runtime. I may review this requirement in the future, particularly if
        the interface of the Event class becomes more complex.
        """
        event = FloodEvent()
        handler = ExplosionEventHandler()

        handler.handle(event)  # type: ignore

        captured = capsys.readouterr()
        assert captured.out == "It got wet\n"
