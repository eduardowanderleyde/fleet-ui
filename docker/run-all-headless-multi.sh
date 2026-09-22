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

# Polls `ros2 topic list` until every pattern given is present, instead of
# sleeping a fixed guess. Falls back to the fixed delay if it times out, so a
# slower-than-expected boot still proceeds instead of hanging forever.
wait_for_topics() {
  local timeout_s="$1"; shift
  local patterns=("$@")
  local waited=0
  while (( waited < timeout_s )); do
    local topics
    topics="$(ros2 topic list 2>/dev/null || true)"
    local missing=0
    for p in "${patterns[@]}"; do
      grep -q "$p" <<<"$topics" || missing=1
    done
    if [ "$missing" -eq 0 ]; then
      echo "[docker] Ready after ${waited}s: ${patterns[*]}"
      return 0
    fi
    sleep 2
    waited=$((waited + 2))
  done
  echo "[docker] Timed out after ${timeout_s}s waiting for: ${patterns[*]} (continuing anyway)"
  return 1
}

cd "${FLEET_ROOT:-/workspace}/fleet_ws"

echo "[docker] Starting headless 3-robot simulation (${WORLD:-warehouse})..."
ros2 launch fleet_orchestrator turtlebot4_multi_sim.launch.py "world:=${WORLD:-warehouse}" headless:=true &
PIDS+=("$!")

echo "[docker] Waiting for tb1/tb2/tb3 scan+tf topics (up to ${FLEET_START_DELAY:-90}s)..."
wait_for_topics "${FLEET_START_DELAY:-90}" "/tb1/scan" "/tb2/scan" "/tb3/scan" "/tb1/tf"

echo "[docker] Starting fleet nodes (orchestrator + sensor collector)..."
ros2 launch fleet_orchestrator fleet.launch.py &
PIDS+=("$!")

echo "[docker] Waiting for fleet/status (up to ${BACKEND_START_DELAY:-30}s)..."
wait_for_topics "${BACKEND_START_DELAY:-30}" "/fleet/status"

echo "[docker] Starting backend..."
cd "${FLEET_ROOT:-/workspace}"
bash backend/run.sh &
PIDS+=("$!")

echo "[docker] Starting frontend on http://localhost:5173 ..."
npm --prefix frontend run dev -- --host 0.0.0.0
