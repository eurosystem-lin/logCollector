from abc import ABC, abstractmethod
import logging
import time
from threading import Thread
from src.LogAbstract import LogAbstract
from src.mqtt.MqttPublisher import MqttPublisher

logger = logging.getLogger(__name__)


class CollectLog(Thread, ABC):
    _log_abstract = None
    _publisher = None
    def __init__(self, log_abstract: LogAbstract, publisher: MqttPublisher):
        logger.info("Inizializzazione di CollectLog")
        super().__init__()
        self._log_abstract = log_abstract
        self._publisher = publisher
        logger.debug(f"LogAbstract: {log_abstract}, MqttPublisher: {publisher}")

    def collect_log_and_publish(self):
        """Raccoglie i log dal servizio e li pubblica tramite MQTT publisher."""
        log = self.collect_log_from_service()
        log = self.elaborate_log(log)
        logger.debug(f"Log dopo l'elaborazione: {log}")
        if self._publisher is not None:
            self.publish_log(log)

    @abstractmethod
    def collect_log_from_service(self) -> str:
        raise NotImplementedError()
    @abstractmethod
    def publish_log(self, log: str):
        raise NotImplementedError()
    @abstractmethod
    def elaborate_log(self, log: str) -> str:
        raise NotImplementedError()

    def run(self):
        """Avvia il thread per raccogliere e pubblicare i log periodicamente."""
        while True:
            self.collect_log_and_publish()
            time.sleep(5)

    def __str__(self):
        """Restituisce una rappresentazione testuale dell'oggetto."""
        return super().__str__() + f" (log_abstract={self._log_abstract})" + f" (publisher={self._publisher})"