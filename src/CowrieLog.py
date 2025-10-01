import logging
import json
import os
from src.LogAbstract import LogAbstract

logger = logging.getLogger(__name__)


class CowrieLog(LogAbstract):
    _file_size = None
    def __init__(self, logAddress):
        logger.info("Inizializzazione di CowrieLog con logAddress: %s", str(logAddress))
        super().__init__(logAddress)
        self._file_size = 0

    def prepare_log_from_service(self) -> list:
        """Legge un file JSON in `self._logAddress` e restituisce una lista di oggetti.
        """
        logger.info("Preparazione del log JSON dal servizio Cowrie")
        logger.debug("Logaddress: %s", str(self._logAddress))

        if not self._logAddress:
            logger.error("Nessun indirizzo di log fornito a CowrieLog")
            return []

        try:
            with open(self._logAddress, "r", encoding="utf-8") as f:
                text = f.read()
            # Prova una riga = un JSON
            logger.debug("Numero di righe letto nel l'ultima volta: %d righe", self._latestUsed)
            logger.debug("Dimensione del file letto (la volta prima): %s", self._file_size)
            logger.debug("Dimensione del file letto adesso: %s", os.path.getsize(self._logAddress))
            objs = []
            if(self._file_size > os.path.getsize(self._logAddress)):
                logger.info("Il file di log è stato resettato. Rilettura dall'inizio.")
                self._latestUsed = 1
            self._file_size = os.path.getsize(self._logAddress)
            current_lines = 0

            for i, line in enumerate(text.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue
                current_lines += 1
                if current_lines < self._latestUsed:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.debug("Riga %d non è JSON valido, salto", i)
            self._latestUsed = current_lines + 1
            if objs:
                return objs

            logger.error("Impossibile decodificare il file come JSON: %s", self._logAddress)
            return []

        except FileNotFoundError:
            logger.exception("File di log non trovato: %s", self._logAddress)
        except Exception:
            logger.exception("Errore durante la lettura del file di log: %s", self._logAddress)

        return []