from src.CollectLog import CollectLog
from src.mqtt.MqttPublisher import MqttPublisher
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
        """Invia i log raccolti tramite MQTT publisher al server broker su topic predefinito."""
        logger.info("Invio dei log raccolti tramite MQTT publisher")
        logger.debug(f"Log: {log}")
        for entry in log:
            self._publisher.publish(self._log_abstract._topic, entry)
        self._publisher.keep_alive()