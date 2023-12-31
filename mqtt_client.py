import paho.mqtt.client as mqtt
from fire import Fire
from rich import print as pprint

TOPIC = "LINT"
HOST = "localhost"  # jose.devbox.melior.ai

# rabbitmq defined ports (un-encrypted)
MQTT_PORT = 1883
WEB_MQTT_PORT = 15675

# rabbitmq defined ports (encrypted)
# not used - here for documentation purposes
SSL_MQTT_PORT = 8883
SSL_WEB_MQTT_PORT = 15676

# nginx proxy ports (un-encrypted)
NGINX_MQTT_PORT = 80
NGINX_WEB_MQTT_PORT = 8888

# nginx proxy ports (encrypted)
SSL_NGINX_MQTT_PORT = 443

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
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    pprint(f"📬️ Received @ {msg.topic}: {msg.payload}")


def _get_port(transport: str, proxied: bool, ssl: bool):
    if proxied:
        if ssl:
            # SSL only through nginx
            # (we drop tls and use plain connections thereafter)
            return SSL_NGINX_MQTT_PORT

        # TCP (raw mqtt) & WebSockets port nginx proxy pass
        return NGINX_WEB_MQTT_PORT if transport == TRANSPORT_WS else NGINX_MQTT_PORT

    if ssl:
        raise ValueError(
            "'SSL' option (-s) can only be used in conjuntion with 'proxied' (-p)"
        )

    # TCP (raw mqtt) or WebSockets port directly to rabbitMQ
    return WEB_MQTT_PORT if transport == TRANSPORT_WS else MQTT_PORT


def _init_client(host: str, websockets: bool, proxied: bool, ssl: bool):
    transport = TRANSPORT_WS if websockets else TRANSPORT_TCP
    client = mqtt.Client(transport=transport)

    # Attach callbacks functions
    client.on_connect = on_connect
    client.on_message = on_message

    # IMPORTANT:
    # By default the Web MQTT plugin exposes a WebSocket endpoint
    # on port 15675 and ** path /ws **
    port = _get_port(transport, proxied, ssl)
    if transport == TRANSPORT_WS:
        client.ws_set_options(path="/ws")
    if ssl:
        # https://github.com/eclipse/paho.mqtt.python/blob/master/examples/client_sub_opts.py
        client.tls_set()
        client.tls_insecure_set(True)  # self-signed cert

    pprint(f"🔌 Connecting with MQTT over {transport.upper()} @ {host}:{port}")
    client.connect(host, port, 60)

    return client


def sub(
    topic: str,
    host: str = HOST,
    websockets: bool = False,
    proxied: bool = False,
    ssl: bool = False,
):
    """This method is analogous to the LINT-frontend which subsribes to updates
    using rabbitMQ's web-mqtt plugin (or mqtt over websockets)

    Example usage:
    ```
    python scripts/mqtt_client.py sub TEST -s -w -p -h jose.devbox.melior.ai
    ```
    """
    client = _init_client(host, websockets, proxied, ssl)

    # Set the global TOPIC to what we received so we get
    # subscription renewal. In practive this would be a class
    # and the 'topic' an attribute of the class
    global TOPIC
    TOPIC = topic
    pprint(f"🔔 Subscribing to {topic}")
    client.subscribe(topic)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        pprint(f"👋 Exiting. Goodbye!")


def pub(
    topic: str,
    message: str,
    host: str = HOST,
    websockets: bool = False,
    proxied: bool = False,
    ssl: bool = False,
):
    """This method is analogous to LINT-backend, publishing document processing updates
    if are to be published through using MQTT protocol.

    Usage example:
    ```
    python scripts/mqtt_client.py pub TEST hey-there \
        --host jose.devbox.melior.ai
        --proxied \
        --websockets \ 
        --ssl
    ```

    Note that this is equivalent to:
    ```
    publish.single(
        f"${TOPIC}/hello",
        message,
        hostname=HOST,
        port=port,
        transport=TRANSPORT_WS if websockets else TRANSPORT_TCP
    )
    ```

    But 'single' doesn't allow to specify a non-default path
    """
    client = _init_client(host, websockets, proxied, ssl)
    pprint(f"📨 Publishing to {topic} -> {message} 📨")
    client.publish(topic, message)
    client.disconnect()


def amqpub(topic: str, message: str = "Hello, RabbitMQ!", host: str = HOST):
    """This method is analogous to LINT-backend, publishing document processing updates
    if are to be published through using AMQP protocol, skipping all along the mqtt
    protocol and paho library by publishing directly to the exchange that rabbitMQ
    uses to route messages used with the mqtt protocol.
    """
    import pika

    # This is the exchange that the mqtt plugin uses
    EXCHANGE = "amq.topic"

    # Establish a connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()

    # Declare a topic exchange (could skip this as we are using a rabbitmq existing)
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", passive=True)

    # Publish the message to the exchange with the specified routing key
    channel.basic_publish(exchange=EXCHANGE, routing_key=topic, body=message)

    # Close the connection
    connection.close()


if __name__ == "__main__":
    try:
        Fire(
            {
                "sub": sub,
                "pub": pub,
                "amqpub": amqpub,
            }
        )
    except Exception as e:
        pprint(f"💥 [red]Error: {e}[/red]")
