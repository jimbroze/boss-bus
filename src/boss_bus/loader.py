"""Classes that load dependencies and use them to instantiate classes.

Class loading classes should implement the Interface (ClassLoader)
"""


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar, overload

obj = TypeVar("obj")


class ClassLoader(ABC):
    """An Interface that allows loading dependencies and instantiating classes."""

    @overload
    def load(self, cls: Type[obj]) -> obj:
        pass

    @overload
    def load(self, cls: obj) -> obj:
        pass

    @abstractmethod
    def load(self, cls: Type[obj] | obj) -> obj:
        """Loads a class' dependencies and instantiates it."""


class ClassInstantiator(ClassLoader):
    """Instantiates a class with no complex dependencies.

    Dependencies are instantiated recursively.
    Throws an exception if a class, or it's dependencies, cannot be instantiated
    """

    @overload
    def load(self, cls: Type[obj]) -> obj:
        pass

    @overload
    def load(self, cls: obj) -> obj:
        pass

    def load(self, cls: Type[obj] | obj) -> obj:
        """Instantiates a class and any simple dependencies it has."""
        if not isinstance(cls, type):
            return cls

        instance: obj = cls()
        return instance
