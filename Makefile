
.ONESHELL:
cert:
	# e.g.: 'make cert env=dev region=eu'
	echo "Generating cert for: localhost"
	mkdir -p ${PWD}/nginx/openssl
	openssl req -new \
		-nodes \
		-x509 \
		-days 365 \
		-newkey rsa:4096 \
		-subj /CN=localhost \
		-keyout ${PWD}/nginx/openssl/server.key \
		-out ${PWD}/nginx/openssl/server.crt

print-cert:
	openssl x509 -in ${PWD}/nginx/openssl/server.crt -text -noout


rabbit:
	bash run_rabbit.sh

build-rabbit:
	docker build \
		-f mqtt_rabbit.dockerfile \
		-t mqtt_rabbit:latest \
		.

run:
	docker-compose up
