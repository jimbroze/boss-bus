"""An optional module that allows using the DI container Lagom, as a class Loader."""

from __future__ import annotations

from typing import Type, overload

from lagom import Container

from boss_bus.loader import ClassLoader, obj


class LagomLoader(ClassLoader):
    """Uses a Lagom DI container as a class Loader."""

    def __init__(
        self,
        container: Container | None = None,
    ):
        """Creates an adapter to connect Lagom."""
        self.container = container if container is not None else Container()

    @overload
    def load(self, cls: Type[obj]) -> obj:
        pass

    @overload
    def load(self, cls: obj) -> obj:
        pass

    def load(self, cls: Type[obj] | obj) -> obj:
        """Instantiates a class or returns an already instantiated instance."""
        if not isinstance(cls, type):
            return cls

        # noinspection PyTypeChecker
        return self.container[cls]
