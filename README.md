# RabbitMQ-MQTT

Small PoC to test rabbitmq as MQTT broker

## How To

1. Build the custom `rabbitmq` image:
    ```bash
    make build-rabbit
    ```

2. Run `nginx` and the custom `rabbitmq`: 
    ```bash
    make run
    ```

3. Run the Subscriber:
    ```bash
    # TCP without nginx
    python mqtt_client.py sub COOL-TOPIC

    # TCP through nginx
    python mqtt_client.py sub COOL-TOPIC -p
    
    # WEBSOCKETS without nginx
    python mqtt_client.py sub COOL-TOPIC -w

    # WEBSOCKETS through nginx
    python mqtt_client.py sub COOL-TOPIC -w -p
    ```

4. Run the publisher:
    ```bash
    # TCP without nginx
    python mqtt_client.py pub COOL-TOPIC hello-message

    # TCP through nginx
    python mqtt_client.py pub COOL-TOPIC hello-message -p

    # WEBSOCKETS without nginx
    python mqtt_client.py pub COOL-TOPIC hello-message -w

    # WEBSOCKETS through nginx
    python mqtt_client.py pub COOL-TOPIC hello-message -w -p
    ```
