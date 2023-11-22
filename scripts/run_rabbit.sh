
echo "Starting rabbitMQ"
docker run -d \
    -p 15672:15672 \
    -p 5672:5672 \
    -p 15675:15675 \
    -p 1883:1883 \
    rabbitmq:3.12-management-alpine

sleep 5

echo "Enabling plugin for container: $rabbitID"
rabbitID=$(docker ps --format "{{.ID}}\t{{.Image}}" | grep rabbit | awk '{print $1}')
docker exec $rabbitID rabbitmq-plugins enable rabbitmq_web_mqtt

echo "Attaching to rabbit logs"
docker logs -f $rabbitID
