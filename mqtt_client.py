import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from fire import Fire
from rich import print as pprint

TOPIC = "LINT"
HOST = "localhost"

# rabbitmq ports
MQTT_PORT = 1883
WEB_MQTT_PORT = 15675

# nginx proxy ports
NGINX_MQTT_PORT = 8888
NGINX_WEB_MQTT_PORT = 80

# rabbitmq / mqtt transport options
TRANSPORT_WS = "websockets"
TRANSPORT_TCP = "tcp"



def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.
    rc_map = {
        0: "🎉 Connection successful",
        1: "💥 Connection refused - incorrect protocol version",
        2: "💥 Connection refused - invalid client identifier",
        3: "💥 Connection refused - server unavailable",
        4: "💥 Connection refused - bad username or password",
        5: "💥 Connection refused - not authorise",
    }
    pprint(rc_map[rc])

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"${TOPIC}/#")


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    pprint(f"📬️ Received @ {msg.topic}: {msg.payload}")


def _get_port(transport:str, nginx:bool):
    if nginx:
        return NGINX_WEB_MQTT_PORT if transport == TRANSPORT_WS else NGINX_MQTT_PORT

    return WEB_MQTT_PORT if transport == TRANSPORT_WS else MQTT_PORT


def _init_client(transport:str, nginx:bool):
    client = mqtt.Client(transport=transport)

    # Attach callbacks functions
    client.on_connect = on_connect
    client.on_message = on_message

    # IMPORTANT:
    # By default the Web MQTT plugin exposes a WebSocket endpoint
    # on port 15675 and ** path /ws **
    client.ws_set_options(path="/ws")

    port = _get_port(transport, nginx)
    pprint(f"🔌 Connecting with MQTT over {transport.upper()} @ port={port}")
    client.connect(HOST, port, 60)

    return client


def pub(payload:str, transport:str = TRANSPORT_WS, nginx:bool = False):
    """This method is analogous to LINT-backend, publishing document processing updates.

    Equivalent to:
    ```
    publish.single(
        f"${TOPIC}/hello",
        payload,
        hostname=HOST,
        port=port,
        transport=transport
    )
    ```

    But 'single' doesn't allow to specify a non-default path
    """
    client = _init_client(transport, nginx)
    pprint(f"📨 Publishing to ${TOPIC}/hello -> {payload} 📨")
    client.publish(f"${TOPIC}/hello", payload)


def sub(transport:str = TRANSPORT_WS, nginx:bool = False):
    """This method is analogous to the LINT-frontend which subsribes to updates"""
    client = _init_client(transport, nginx)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()


if __name__ == "__main__":
    Fire({"pub": pub, "sub": sub})
