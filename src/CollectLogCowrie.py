from src.CollectLog import CollectLog
from src.MqttPublisher import MqttPublisher


class CollectLogCowrie(CollectLog):
    _service_log = None
    def __init__(self, logAbstract:CollectLog, MqttPublisher:MqttPublisher):
        super().__init__(logAbstract, MqttPublisher)

    def collect_log_from_service(self) -> str:
        return self._logAbstract.prepare_log_from_service()

    def publish_log(self, log: list):
        for entry in log:
            self._publisher.publish("cowrie/log", str(entry))
        self._publisher.keep_alive()