# python 3.11

import random
import time

from paho.mqtt import client as mqtt_client


brokerServerAddress = 'broker.emqx.io'
port = 1883
topic = "python/mqtt"
# Generate a Client ID with the publish prefix.
clientID = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

def connect_mqttServer():
    # Accept the optional 'properties' parameter used by the newer Paho callback API (MQTT v5)
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Use the modern callback API (VERSION2) to avoid DeprecationWarning
    client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
                                client_id=clientID)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(brokerServerAddress, port)
    return client


def publish(client , topic, msg):
    time.sleep(1)
    msg = f"messages: {msg}"
    result = client.publish(topic, msg)
    # result is an MQTTMessageInfo; prefer using .rc when available
    status = getattr(result, "rc", None)
    if status is None:
        # fallback for tuple-style results used in older versions
        try:
            status = result[0]
        except Exception:
            status = -1

    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqttServer()
    client.loop_start()
    publish(client,topic="eurosystem/Test", msg="Hello World")
    client.loop_stop()


if __name__ == '__main__':
    run()
