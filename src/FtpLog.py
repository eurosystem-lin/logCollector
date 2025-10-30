import logging
import os
import re
from datetime import datetime, timezone
from src.LogAbstract import LogAbstract

logger = logging.getLogger(__name__)


class FtpLog(LogAbstract):
    _file_size = None

    def __init__(self, logAddress: str, topic: str):
        logger.info("Inizializzazione di FtpLog con logAddress: %s e topic: %s", str(logAddress), topic)
        super().__init__(logAddress, topic)
        self._file_size = 0

    def prepare_log_from_service(self) -> list:
        """Legge l'intero file FTP e converte ogni riga in un oggetto JSON normalizzato."""

        logger.info("Preparazione del log dal servizio FTP")
        logger.debug("Logaddress: %s", str(self._log_file_path))

        if not self._log_file_path:
            logger.error("Nessun indirizzo di log fornito a FtpLog")
            return []

        try:
            with open(self._log_file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            logger.exception("File di log non trovato: %s", self._log_file_path)
            return []
        except Exception:
            logger.exception("Errore durante la lettura del file di log: %s", self._log_file_path)
            return []

        if self._file_size > os.path.getsize(self._log_file_path):
            logger.info("Il file di log FTP è stato resettato. Rilettura dall'inizio.")
            self._last_used = 1
        self._file_size = os.path.getsize(self._log_file_path)

        ftp_header = re.compile(
            r"^(?P<weekday>\w{3}) (?P<month>\w{3}) (?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2})(?: (?P<year>\d{4}))? (?P<rest>.+)$"
        )
        ipv4_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

        def _format_timestamp(dt: datetime) -> str:
            return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

        def _parse_line(raw_line: str) -> tuple[str | None, str]:
            match = ftp_header.match(raw_line)
            if not match:
                logger.debug("Formato riga FTP non riconosciuto, uso contenuto grezzo")
                return None, raw_line.strip()

            year = match.group("year") or str(datetime.now().year)
            timestamp_str = (
                f"{match.group('weekday')} {match.group('month')} {match.group('day')} "
                f"{match.group('time')} {year}"
            )

            try:
                timestamp = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
            except ValueError:
                logger.debug("Impossibile convertire il timestamp FTP: %s", timestamp_str)
                return None, match.group("rest").strip()

            formatted_timestamp = _format_timestamp(timestamp)
            remainder = match.group("rest").strip()
            return formatted_timestamp, remainder

        def _extract_ipv4(text: str) -> str | None:
            match = ipv4_pattern.search(text)
            if not match:
                return None

            candidate = match.group()
            return candidate if all(0 <= int(num) <= 255 for num in candidate.split(".")) else None

        entries = []
        processed_lines = 0

        for raw_line in text.splitlines():
            stripped_line = raw_line.strip()
            if not stripped_line:
                continue

            processed_lines += 1
            if processed_lines < self._last_used:
                continue

            timestamp, remainder = _parse_line(raw_line)
            src_ip = _extract_ipv4(remainder) or _extract_ipv4(raw_line)
            entries.append({
                "timestamp": timestamp,
                "eventid": "ftp",
                "other": remainder,
                "src_ip": src_ip,
            })

        self._last_used = processed_lines + 1 if processed_lines else 1

        if entries:
            return entries

        logger.info("Non sono presenti log FTP validi in %s", self._log_file_path)
        return []