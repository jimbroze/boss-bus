"""Base Message Handler classes."""

from __future__ import annotations


class MissingHandlerError(Exception):
    """The requested Handler could not be found."""
