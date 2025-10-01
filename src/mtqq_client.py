# python 3.11

import random
import os
from dotenv import load_dotenv

from paho.mqtt import client as mqtt_client

# Load and require MQTT env vars (no defaults)
load_dotenv()

broker = os.getenv("MQTT_BROKER")
port_raw = os.getenv("MQTT_PORT")
topic = os.getenv("MQTT_TOPIC")
client_prefix = os.getenv('MQTT_CLIENT_ID_PREFIX')

# Generate a Client ID with the subscribe prefix.
client_id = f"{client_prefix}-{random.randint(0, 100)}"
# username = os.getenv('MQTT_USERNAME')
# password = os.getenv('MQTT_PASSWORD')


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connesso al broker MQTT!")
        else:
            print("Connessione fallita, codice di ritorno %d\n", rc)

    client = mqtt_client.Client(client_id=client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Ricevuto `{msg.payload.decode()}` dal topic `{msg.topic}`")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
