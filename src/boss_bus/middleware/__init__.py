"""Provide the ability to augment or supplement message handling."""
from typing import List

from .lock import BusLocker
from .log import MessageLogger
from .middleware import Middleware

DEFAULT_MIDDLEWARE: List[Middleware] = [BusLocker(), MessageLogger()]

__all__ = ["Middleware", "MessageLogger", "BusLocker", "DEFAULT_MIDDLEWARE"]
