#!/usr/bin/env bash
set -euo pipefail

# Windows Docker Desktop mode, adapted for the 3-robot (tb1/tb2/tb3) simulation.
# Everything runs in one container so ROS 2 DDS discovery stays local, which
# avoids cross-container discovery issues that network_mode: host would need
# on Linux (not available the same way on Docker Desktop for Windows/macOS).

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

echo "[docker] Starting headless 3-robot simulation (${WORLD:-warehouse})..."
ros2 launch fleet_orchestrator turtlebot4_multi_sim.launch.py "world:=${WORLD:-warehouse}" headless:=true &
PIDS+=("$!")

echo "[docker] Waiting ${FLEET_START_DELAY:-40}s before fleet nodes (SLAM + Nav2 x3 take longer to come up)..."
sleep "${FLEET_START_DELAY:-40}"

echo "[docker] Starting fleet nodes (orchestrator + sensor collector)..."
ros2 launch fleet_orchestrator fleet.launch.py &
PIDS+=("$!")

echo "[docker] Waiting ${BACKEND_START_DELAY:-15}s before backend..."
sleep "${BACKEND_START_DELAY:-15}"

echo "[docker] Starting backend..."
cd "${FLEET_ROOT:-/workspace}"
bash backend/run.sh &
PIDS+=("$!")

echo "[docker] Starting frontend on http://localhost:5173 ..."
npm --prefix frontend run dev -- --host 0.0.0.0
