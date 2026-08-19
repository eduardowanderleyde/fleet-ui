#!/usr/bin/env bash
set -euo pipefail

cd "${FLEET_ROOT:-/workspace}/fleet_ws"
exec ros2 launch fleet_orchestrator turtlebot4_sim.launch.py "world:=${WORLD:-warehouse}"
