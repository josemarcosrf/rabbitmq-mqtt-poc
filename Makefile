
.ONESHELL:
cert:
	# e.g.: 'make cert env=dev region=eu'
	echo "Generating cert for: localhost"
	mkdir -p ${PWD}/nginx/openssl
	openssl req -new -newkey rsa:4096 \
		-days 999999 -nodes -x509 \
		-subj /CN=localhost \
		-keyout ${PWD}/nginx/openssl/server.key \
		-out ${PWD}/nginx/openssl/server.crt

rabbit:
	bash run_rabbit.sh

build-rabbit:
	docker build \
		-f mqtt_rabbit.dockerfile \
		-t mqtt_rabbit:latest \
		.

run:
	docker-compose up
