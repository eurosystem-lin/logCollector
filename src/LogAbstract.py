from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

class LogAbstract(ABC):
    _last_used = None
    _log_file_path = None

    def __init__(self, log_path:str):
        logger.info(f"Inizializzazione di LogAbstract con logAddress: {log_path}")
        self._last_used = 0
        self._log_file_path = log_path

    @abstractmethod
    def prepare_log_from_service(self) -> list:
        """Prepara i log dal servizio specifico e lo restituisce in un formato specifico definito dalla sottoclasse"""
        raise NotImplementedError()
    
    def __str__(self):
        """Restituisce una rappresentazione testuale dell'oggetto."""
        return super().__str__() + f" (log_path={self._log_file_path})" + f" (last_used={self._last_used})"