"""An optional module that allows using the DI container Lagom, as a class Loader."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type, overload

from lagom import Container

from boss_bus import ClassLoader
from boss_bus.loader.instantiator import ClassInstantiator

if TYPE_CHECKING:
    from boss_bus.loader.loader import obj


class LagomLoader(ClassLoader):
    """Uses a Lagom DI container as a class Loader."""

    def __init__(
        self,
        container: Container | None = None,
    ):
        """Creates an adapter to connect Lagom."""
        self.container = container if container is not None else Container()
        self.instantiator = ClassInstantiator()

    def add_dependency(self, dependency: object) -> None:
        """Add an already instantiated object dependency that can be retrieved.

        Keeps container definitions explicit
        """
        self.instantiator.add_dependency(dependency)

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
        return self._instantiate(cls)

    def _instantiate(self, cls: Type[obj]) -> obj:
        try:
            return self.container.resolve(cls)
        except NameError:
            return self.instantiator.load(cls)
