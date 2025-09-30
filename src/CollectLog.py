import logging 
import json
import MqttPublisher
import CowrieLog
import LogAbstract

logger = logging.getLogger(__name__)
class CollectLog():
    @staticmethod
    def collectFromService(str,LogAbstract) -> str:
        logging.info("Inizio processo di inviio log dal service: %s", str)
        if str == "cowrie":
            list = CowrieLog(LogAbstract).prepareLogFromService()
        return MqttPublisher.publish(str)
        return list