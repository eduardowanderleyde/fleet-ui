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
│   │   ├── fleet_data_collector/ # MCAP sensor recording
│   │   └── route_tool/           # Route utility (legacy)
│   ├── routes/             # Recorded route YAMLs  (created at runtime)
│   ├── collections/        # MCAP bag files         (created at runtime)
│   └── fix_ament_hooks.sh  # Required after every colcon build (see below)
├── backend/                # FastAPI + ROS 2 bridge
├── frontend/               # React + Vite
└── scripts/                # CLI tools: experiment_repeatability.py, analyze_runs.py
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
  --output-dir analysis_results/
```

Output: `summary.json` (RMSE metrics), `trajectory_overlay.png`, per-run CSVs.
