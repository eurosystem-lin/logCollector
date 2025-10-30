import logging

from src.CollectLog import CollectLog
from src.mqtt.MqttPublisher import MqttPublisher
from src.tool import IPCheck

logger = logging.getLogger(__name__)


class CollectLogFtp(CollectLog):
    _service_log = None

    def __init__(self, logAbstract: CollectLog, MqttPublisher: MqttPublisher):
        logger.info("Inizializzazione di CollectLogFtp")
        super().__init__(logAbstract, MqttPublisher)

    def collect_log_from_service(self) -> str:
        """Raccoglie i log dal servizio FTP."""
        logger.info("Raccolta dei log dal servizio FTP")
        return self._log_abstract.prepare_log_from_service()

    def elaborate_log(self, log: list) -> list:
        """Elabora i log FTP raccolti."""
        logger.info("Elaborazione dei log FTP raccolti")
        logger.debug(f"Log FTP prima dell'elaborazione: {log}")
        filtered_log = []
        for entry in log:
            if "client_ip" not in entry and "src_ip" not in entry:
                filtered_log.append(entry)
                continue
            client_ip = entry.get("client_ip") or entry.get("src_ip")
            isp = None
            try:
                isp = IPCheck.check_ip_isp(client_ip)
            except Exception as exc:
                logger.warning(
                    "Impossibile recuperare l'ISP per %s: %s",
                    client_ip,
                    exc,
                )
            if isp:
                entry["isp"] = isp
            filtered_log.append(entry)
        return filtered_log

    def publish_log(self, log: list):
        """Invia i log FTP raccolti tramite MQTT publisher."""
        logger.info("Invio dei log FTP raccolti tramite MQTT publisher")
        logger.debug(f"Log FTP: {log}")
        for entry in log:
            self._publisher.publish(self._log_abstract._topic, entry)
        self._publisher.keep_alive()
