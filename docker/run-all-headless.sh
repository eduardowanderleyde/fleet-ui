#!/usr/bin/env bash
set -euo pipefail

PIDS=()

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait || true
}
trap cleanup EXIT INT TERM

cd "${FLEET_ROOT:-/workspace}/fleet_ws"

echo "[docker] Starting headless simulation (${WORLD:-warehouse})..."
ros2 launch fleet_orchestrator turtlebot4_sim.launch.py "world:=${WORLD:-warehouse}" headless:=True &
PIDS+=("$!")

echo "[docker] Waiting ${FLEET_START_DELAY:-18}s before fleet nodes..."
sleep "${FLEET_START_DELAY:-18}"

echo "[docker] Starting fleet nodes..."
ros2 launch fleet_orchestrator fleet.launch.py single_robot_sim:=true &
PIDS+=("$!")

echo "[docker] Waiting ${BACKEND_START_DELAY:-10}s before backend..."
sleep "${BACKEND_START_DELAY:-10}"

echo "[docker] Starting backend..."
cd "${FLEET_ROOT:-/workspace}"
bash backend/run.sh &
PIDS+=("$!")

echo "[docker] Starting frontend on http://localhost:5173 ..."
npm --prefix frontend run dev -- --host 0.0.0.0
