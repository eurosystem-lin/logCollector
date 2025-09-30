import logging
import json
from .LogAbstract import LogAbstract

logger = logging.getLogger(__name__)


class CowrieLog(LogAbstract):
    def __init__(self, logAddress):
        super().__init__(logAddress)

    def prepareLogFromService(self) -> list:
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

            # Prova diretta: caricare tutto come JSON
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return data
                else:
                    return [data]
            except json.JSONDecodeError as e:
                logger.debug("json.loads fallito: %s", e)

            # Prova una riga = un JSON
            objs = []
            for i, line in enumerate(text.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.debug("Riga %d non è JSON valido, salto", i)

            if objs:
                return objs

            logger.error("Impossibile decodificare il file come JSON: %s", self._logAddress)
            return []

        except FileNotFoundError:
            logger.exception("File di log non trovato: %s", self._logAddress)
        except Exception:
            logger.exception("Errore durante la lettura del file di log: %s", self._logAddress)

        return []