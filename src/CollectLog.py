from abc import ABC, abstractmethod
import logging 
import json
import MqttPublisher
import CowrieLog
from threading import Thread
from src.LogAbstract import LogAbstract

logger = logging.getLogger(__name__)
class CollectLog(Thread, ABC):
    _logAbstract = None
    _publisher = None
    def __init__(self, logAbstract:LogAbstract, MqttPublisher:MqttPublisher):
        super().__init__()
        self._logAbstract = logAbstract
        self._publisher = MqttPublisher

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
        self.collect_log_and_publish()