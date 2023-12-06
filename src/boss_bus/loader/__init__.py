"""Classes that load dependencies and use them to instantiate classes."""

from .instantiator import ClassInstantiator
from .loader import ClassLoader

__all__ = ["ClassLoader", "ClassInstantiator"]

try:
    from .lagom import LagomLoader  # noqa: F401

    __all__.append("LagomLoader")  # pragma: no cover
except ImportError:
    pass
