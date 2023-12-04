from __future__ import annotations

from typing import TYPE_CHECKING, Union

import pytest
from typeguard import TypeCheckError

from boss_bus.command import (
    Command,
    CommandBus,
    CommandHandler,
    InvalidHandlerError,
    TooManyHandlersError,
)
from boss_bus.interface import MissingHandlerError
from tests.examples import (
    ReturnCommand,
    ReturnCommandHandler,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


class ExplosionCommand(Command):
    def print_command_data(self) -> None:
        print("It went boom")


class FloodCommand(Command):
    def print_command_data(self) -> None:
        print("It got wet")


class AnyCommandHandler(CommandHandler[Command]):
    def handle(self, command: Command) -> None:
        pass


class UnionCommandHandler(CommandHandler[Union[ExplosionCommand, FloodCommand]]):
    def handle(self, command: ExplosionCommand | FloodCommand) -> None:
        command.print_command_data()


class ExplosionCommandHandler(CommandHandler[ExplosionCommand]):
    def handle(self, command: ExplosionCommand) -> None:
        command.print_command_data()


class SecondExplosionCommandHandler(CommandHandler[ExplosionCommand]):
    def handle(self, command: ExplosionCommand) -> None:
        pass


class TestCommandBus:
    def test_execute_accepts_a_specific_command(self) -> None:
        command = ExplosionCommand()
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        bus.execute(command, handler)

    # noinspection PyTypeChecker
    def test_execute_does_not_accept_a_non_specific_command(self) -> None:
        command = ExplosionCommand()
        handler = AnyCommandHandler()
        bus = CommandBus()

        with pytest.raises(InvalidHandlerError):
            bus.execute(command, handler)

    def test_execute_does_not_accept_an_invalid_handler_for_the_command(self) -> None:
        command = FloodCommand()
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        with pytest.raises(InvalidHandlerError):
            bus.execute(command, handler)  # type: ignore[misc]

    def test_execute_does_not_accept_multiple_handlers(self) -> None:
        command = ExplosionCommand()
        handler1 = ExplosionCommandHandler()
        handler2 = SecondExplosionCommandHandler()
        bus = CommandBus()

        with pytest.raises(TypeCheckError):
            bus.execute(command, [handler1, handler2])  # type: ignore[arg-type]

    def test_execute_cannot_execute_a_command_with_no_handlers(
        self,
    ) -> None:
        command = ExplosionCommand()
        bus = CommandBus()

        with pytest.raises(MissingHandlerError):
            bus.execute(command)

    def test_execute_finds_a_previously_registered_command(
        self, capsys: CaptureFixture[str]
    ) -> None:
        command = ExplosionCommand()
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        bus.register_handler(ExplosionCommand, handler)

        bus.execute(command)

        captured = capsys.readouterr()
        assert captured.out == "It went boom\n"

    def test_execute_does_not_accept_a_handler_if_one_is_already_registered(
        self,
    ) -> None:
        command = ExplosionCommand()
        handler1 = ExplosionCommandHandler()
        handler2 = SecondExplosionCommandHandler()
        bus = CommandBus()

        bus.register_handler(ExplosionCommand, handler1)

        with pytest.raises(TooManyHandlersError):
            bus.execute(command, handler2)

    def test_execute_accepts_a_union_of_commands(
        self, capsys: CaptureFixture[str]
    ) -> None:
        command = FloodCommand()
        handler = UnionCommandHandler()
        bus = CommandBus()

        bus.execute(command, handler)

        captured = capsys.readouterr()
        assert captured.out == "It got wet\n"

    def test_execute_can_return_a_value(self) -> None:
        command = ReturnCommand("Returned a value")
        handler = ReturnCommandHandler()
        bus = CommandBus()

        result = bus.execute(command, handler)

        assert result == "Returned a value"

    def test_register_handler_requires_handlers_to_be_provided(self) -> None:
        bus = CommandBus()

        with pytest.raises(TypeError):
            bus.register_handler(ExplosionCommand)  # type: ignore[call-arg]

    def test_register_handler_requires_command_type_to_be_a_type(self) -> None:
        command = ExplosionCommand()
        handler1 = ExplosionCommandHandler()
        bus = CommandBus()

        with pytest.raises(TypeCheckError):
            bus.register_handler(command, handler1)  # type: ignore[arg-type]

    def test_register_handler_will_not_register_an_invalid_handler_for_the_command(
        self,
    ) -> None:
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        with pytest.raises(InvalidHandlerError):
            bus.register_handler(FloodCommand, handler)  # type: ignore[misc]

    def test_register_handler_will_not_accept_multiple_handlers(self) -> None:
        command = ExplosionCommand()
        handler1 = ExplosionCommandHandler()
        handler2 = SecondExplosionCommandHandler()
        bus = CommandBus()

        with pytest.raises(TypeCheckError):
            bus.register_handler(command, [handler1, handler2])  # type: ignore[arg-type]

    def test_register_handler_will_not_register_an_uninstantiated_handler(self) -> None:
        bus = CommandBus()

        with pytest.raises(TypeCheckError):
            bus.register_handler(ExplosionCommand, [ExplosionCommandHandler])  # type: ignore[arg-type]

    def test_remove_handler_removes_handler_for_a_given_command_and_deletes_key(
        self,
    ) -> None:
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        bus.register_handler(ExplosionCommand, handler)
        assert ExplosionCommand in bus._handlers  # noqa: SLF001

        bus.remove_handler(ExplosionCommand)

        assert ExplosionCommand not in bus._handlers  # noqa: SLF001

    def test_remove_handler_throws_exception_if_command_is_not_registered(
        self,
    ) -> None:
        bus = CommandBus()

        with pytest.raises(MissingHandlerError):
            bus.remove_handler(ExplosionCommand)

    def test_is_registered_returns_false_for_non_registered_command(
        self,
    ) -> None:
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        bus.register_handler(ExplosionCommand, handler)

        assert bus.is_registered(FloodCommand) is False

    def test_is_registered_returns_true_for_registered_command(
        self,
    ) -> None:
        handler = ExplosionCommandHandler()
        bus = CommandBus()

        bus.register_handler(ExplosionCommand, handler)

        assert bus.is_registered(ExplosionCommand) is True
