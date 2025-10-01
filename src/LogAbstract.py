from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

class LogAbstract(ABC):
    _latestUsed = None
    _logAddress = None

    def __init__(self, logAddress:str):
        logger.info(f"Inizializzazione di LogAbstract con logAddress: {logAddress}")
        self._latestUsed = 0
        self._logAddress = logAddress

    def log(self, message):
        logger.info(f"Scrittura log su {self._logAddress}: {message}")
        raise NotImplementedError("Le sottoclassi devono implementare questo metodo")

    @abstractmethod
    def prepare_log_from_service(self) -> str:
        """Apri l'indirizzo di log configurato e restituisci il suo contenuto."""
        raise NotImplementedError()