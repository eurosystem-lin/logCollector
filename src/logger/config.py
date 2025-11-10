from __future__ import annotations

import logging
import os
import sys
from collections.abc import Sequence
from typing import Final, TextIO

import colorama

DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_LEVEL_NAME_MAP: Final[dict[str, int]] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "fatal": logging.CRITICAL,
}

# Mapping of ANSI escape sequences for each log level; tweak values to change colors.
_LEVEL_COLOR_MAP: Final[dict[int, str]] = {
    logging.DEBUG: "\033[36m",   # Cyan
    logging.INFO: "\033[32m",    # Green
    logging.WARNING: "\033[33m", # Yellow
    logging.ERROR: "\033[31m",   # Red
    logging.CRITICAL: "\033[35m",# Magenta
}
_ANSI_RESET: Final[str] = "\033[0m"
_COLORAMA_INITIALIZED: bool = False


class _ColorFormatter(logging.Formatter):
    """Formatter che applica colori ANSI al nome del livello e al messaggio."""

    def __init__(self, fmt: str, color_map: dict[int, str] | None = None) -> None:
        super().__init__(fmt)
        self._color_map = color_map or _LEVEL_COLOR_MAP

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        original_levelname = record.levelname
        original_msg = record.msg

        color = self._color_map.get(record.levelno)
        if color:
            record.levelname = f"{color}{original_levelname}{_ANSI_RESET}"
            if isinstance(record.msg, str):
                record.msg = f"{color}{record.msg}{_ANSI_RESET}"

        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname
            record.msg = original_msg


def _prepare_stream(stream: TextIO | None) -> TextIO:
    target = stream or sys.stdout
    global _COLORAMA_INITIALIZED

    if os.name == "nt" and colorama is not None:
        if not _COLORAMA_INITIALIZED:
            if hasattr(colorama, "just_fix_windows_console"):
                colorama.just_fix_windows_console()
            colorama.init(convert=True, strip=False, autoreset=False, wrap=False)
            _COLORAMA_INITIALIZED = True
        return colorama.AnsiToWin32(target, convert=True).stream

    return target


def _stream_supports_color(stream: TextIO) -> bool:
    if os.getenv("NO_COLOR") is not None:
        return False

    is_tty = getattr(stream, "isatty", None)
    if callable(is_tty):
        try:
            return bool(is_tty())
        except Exception:  # pragma: no cover - difesa da stream non standard
            return False

    return False


def resolve_log_level(level: str | None, default: int = logging.DEBUG) -> int:
    """Traduce un livello di log testuale nella costante corrispondente.

    Qualsiasi valore non riconosciuto ricade su *default* (DEBUG per impostazione predefinita).
    """

    if level is None:
        return default

    return _LEVEL_NAME_MAP.get(level.lower(), default)


def configure_logging(
    level: int | str | None = None,
    *,
    log_format: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
    use_color: bool | None = None,
    color_map: dict[int, str] | None = None,
    stream: TextIO | None = None,
) -> int:
    """Configura il logger radice.

    Accetta un livello numerico, un nome di livello testuale oppure *None* (predefinito DEBUG).
    Restituisce il livello numerico effettivamente applicato.
    """

    resolved_level = (
        resolve_log_level(level) if isinstance(level, str) else level or logging.DEBUG
    )

    raw_stream = stream or sys.stdout
    should_use_color = use_color if use_color is not None else _stream_supports_color(raw_stream)

    handlers = None
    if should_use_color:
        target_stream = _prepare_stream(raw_stream)
        color_handler = logging.StreamHandler(target_stream)
        color_handler.setFormatter(_ColorFormatter(log_format, color_map))
        handlers = [color_handler]

    basic_config_kwargs: dict[str, object] = {
        "level": resolved_level,
        "force": force,
    }

    if handlers:
        basic_config_kwargs["handlers"] = handlers
    else:
        basic_config_kwargs["format"] = log_format
        if stream is not None:
            basic_config_kwargs["stream"] = raw_stream

    logging.basicConfig(**basic_config_kwargs)
    return resolved_level


def configure_logging_from_argv(
    argv: Sequence[str],
    *,
    default_level: int | None = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
    use_color: bool | None = None,
    color_map: dict[int, str] | None = None,
    stream: TextIO | None = None,
) -> int:
    """Configura il logging in base a una sequenza di argomenti CLI.

    Il secondo argomento posizionale (indice 1) viene interpretato come livello di log desiderato.
    """

    raw_level = argv[1] if len(argv) > 1 else None
    resolved_level = resolve_log_level(
        raw_level if raw_level is not None else None,
        default=default_level or logging.DEBUG,
    )
    configure_logging(
        resolved_level,
        log_format=log_format,
        force=force,
        use_color=use_color,
        color_map=color_map,
        stream=stream,
    )
    return resolved_level
