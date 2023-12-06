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

    @abstractmethod
    def load(self, cls: Type[obj] | obj) -> obj:
        """Instantiates a class or returns an already instantiated object."""
