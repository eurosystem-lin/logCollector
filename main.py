import threading
import os
import src.mtqq_client as mtqq_client
from src.MqttPublisher import MqttPublisher
from src.CowrieLog import CowrieLog
from src.CollectLogCowrie import CollectLogCowrie
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    logging.getLogger().setLevel(logging.DEBUG)
    cowrieLog = CowrieLog("text.json")
    mqttPublisher = MqttPublisher()
    collectLogCowrie = CollectLogCowrie(cowrieLog, mqttPublisher)
    print("ID del processo che esegue il programma principale: {}".format(os.getpid()))

    print("Nome del thread principale: {}".format(threading.current_thread().name))
    t1 = threading.Thread(target=mtqq_client.run, name="Thread-CowrieLog")
    t2 = threading.Thread(target=collectLogCowrie.run, name="Thread-MqttPublisher")


    t1.start()
    t2.start()

    t1.join()
    t2.join()