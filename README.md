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
    # WEBSOCKETS without nginx
    python mqtt_client.py sub
    
    # TCP without nginx
    python mqtt_client.py sub -t tcp
    
    # WEBSOCKETS through nginx
    python mqtt_client.py sub -n
    
    # TCP through nginx
    python mqtt_client.py sub -t tcp -n
    ```

4. Run the publisher:
    ```bash
    # WEBSOCKETS without nginx
    python mqtt_client.py pub yaaaay
    
    # TCP without nginx
    python mqtt_client.py pub yaaaay -t tcp
    
    # WEBSOCKETS through nginx
    python mqtt_client.py pub yaaaay  -n
    
    # TCP through nginx
    python mqtt_client.py pub yaaaay -t tcp -n
    ```
