"""
This file is no longer testing much functionality within the project since
the Event Handler interface was removed. As the structure becomes more complex,
they may be useful again.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from boss_bus.interface import SupportsHandle

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


class ExplosionMessage:
    def print_message_data(self) -> None:
        print("It went boom")


class FloodMessage:
    def print_message_data(self) -> None:
        print("It got wet")


class AnyMessageHandler(SupportsHandle):
    def handle(self, message: Any) -> None:  # noqa: ARG002
        print("Hi")


class ExplosionMessageHandler(SupportsHandle):
    def handle(self, message: ExplosionMessage) -> None:
        message.print_message_data()


class SecondExplosionMessageHandler(SupportsHandle):
    def handle(self, message: ExplosionMessage) -> None:
        pass


class TestMessageHandler:
    def test_non_specific_message_handler_can_handle_an_message(
        self, capsys: CaptureFixture[str]
    ) -> None:
        message = ExplosionMessage()
        handler = AnyMessageHandler()

        handler.handle(message)

        captured = capsys.readouterr()
        assert captured.out == "Hi\n"

    def test_specific_message_handler_can_handle_a_valid_message(
        self, capsys: CaptureFixture[str]
    ) -> None:
        message = ExplosionMessage()
        handler = ExplosionMessageHandler()

        handler.handle(message)

        captured = capsys.readouterr()
        assert captured.out == "It went boom\n"

    def test_message_handler_does_not_restrict_message_type(
        self, capsys: CaptureFixture[str]
    ) -> None:
        """Remove responsibility from the handlers and allow duck typing.

        This will not pass static type checking but the message type is not enforced
        by handlers at runtime. Specific handlers are created by users, so it's
        difficult to enforce type checking. Instead, this responsibility
        is handled by the Message Bus.
        """
        message = FloodMessage()
        handler = ExplosionMessageHandler()

        handler.handle(message)  # type: ignore

        captured = capsys.readouterr()
        assert captured.out == "It got wet\n"
