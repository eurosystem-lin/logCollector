import threading
import os
import sys
import src.mtqq_client as mtqq_client
from src.MqttPublisher import MqttPublisher
from src.CowrieLog import CowrieLog
from src.CollectLogCowrie import CollectLogCowrie
import logging

if __name__ == "__main__":
    configLevel = logging.DEBUG
    if(sys.argv.__len__() > 1 and sys.argv[1] == "info"):
        configLevel = logging.INFO
    elif(sys.argv.__len__() > 1 and sys.argv[1] == "warning"):
        configLevel = logging.WARNING
    elif(sys.argv.__len__() > 1 and sys.argv[1] == "error"):
        configLevel = logging.ERROR
    elif(sys.argv.__len__() > 1 and sys.argv[1] == "critical"):
        configLevel = logging.CRITICAL


    logging.basicConfig(level=configLevel,
                        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    cowrieLog = CowrieLog("text.json")
    mqttPublisher = MqttPublisher()
    collectLogCowrie = CollectLogCowrie(cowrieLog, mqttPublisher)
    print("ID del processo che esegue il programma principale: {}".format(os.getpid()))

    print("Nome del thread principale: {}".format(threading.current_thread().name))
    t2 = threading.Thread(target=collectLogCowrie.run, name="Thread-MqttPublisher")


    t2.start()
    t2.join()