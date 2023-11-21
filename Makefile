
rabbit:
	bash run_rabbit.sh

build-rabbit:
	docker build \
		-f mqtt_rabbit.dockerfile \
		-t mqtt_rabbit:latest \
		.

run:
	docker-compose up
