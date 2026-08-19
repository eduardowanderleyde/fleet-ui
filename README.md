# Fleet UI

Web interface for operating a TurtleBot4 fleet in simulation. Record navigation routes with full sensor data, replay them, and measure trajectory repeatability.

## Architecture

Four processes that must run simultaneously:

| # | Process | What it does | Port |
|---|---------|-------------|------|
| 1 | **Simulation** | Gazebo + SLAM Toolbox + Nav2 | — |
| 2 | **Fleet nodes** | Route recording/replay, sensor collection | — |
| 3 | **Backend** | FastAPI bridge between ROS 2 and the web UI | 8000 |
| 4 | **Frontend** | React + Vite map interface | 5173 |

```
fleet-ui/
├── fleet_ws/               # ROS 2 colcon workspace
│   ├── src/
│   │   ├── fleet_msgs/           # Custom messages and services
│   │   ├── fleet_orchestrator/   # Route record/play + Nav2 client
│   │   │   └── launch/
│   │   │       ├── turtlebot4_sim.launch.py   # Terminal 1
│   │   │       └── fleet.launch.py            # Terminal 2
│   │   └── fleet_data_collector/ # MCAP sensor recording
│   ├── scripts/            # CLI tools and healthcheck
│   │   ├── experiment_repeatability.py
│   │   ├── analyze_runs.py
│   │   └── health_check.py
│   ├── docs/               # Experiment protocol
│   ├── routes/             # Recorded route YAMLs  (created at runtime)
│   ├── collections/        # MCAP bag files         (created at runtime)
│   └── fix_ament_hooks.sh  # Required after every colcon build (see below)
├── backend/                # FastAPI + ROS 2 bridge
├── frontend/               # React + Vite
└── check.sh                # Local frontend/Python validation
```

---

## Prerequisites

### OS and ROS 2

- Ubuntu 24.04
- [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/Installation.html) (desktop install)

### ROS 2 simulation packages

```bash
sudo apt install \
  ros-jazzy-nav2-minimal-tb4-sim \
  ros-jazzy-turtlebot4-navigation \
  ros-jazzy-tf2-ros \
  ros-jazzy-tf2-py
```

### Python backend dependencies

```bash
sudo apt install \
  python3-fastapi \
  python3-uvicorn \
  python3-websockets \
  python3-yaml
```

### Node.js (frontend)

```bash
sudo apt install nodejs npm
```

---

## Installation

> **Important:** The workspace path must contain only ASCII characters.  
> Paths with accented letters (e.g. `~/Músicas/`) break `rosidl_cmake`.  
> Use a plain path like `~/fleet-ui`.

```bash
git clone <repo-url> ~/fleet-ui
```

### Build ROS 2 packages

```bash
cd ~/fleet-ui
bash build.sh
```

`build.sh` runs `colcon build --symlink-install` and then `fix_ament_hooks.sh`.

> `fix_ament_hooks.sh` is a workaround for a `colcon-ros 0.5.0` bug where
> `ament_python` packages are not added to `AMENT_PREFIX_PATH`. It must be
> run after every `colcon build`.

### Install frontend dependencies

```bash
cd ~/fleet-ui/frontend
npm install
```

---

## Running

Open **4 terminals**. Start them in order — Terminal 1 takes ~12 s to be ready.

### Terminal 1 — Simulation

Launches Gazebo Harmonic, SLAM Toolbox (after 8 s), and Nav2 (after 12 s).

```bash
cd ~/fleet-ui/fleet_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch fleet_orchestrator turtlebot4_sim.launch.py
```

Wait until you see `All BT navigator servers are active` before continuing.

Optional argument: `world:=depot` (default is `warehouse`).

### Terminal 2 — Fleet nodes

Starts `fleet_orchestrator` (route record/play) and `sensor_collector` (MCAP recording).

```bash
cd ~/fleet-ui/fleet_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch fleet_orchestrator fleet.launch.py single_robot_sim:=true
```

Ready when you see `fleet_orchestrator ready` and `sensor_collector ready`.

### Terminal 3 — Backend

FastAPI server that bridges ROS 2 topics/services to the web UI.

```bash
source /opt/ros/jazzy/setup.bash
source ~/fleet-ui/fleet_ws/install/setup.bash
cd ~/fleet-ui/backend
python3 main.py
```

Ready when you see `Uvicorn running on http://0.0.0.0:8000`.

Alternatively, use the helper script (handles sourcing automatically):

```bash
bash ~/fleet-ui/backend/run.sh
```

### Terminal 4 — Frontend

```bash
cd ~/fleet-ui/frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

### Optional healthcheck

After starting the four processes, run:

```bash
cd ~/fleet-ui
python3 fleet_ws/scripts/health_check.py
```

Useful variants:

```bash
# Only verify local files/tools, without live services.
python3 fleet_ws/scripts/health_check.py --skip-http --skip-ros

# Verify a backend/frontend running on another host.
python3 fleet_ws/scripts/health_check.py \
  --backend-url http://192.168.1.10:8000 \
  --frontend-url http://192.168.1.10:5173
```

The healthcheck reports missing commands, workspace packages, HTTP readiness,
ROS services/topics, and the Nav2 `/navigate_to_pose` action.

---

## After modifying ROS 2 packages

```bash
cd ~/fleet-ui
bash build.sh
# then re-source in any open terminal:
source ~/fleet-ui/fleet_ws/install/setup.bash
```

---

## Experiment workflow

### Record a route

1. Place waypoints on the map in the UI.
2. Click **Executar → record**.
3. The robot navigates the waypoints; the route is saved to `fleet_ws/routes/default/<name>.yaml`.
4. Sensor data is saved to `fleet_ws/collections/`.

### Replay a route

1. Select mode **Reproduzir** and choose a saved route.
2. Click **Executar → replay** (repeat N times as needed).

### Analyse results

```bash
cd ~/fleet-ui/fleet_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash
python3 scripts/analyze_runs.py \
  collections/default/baseline/*.mcap \
  collections/default/replay_1/*.mcap \
  --output-dir analysis_results/ \
  --resample-mode time \
  --resample-samples 100
```

Output: `summary.json` (RMSE metrics), `trajectory_overlay.png`, per-run CSVs.

`analyze_runs.py` aligns trajectories with normalized temporal interpolation by
default (`--resample-mode time`). Use `--resample-mode index` only to reproduce
legacy reports based on uniform index subsampling.

For controlled replay campaigns with multiple replicas:

```bash
cd ~/fleet-ui/fleet_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash
python3 scripts/experiment_repeatability.py replay \
  --single-robot \
  --route percurso_initial \
  --repeat 5 \
  --return-to-start 0,0,0 \
  --protocol-id val01 \
  --condition slam_reset=false \
  --export runs/val01_replay.json
```

With `--repeat N`, each replay writes a separate export file such as
`val01_replay_r01.json`, including protocol metadata (`protocol_id`,
`replicate_id`, `replicate_total`, `condition`, command line and notes).

---

## Development checks

Before opening a pull request or after changing frontend/backend scripts:

```bash
cd ~/fleet-ui
bash check.sh
```

This compiles the main Python files and runs `npm --prefix frontend run build`.
It does not start ROS, Gazebo, or Nav2.

---

## Backend configuration

The FastAPI backend accepts these optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `FLEET_WS` | repo root | Fleet UI repository root |
| `FLEET_ROS_WS` | `fleet_ws` under the repo root | ROS 2 colcon workspace |
| `FLEET_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed frontend origins |
| `FLEET_DISCOVERY_WORKERS` | `32` | Worker count for SSH port discovery |
| `FLEET_SSH_STRICT_HOST_KEY_CHECKING` | `accept-new` | SSH host-key policy used by `/api/test_ssh` |
| `FLEET_SSH_KNOWN_HOSTS` | unset | Optional custom known_hosts file for SSH tests |
