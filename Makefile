COMPOSE ?= docker compose

# Percurso do experimento BLE do CBSoft'26 num mundo aberto (ver fleet_ws/scripts/cbsoft/).
CBSOFT_ENV = WORLD=cbsoft_open LOCALIZATION=amcl X_POSE=1.0216323137283325 Y_POSE=16.61626625061035 YAW=0.0

.PHONY: docker-build docker-up docker-down docker-logs docker-shell docker-check cbsoft-up cbsoft-run

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

cbsoft-up:
	mkdir -p fleet_ws/routes/default
	cp fleet_ws/scripts/cbsoft/percurso_cbsoft.yaml fleet_ws/routes/default/
	$(CBSOFT_ENV) $(COMPOSE) up

cbsoft-run:
	$(COMPOSE) exec -w /workspace/fleet_ws sim bash -c "source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 -u scripts/cbsoft/nav_3points.py --sim --log-dir collections/cbsoft"
