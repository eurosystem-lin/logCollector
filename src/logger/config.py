from __future__ import annotations

import io
import logging
import os
import sys
from collections.abc import Sequence
from typing import Final, TextIO

DEFAULT_LOG_FORMAT: Final[str] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
)
_LEVEL_NAME_MAP: Final[dict[str, int]] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "fatal": logging.CRITICAL,
}


class _ColorFormatter(logging.Formatter):
    """Applicazione di sequenze ANSI in base al livello di log."""

    _COLOR_BY_LEVEL: Final[dict[int, str]] = {
        logging.DEBUG: "\x1b[36m",  # cyan
        logging.INFO: "\x1b[37m",  # light gray
        logging.WARNING: "\x1b[33m",  # yellow
        logging.ERROR: "\x1b[31m",  # red
        logging.CRITICAL: "\x1b[1;31m",  # bold red
    }
    _RESET: Final[str] = "\x1b[0m"

    def __init__(self, base_format: str) -> None:
        super().__init__()
        self._formatter_by_level = {
            level: logging.Formatter(f"{color}{base_format}{self._RESET}")
            for level, color in self._COLOR_BY_LEVEL.items()
        }
        self._fallback_formatter = logging.Formatter(base_format)

    def format(self, record: logging.LogRecord) -> str:
        formatter = self._formatter_by_level.get(record.levelno, self._fallback_formatter)
        return formatter.format(record)


def resolve_log_level(level: str | None, default: int = logging.DEBUG) -> int:
    """Traduce un livello di log testuale nella costante corrispondente."""
    if level is None:
        return default
    return _LEVEL_NAME_MAP.get(level.lower(), default)


def configure_logging(
    level: int | str | None = None,
    *,
    log_format: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
    use_color: bool | None = None,
    stream: TextIO | None = None,
) -> int:
    """Configura il logger radice applicando opzionalmente colori ANSI."""
    resolved_level = (
        resolve_log_level(level) if isinstance(level, str) else level or logging.DEBUG
    )
    handler_stream = stream or sys.stdout

    use_color_flag = _should_use_color(handler_stream, use_color)
    if use_color_flag:
        _enable_windows_ansi(handler_stream)
        formatter: logging.Formatter = _ColorFormatter(log_format)
    else:
        formatter = logging.Formatter(log_format)

    root_logger = logging.getLogger()

    if force:
        _reset_handlers(root_logger)

    root_logger.setLevel(resolved_level)
    if not root_logger.handlers:
        handler = logging.StreamHandler(handler_stream)
        handler.setLevel(resolved_level)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        root_logger.setLevel(resolved_level)
        for handler in root_logger.handlers:
            handler.setLevel(resolved_level)
            if isinstance(handler, logging.StreamHandler):
                if stream is not None and hasattr(handler, "setStream"):
                    handler.setStream(handler_stream)
                handler.setFormatter(formatter)
    return resolved_level


def configure_logging_from_argv(
    argv: Sequence[str],
    *,
    default_level: int | None = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
    use_color: bool | None = None,
    stream: TextIO | None = None,
) -> int:
    """Configura il logging in base agli argomenti CLI."""
    raw_level = argv[1] if len(argv) > 1 else None
    resolved_level = resolve_log_level(
        raw_level,
        default=default_level or logging.DEBUG,
    )
    return configure_logging(
        resolved_level,
        log_format=log_format,
        force=force,
        use_color=use_color,
        stream=stream,
    )


def _should_use_color(stream: TextIO, explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    isatty = getattr(stream, "isatty", None)
    if callable(isatty):
        try:
            return bool(isatty())
        except OSError:
            return False
    return False


def _enable_windows_ansi(stream: TextIO) -> None:
    if os.name != "nt":
        return
    fileno = getattr(stream, "fileno", None)
    if not callable(fileno):
        return
    try:
        fd = stream.fileno()
    except (io.UnsupportedOperation, ValueError, OSError):
        return
    try:
        import msvcrt  # type: ignore
        import ctypes
    except ImportError:
        return

    kernel32 = ctypes.windll.kernel32
    handle = msvcrt.get_osfhandle(fd)
    mode = ctypes.c_uint()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    if mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
        return
    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)


def _reset_handlers(logger: logging.Logger) -> None:
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
