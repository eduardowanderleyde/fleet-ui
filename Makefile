COMPOSE ?= docker compose

.PHONY: docker-build docker-up docker-down docker-logs docker-shell docker-check

docker-build:
	$(COMPOSE) build

docker-up:
	$(COMPOSE) up

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f

docker-shell:
	$(COMPOSE) run --rm backend bash

docker-check:
	$(COMPOSE) run --rm backend bash check.sh
