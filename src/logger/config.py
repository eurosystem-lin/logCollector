from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Final

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
) -> int:
    """Configura il logger radice.

    Accetta un livello numerico, un nome di livello testuale oppure *None* (predefinito DEBUG).
    Restituisce il livello numerico effettivamente applicato.
    """

    resolved_level = (
        resolve_log_level(level) if isinstance(level, str) else level or logging.DEBUG
    )

    logging.basicConfig(level=resolved_level, format=log_format, force=force)
    return resolved_level


def configure_logging_from_argv(
    argv: Sequence[str],
    *,
    default_level: int | None = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    force: bool = False,
) -> int:
    """Configura il logging in base a una sequenza di argomenti CLI.

    Il secondo argomento posizionale (indice 1) viene interpretato come livello di log desiderato.
    """

    raw_level = argv[1] if len(argv) > 1 else None
    resolved_level = resolve_log_level(
        raw_level if raw_level is not None else None,
        default=default_level or logging.DEBUG,
    )
    logging.basicConfig(level=resolved_level, format=log_format, force=force)
    return resolved_level
