# python 3.11
import json
import logging
import random
import os
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from paho.mqtt import MQTTException
load_dotenv()

# Read required MQTT configuration from environment. No defaults allowed.
# TODO: da eliminare
brokerServerAddress = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
topic = os.getenv("MQTT_PUBLISH_TOPIC")
client_prefix = os.getenv('MQTT_CLIENT_ID_PREFIX')

logger = logging.getLogger(__name__)
# Generate a Client ID with the publish prefix.
clientID = f"{client_prefix}-{random.randint(0, 1000)}"
class MqttPublisher:
    __client = None
    # username = os.getenv('MQTT_USERNAME')
    # password = os.getenv('MQTT_PASSWORD')
    def __init__(self):
        logger.info("Inizializzazione di MqttPublisher")
        self.connect_mqttServer()


    def connect_mqttServer(self):
        """
        Connette al server MQTT e inizializza il client MQTT."""
        # Accept the optional 'properties' parameter used by the newer Paho callback API (MQTT v5)
        logger.info("Connessione al broker MQTT...")
        logger.debug(f"Client ID: {clientID}, Broker: {brokerServerAddress}:{port}")
        def on_connect(client:mqtt_client, userdata, flags, rc, properties=None):
            if rc == 0:
                logger.info("Connesso al broker MQTT!")
                logger.debug(f"Client ID: {clientID}, Broker: {brokerServerAddress}:{port}")
            else:
                logger.error(f"Connessione fallita, codice di ritorno {rc}")

        # Usa l'API di callback moderna (VERSION2) per evitare DeprecationWarning
        self.__client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
                                    client_id=clientID)
        # client.username_pw_set(username, password)
        self.__client.on_connect = on_connect
        self.__client.connect(brokerServerAddress, port)


    def publish(self, topic:str, msg:json):
        """
        Pubblica un messaggio di tipo JSON su un topic MQTT, il parametro topic deve essere una stringa.
        """
        result = self.__client.publish(topic, json.dumps(msg))
        # result is an MQTTMessageInfo; prefer using .rc when available
        status = getattr(result, "rc", None)
        if status is None:
            try:
                status = result[0]
            except Exception:
                status = -1

        if status == 0:
            logger.info(f"Inviato `{msg}` al topic `{topic}`")
        else:
            logger.error(f"Invio del messaggio al topic {topic} non riuscito")

    def keep_alive(self):
        """Mantiene viva la connessione MQTT chiamando il loop del client."""
        self.__client.loop()

    def run(self):
        """Avvia il loop del client MQTT per mantenere la connessione attiva.
        """
        # Use loop_forever so the thread blocks and handles reconnects/callbacks.
        try:
            self.__client.loop_forever()
        except Exception as e:
            logger.error(f"MQTT loop terminated with exception: {e}")

