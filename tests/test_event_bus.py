from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typeguard import TypeCheckError

from boss_bus.event_bus import (
    Event,
    EventBus,
    MissingEventError,
)
from boss_bus.handler import MissingHandlerError
from boss_bus.interface import IMessageHandler

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


class ExplosionEvent(Event):
    def print_event_data(self) -> None:
        print("It went boom")


class FloodEvent:
    pass


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


class TestEventBus:
    def test_dispatch_accepts_a_non_specific_event(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler = AnyEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler])

        captured = capsys.readouterr()
        assert captured.out == "Hi\n"

    def test_dispatch_accepts_a_list_of_handlers(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.dispatch(event, [handler1, handler2])

        captured = capsys.readouterr()
        assert captured.out == "It went boom\nIt went boom\nagain\n"

    def test_dispatch_accepts_a_tuple_of_handlers(
        self, capsys: CaptureFixture[str]
    ) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.dispatch(event, (handler1, handler2))

        captured = capsys.readouterr()
        assert captured.out == "It went boom\nIt went boom\nagain\n"

    def test_dispatch_will_not_accept_an_invalid_event(self) -> None:
        event = FloodEvent()
        handler = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(TypeCheckError):
            bus.dispatch(event, [handler])  # type: ignore[arg-type]

    def test_dispatch_will_not_throw_exception_if_dispatching_an_event_with_no_handlers(
        self,
    ) -> None:
        event = ExplosionEvent()
        bus = EventBus()

        bus.dispatch(event, [])

    def test_dispatch_uses_previously_registered_events(
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

    def test_dispatch_combines_registered_and_passed_events(
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
        assert captured.out == "It went boom\nIt went boom\nagain\nHi\n"

    def test_add_handlers_requires_handlers_to_be_provided(self) -> None:
        bus = EventBus()

        with pytest.raises(TypeError) as e:
            bus.add_handlers(ExplosionEvent, [])

        assert str(e.value) == "add_handlers() requires at least one handler"

    def test_add_handlers_requires_event_type_to_be_a_type(self) -> None:
        event = ExplosionEvent()
        handler1 = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(TypeCheckError):
            bus.add_handlers(event, [handler1])  # type: ignore[arg-type]

    def test_add_handlers_will_not_register_an_invalid_event_and_handler(self) -> None:
        handler = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(TypeCheckError):
            bus.add_handlers(FloodEvent, [handler])  # type: ignore[arg-type]

    def test_remove_handlers_can_remove_all_handlers(self) -> None:
        handler1 = ExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler1])

        bus.remove_handlers(ExplosionEvent)

        assert ExplosionEvent not in bus._handlers  # noqa: SLF001

    def test_remove_handlers_can_remove_specific_handlers(self) -> None:
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler1, handler2])

        bus.remove_handlers(ExplosionEvent, [handler1])

        assert ExplosionEvent in bus._handlers  # noqa: SLF001
        assert len(bus._handlers[ExplosionEvent]) == 1  # noqa: SLF001

    def test_remove_handlers_deletes_event_key_if_all_handlers_are_removed_specifically(
        self,
    ) -> None:
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler1, handler2])

        bus.remove_handlers(ExplosionEvent, [handler1, handler2])

        assert ExplosionEvent not in bus._handlers  # noqa: SLF001

    def test_remove_handlers_will_not_accept_an_invalid_event_and_handler(self) -> None:
        handler = ExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler])

        with pytest.raises(TypeCheckError):
            bus.remove_handlers(FloodEvent, [handler])  # type: ignore[arg-type]

    def test_remove_handlers_throws_exception_if_handler_is_not_registered(
        self,
    ) -> None:
        handler1 = ExplosionEventHandler()
        handler2 = SecondExplosionEventHandler()
        bus = EventBus()

        bus.add_handlers(ExplosionEvent, [handler1])

        with pytest.raises(MissingHandlerError):
            bus.remove_handlers(ExplosionEvent, [handler2])

    def test_remove_handlers_throws_exception_if_event_is_not_registered(self) -> None:
        handler = ExplosionEventHandler()
        bus = EventBus()

        with pytest.raises(MissingEventError):
            bus.remove_handlers(ExplosionEvent, [handler])
