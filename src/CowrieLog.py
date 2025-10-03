import logging
import json
import os
from src.LogAbstract import LogAbstract

logger = logging.getLogger(__name__)


class CowrieLog(LogAbstract):
    _file_size = None
    def __init__(self, logAddress: str, topic: str):
        logger.info("Inizializzazione di CowrieLog con logAddress: %s e topic: %s", str(logAddress), topic)
        super().__init__(logAddress, topic)
        self._file_size = 0

    def prepare_log_from_service(self) -> list:
        """Legge un file JSON in `self._logAddress` e restituisce una lista di oggetti JSON.
        """
        logger.info("Preparazione del log JSON dal servizio Cowrie")
        logger.debug("Logaddress: %s", str(self._log_file_path))

        if not self._log_file_path:
            logger.error("Nessun indirizzo di log fornito a CowrieLog")
            return []

        try:
            with open(self._log_file_path, "r", encoding="utf-8") as f:
                text = f.read()
            # Prova una riga = un JSON
            logger.debug("Prossima riga da leggere: %d", self._last_used)
            logger.debug("Dimensione del file letto (la volta prima): %s", self._file_size)
            logger.debug("Dimensione del file letto adesso: %s", os.path.getsize(self._log_file_path))
            objs = []
            if(self._file_size > os.path.getsize(self._log_file_path)):
                logger.info("Il file di log è stato resettato. Rilettura dall'inizio.")
                self._last_used = 1
            self._file_size = os.path.getsize(self._log_file_path)
            current_lines = 0

            for i, line in enumerate(text.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue
                current_lines += 1
                if current_lines < self._last_used:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.debug("Riga %d non è JSON valido, salto", i)
            self._last_used = current_lines + 1
            if objs:
                return objs
            else:
                logger.info("Non sono presenti oggetti JSON validi: %s", self._log_file_path)
            return []

        except FileNotFoundError:
            logger.exception("File di log non trovato: %s", self._log_file_path)
        except Exception:
            logger.exception("Errore durante la lettura del file di log: %s", self._log_file_path)

        return []