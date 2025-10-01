import threading
import os
import src.mtqq_client as mtqq_client
import src.MqttPublisher as MqttPublisher
import src.CowrieLog as CowrieLog


if __name__ == "__main__":

    print("ID del processo che esegue il programma principale: {}".format(os.getpid()))

    print("Nome del thread principale: {}".format(threading.current_thread().name))
    t1 = threading.Thread(target=mtqq_client.run, name="Thread-CowrieLog")
    t2 = threading.Thread(target=MqttPublisher.run, name="Thread-MqttPublisher")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
