"""Classes that load dependencies and use them to instantiate classes.

Class loading classes should implement the Interface (ClassLoader)
"""


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar, get_type_hints, overload

from ._utils.typing import get_annotations

RETURN_ANNOTATION = "return"

obj = TypeVar("obj", bound=object)


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
        """Instantiates a class or returns an already instantiated instance."""


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

    def load(self, cls: type[obj] | obj) -> obj:
        """Instantiates a class or returns an already instantiated instance."""
        if not isinstance(cls, type):
            return cls

        # noinspection PyTypeChecker
        return self.instantiate(cls)

    def instantiate(self, cls: type[obj]) -> obj:
        """Instantiates a class and any simple dependencies it has."""
        dependencies = get_type_hints(cls.__init__)
        print(get_annotations(cls.__init__))
        dependencies.pop(RETURN_ANNOTATION, None)

        dependency_instances = {
            dep_name: self.instantiate(dependency)
            for dep_name, dependency in dependencies.items()
        }

        return cls(**dependency_instances)
