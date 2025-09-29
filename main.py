import threading
import os
import src.mtqq_client as mtqq_client
import src.MqttPublisher as MqttPublisher


if __name__ == "__main__":

    print("ID of process running main program: {}".format(os.getpid()))

    print("Main thread name: {}".format(threading.current_thread().name))

    t1 = threading.Thread(target=mtqq_client.run, name='t1')
    t2 = threading.Thread(target=MqttPublisher.run, name='t2')

    t1.start()
    t2.start()

    t1.join()
    t2.join()