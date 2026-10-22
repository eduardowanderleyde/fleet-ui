COMPOSE ?= docker compose

# Percurso do experimento BLE do CBSoft'26 num mundo aberto (ver fleet_ws/scripts/cbsoft/).
# HEADLESS: sem a janela do Gazebo (o frontend mostra o robô); com ela a CPU
# satura e o Nav2 aborta trajetos longos.
# NAV2_*: rota de ~95 m precisa de mais folga no BT e de A* no planner
# (ver _make_nav2_params em turtlebot4_sim.launch.py).
# Domínio ROS próprio: com o padrão (0) a simulação se mistura, na mesma rede,
# com TurtleBot4 reais (que também usam 0) — o Nav2 simulado poderia comandar
# um robô de verdade. Troque com `make cbsoft-up CBSOFT_DOMAIN=<n>`.
CBSOFT_DOMAIN ?= 42
CBSOFT_ENV = ROS_DOMAIN_ID=$(CBSOFT_DOMAIN) WORLD=cbsoft_open LOCALIZATION=amcl HEADLESS=True \
	NAV2_DEFAULT_SERVER_TIMEOUT_MS=1000 NAV2_NAVFN_USE_ASTAR=true \
	X_POSE=1.0216323137283325 Y_POSE=16.61626625061035 YAW=0.0

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
