"""An optional module that allows using the DI container Lagom, as a class Loader."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

from lagom import Container

from boss_bus import ClassLoader
from boss_bus.loader.instantiator import ClassInstantiator

if TYPE_CHECKING:
    from boss_bus.loader.loader import ObjectT


class LagomLoader(ClassLoader):
    """Enables the use of a Lagom IoC (DI) container as a class Loader."""

    def __init__(
        self,
        container: Container | None = None,
    ):
        """Creates an adapter to connect Lagom."""
        self.container = container if container is not None else Container()
        self.instantiator = ClassInstantiator()

    def add_dependency(self, dependency: object) -> None:
        """Adds an already instantiated object dependency that can be retrieved.

        This is delegated to a ClassInstantiator object rather than being added
        to the container. This keeps container definitions explicit.
        """
        self.instantiator.add_dependency(dependency)

    def _instantiate(self, cls: Type[ObjectT]) -> ObjectT:
        try:
            return self.container.resolve(cls)
        except NameError:
            return self.instantiator.load(cls)
