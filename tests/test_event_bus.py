from __future__ import annotations

from boss_bus.event_bus import Event
from boss_bus.event_bus import EventHandler


class ExplosionEvent(Event):
    def get_event_data(self) -> str:
        return "It went boom"


class FloodEvent:
    def get_event_data(self) -> str:
        return "It got wet"


class ExplosionEventHandler(EventHandler[ExplosionEvent]):
    def handle(self, event: ExplosionEvent) -> str:
        return event.get_event_data()


class TestEventHandler:
    def test_event_handler_handles_a_valid_event(self) -> None:
        event = ExplosionEvent()
        handler = ExplosionEventHandler()

        result = handler.handle(event)

        assert result == "It went boom"

    def test_event_handler_does_not_restrict_event_type(self) -> None:
        """Remove responsibility from the handlers and allow duck typing.

        While this will not pass static type checking, the event type is not enforced
        at runtime. I may review this requirement in the future, particularly if
        the interface of the Event class becomes more complex.
        """
        event = FloodEvent()
        handler = ExplosionEventHandler()

        result = handler.handle(event)  # type: ignore

        assert result == "It got wet"
