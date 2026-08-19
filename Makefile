COMPOSE ?= docker compose
WINDOWS_COMPOSE ?= docker compose -f docker-compose.windows.yml

.PHONY: docker-build docker-up docker-down docker-logs docker-shell docker-check docker-build-windows docker-up-windows docker-down-windows docker-logs-windows

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

docker-build-windows:
	$(WINDOWS_COMPOSE) build

docker-up-windows:
	$(WINDOWS_COMPOSE) up

docker-down-windows:
	$(WINDOWS_COMPOSE) down

docker-logs-windows:
	$(WINDOWS_COMPOSE) logs -f
