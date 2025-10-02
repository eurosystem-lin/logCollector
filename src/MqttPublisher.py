# python 3.11
import json
import random
import time
from xmlrpc import client
import os
from dotenv import load_dotenv

from paho.mqtt import client as mqtt_client

from src.CowrieLog import CowrieLog

load_dotenv()

# Read required MQTT configuration from environment. No defaults allowed.
brokerServerAddress = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
topic = os.getenv("MQTT_PUBLISH_TOPIC")
client_prefix = os.getenv('MQTT_CLIENT_ID_PREFIX')


# Generate a Client ID with the publish prefix.
clientID = f"{client_prefix}-{random.randint(0, 1000)}"
class MqttPublisher:
    __client = None
    # username = os.getenv('MQTT_USERNAME')
    # password = os.getenv('MQTT_PASSWORD')
    def __init__(self):
        self.connect_mqttServer()


    def connect_mqttServer(self):
        # Accept the optional 'properties' parameter used by the newer Paho callback API (MQTT v5)
        def on_connect(client:mqtt_client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("Connesso al broker MQTT!")
            else:
                print("Connessione fallita, codice di ritorno %d\n", rc)

        # Usa l'API di callback moderna (VERSION2) per evitare DeprecationWarning
        self.__client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
                                    client_id=clientID)
        # client.username_pw_set(username, password)
        self.__client.on_connect = on_connect
        self.__client.connect(brokerServerAddress, port)


    def publish(self, topic:str, msg:json):
        result = self.__client.publish(topic, json.dumps(msg))
        # result is an MQTTMessageInfo; prefer using .rc when available
        status = getattr(result, "rc", None)
        if status is None:
            try:
                status = result[0]
            except Exception:
                status = -1

        if status == 0:
            print(f"Inviato `{msg}` al topic `{topic}`")
        else:
            print(f"Invio del messaggio al topic {topic} non riuscito")

    def keep_alive(self):
        self.__client.loop()

    def run(self):
        """Run the MQTT network loop forever. This is intended to be used as
        the target of a background thread (e.g. threading.Thread(target=run)).
        """
        # Use loop_forever so the thread blocks and handles reconnects/callbacks.
        try:
            self.__client.loop_forever()
        except Exception as e:
            print(f"MQTT loop terminated with exception: {e}")

