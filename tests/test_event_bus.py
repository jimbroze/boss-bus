from __future__ import annotations

from boss_bus.event_bus import Event
from boss_bus.event_bus import EventHandler


class ExplosionEvent(Event):
    pass


class ExplosionEventHandler(EventHandler):
    def handle(self, event: ExplosionEvent) -> str:
        return "It went boom"


class TestEventHandler:
    def test_event_handler_handles_valid_event(self) -> None:
        event = ExplosionEvent()
        handler = ExplosionEventHandler()

        result = handler.handle(event)

        assert result == "It went boom"
