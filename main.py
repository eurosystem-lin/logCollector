import threading
import os
import src.mtqq_client as mtqq_client
import src.MqttPublisher as MqttPublisher
import src.CowrieLog as CowrieLog


if __name__ == "__main__":

    print("ID del processo che esegue il programma principale: {}".format(os.getpid()))

    print("Nome del thread principale: {}".format(threading.current_thread().name))
    instance = CowrieLog.CowrieLog(logAddress="test.json")
    print(instance.prepareLogFromService())
