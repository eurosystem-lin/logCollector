from abc import ABC, abstractmethod
import logging
import time
from threading import Thread
from src.LogAbstract import LogAbstract
from src.MqttPublisher import MqttPublisher
from src.CowrieLog import CowrieLog

logger = logging.getLogger(__name__)


class CollectLog(Thread, ABC):
    _logAbstract = None
    _publisher = None
    def __init__(self, logAbstract: LogAbstract, publisher: MqttPublisher):
        super().__init__()
        self._logAbstract = logAbstract
        self._publisher = publisher

    def collect_log_and_publish(self):
        log = self.collect_log_from_service()
        self.publish_log(log)

    @abstractmethod
    def collect_log_from_service(self) -> str:
        raise NotImplementedError()
    @abstractmethod
    def publish_log(self, log: str):
        raise NotImplementedError()

    def run(self):
        while True:
            self.collect_log_and_publish()
            time.sleep(5)