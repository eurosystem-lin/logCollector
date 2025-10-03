"""Utility di logging per l'applicazione logCollector."""

from .config import (
    configure_logging,
    configure_logging_from_argv,
    resolve_log_level,
)

__all__ = [
    "configure_logging",
    "configure_logging_from_argv",
    "resolve_log_level",
]
