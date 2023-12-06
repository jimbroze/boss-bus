"""Default ClassLoader that instantiates simple classes."""


from __future__ import annotations

from typing import (
    Dict,
    Sequence,
    Type,
    get_type_hints,
    overload,
)

from .loader import ClassLoader, obj

RETURN_ANNOTATION = "return"


class ClassInstantiator(ClassLoader):
    """Instantiates a class with no complex dependencies.

    Dependencies are instantiated recursively.
    Throws an exception if a class, or it's dependencies, cannot be instantiated
    """

    def __init__(self, dependencies: Sequence[object] = ()):
        """Creates an object that instantiates simple dependencies."""
        self.dependencies = list(dependencies)

    def add_dependency(self, dependency: object) -> None:
        """Add an already instantiated object dependency that can be retrieved."""
        self.dependencies.append(dependency)

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
        return self.instantiate(cls)

    def instantiate(self, cls: Type[obj]) -> obj:
        """Instantiates a class and any simple dependencies it has."""
        for dep in self.dependencies:
            if isinstance(dep, cls):
                return dep

        dependencies = get_type_hints(cls.__init__, localns=self._get_locals())
        dependencies.pop(RETURN_ANNOTATION, None)

        dependency_instances = {
            dep_name: self.instantiate(dependency)
            for dep_name, dependency in dependencies.items()
        }

        return cls(**dependency_instances)

    def _get_locals(self) -> Dict[str, Type[object]]:
        return {type(dep).__name__: type(dep) for dep in self.dependencies}
