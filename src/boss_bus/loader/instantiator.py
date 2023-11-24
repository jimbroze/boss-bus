"""Default ClassLoader that instantiates simple classes."""


from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Type, get_type_hints, overload

from boss_bus.loader import ClassLoader, obj

if TYPE_CHECKING:
    from boss_bus.message_bus import MessageBus

RETURN_ANNOTATION = "return"


class ClassInstantiator(ClassLoader):
    """Instantiates a class with no complex dependencies.

    Dependencies are instantiated recursively.
    Throws an exception if a class, or it's dependencies, cannot be instantiated
    """

    def __init__(self, bus: MessageBus | None = None):
        """Creates an object that instantiates simple dependencies."""
        self.bus = bus

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
        if self.bus is not None and isinstance(self.bus, cls):
            return self.bus

        dependencies = get_type_hints(cls.__init__, localns=self._get_locals())
        dependencies.pop(RETURN_ANNOTATION, None)

        dependency_instances = {
            dep_name: self.instantiate(dependency)
            for dep_name, dependency in dependencies.items()
        }

        return cls(**dependency_instances)

    def _get_locals(self) -> Dict[str, Type[Any]]:
        bus_class = type(self.bus)
        return {bus_class.__name__: bus_class} if self.bus is not None else {}
