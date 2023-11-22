"""Provide the ability to augment or supplement message handling."""

from boss_bus.middleware.log import MessageLogger
from boss_bus.middleware.middleware import Middleware

DEFAULT_MIDDLEWARE: list[Middleware] = [MessageLogger()]
