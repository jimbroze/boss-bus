from __future__ import annotations

from boss_bus.event_bus import Event
from boss_bus.event_bus import EventHandler


class ExplosionEvent(Event):
    def get_event_data(self) -> str:
        return "It went boom"


class FloodEvent(Event):
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
