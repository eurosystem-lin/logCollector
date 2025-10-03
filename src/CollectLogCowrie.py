from src.CollectLog import CollectLog
from src.MqttPublisher import MqttPublisher
import logging

logger = logging.getLogger(__name__)

class CollectLogCowrie(CollectLog):
    _service_log = None
    def __init__(self, logAbstract:CollectLog, MqttPublisher:MqttPublisher):
        logger.info("Inizializzazione di CollectLogCowrie")
        super().__init__(logAbstract, MqttPublisher)

    def collect_log_from_service(self) -> str:
        """Raccoglie i log dal servizio Cowrie."""
        return self._log_abstract.prepare_log_from_service()

    def publish_log(self, log: list):
        """Invia i log raccolti tramite MQTT publisher al server broker su topic cowrie/log."""
        for entry in log:
            self._publisher.publish("cowrie/log", entry)
        self._publisher.keep_alive()