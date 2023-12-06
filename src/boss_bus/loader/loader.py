"""Class loading classes should implement the Interface (ClassLoader)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar, overload

obj = TypeVar("obj", bound=object)


class ClassLoader(ABC):
    """An Interface that allows loading dependencies and instantiating classes."""

    @abstractmethod
    def add_dependency(self, dependency: object) -> None:
        """Add an already instantiated object dependency that can be retrieved."""

    @overload
    def load(self, cls: Type[obj]) -> obj:
        pass

    @overload
    def load(self, cls: obj) -> obj:
        pass

    def load(self, cls: Type[obj] | obj) -> obj:
        """Instantiates a class or returns an already instantiated instance.

        If cls is an uninstantiated class, try to instantiate it and its dependencies.
        If cls is an instantiated object, return it.
        """
        if not isinstance(cls, type):
            return cls

        # noinspection PyTypeChecker
        return self._instantiate(cls)

    @abstractmethod
    def _instantiate(self, cls: Type[obj]) -> obj:
        """Instantiates a class."""
