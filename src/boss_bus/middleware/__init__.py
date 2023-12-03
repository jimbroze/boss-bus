"""Provide the ability to augment or supplement message handling."""
from typing import List

from boss_bus.middleware.lock import BusLocker
from boss_bus.middleware.log import MessageLogger
from boss_bus.middleware.middleware import Middleware

DEFAULT_MIDDLEWARE: List[Middleware] = [BusLocker(), MessageLogger()]
