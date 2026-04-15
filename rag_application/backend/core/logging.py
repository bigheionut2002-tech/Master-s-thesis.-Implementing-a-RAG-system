"""Centralised logging configuration.

Importing :func:`configure_logging` once at application startup is enough —
afterwards every module should obtain a logger with ``logging.getLogger(__name__)``.
"""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger with a consistent format and stdout handler.

    Args:
        level: Minimum log level (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``).
    """
    root = logging.getLogger()
    root.setLevel(level.upper())

    # Remove duplicate handlers that uvicorn/pytest may attach.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root.addHandler(handler)
