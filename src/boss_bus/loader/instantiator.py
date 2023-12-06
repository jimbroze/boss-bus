"""Default implementation of ClassLoader that instantiates simple classes."""


from __future__ import annotations

from typing import (
    Dict,
    Sequence,
    Type,
    get_type_hints,
)

from .loader import ClassLoader, ObjectT

RETURN_ANNOTATION = "return"


class ClassInstantiator(ClassLoader):
    """Instantiates a class with no complex dependencies.

    Dependencies are instantiated recursively.
    Throws an exception if a class, or its dependencies, cannot be instantiated
    """

    def __init__(self, dependencies: Sequence[object] = ()):
        """Creates an object that instantiates simple dependencies."""
        self.dependencies = list(dependencies)

    def add_dependency(self, dependency: object) -> None:
        """Add an already instantiated object dependency that can be retrieved.

        Any classes passed to 'load' that require this dependency will be given it.
        """
        self.dependencies.append(dependency)

    def _instantiate(self, cls: Type[ObjectT]) -> ObjectT:
        """Instantiates a class and any simple dependencies it has.

        Simple dependencies are defined as those which can be instantiated.
        The dependencies may also have dependencies, as long as these can be instantiated.
        This continues recursively.
        """
        for dep in self.dependencies:
            if isinstance(dep, cls):
                return dep

        dependencies = get_type_hints(cls.__init__, localns=self._get_locals())
        dependencies.pop(RETURN_ANNOTATION, None)

        dependency_instances = {
            dep_name: self._instantiate(dependency)
            for dep_name, dependency in dependencies.items()
        }

        return cls(**dependency_instances)

    def _get_locals(self) -> Dict[str, Type[object]]:
        return {type(dep).__name__: type(dep) for dep in self.dependencies}
