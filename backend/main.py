"""
Backend FastAPI: bridge para o fleet (ROS 2).
Rode com o workspace sourceado: source install/setup.bash && python main.py
"""
from __future__ import annotations

import base64
import json
import math
import os
import struct
import subprocess
import threading
import zlib
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ros_bridge import RosBridge

# Raiz do projeto (fleet-ui/). Use FLEET_WS para sobrescrever.
WORKSPACE = os.environ.get("FLEET_WS") or str(Path(__file__).resolve().parent.parent)
# Workspace colcon ROS 2 (fleet_ws/ dentro da raiz)
ROS_WS = os.environ.get("FLEET_ROS_WS") or str(Path(WORKSPACE) / "fleet_ws")
_bridge = RosBridge(ROS_WS, ros_distro=os.environ.get("ROS_DISTRO", "jazzy"))

# Status da frota (atualizado pelo subscriber ROS em thread)
_fleet_status: dict = {"robots": []}
_robot_pose: dict = {"x": 0.0, "y": 0.0, "yaw": 0.0, "valid": False}
_map_meta: dict = {}  # resolution, origin_x, origin_y, width, height, png_b64
_status_lock = threading.Lock()
_ws_clients: list[WebSocket] = []


def _ros_env():
    return _bridge.ros_env()


def _run_ros2_service(srv: str, srv_type: str, request_json: str, timeout: int = 10) -> tuple[bool, str]:
    return _bridge.run_service(srv, srv_type, request_json, timeout=timeout)


def _encode_map_png(data: list, width: int, height: int) -> bytes:
    """Codifica OccupancyGrid como PNG RGBA colorido (Y flipado para canvas).
    Paleta:
      desconhecido (-1): azul-cinza suave   #b0bcc8  semi-transparente
      livre        ( 0): branco quente      #f5f5f0
      ocupado      (>0): azul-escuro        #2d3748
    """
    # RGBA 4 bytes por pixel
    pixels: list[tuple[int, int, int, int]] = []
    for v in data:
        if v < 0:
            pixels.append((176, 188, 200, 210))  # desconhecido: azul-cinza
        elif v == 0:
            pixels.append((245, 245, 240, 255))  # livre: creme quase branco
        else:
            pixels.append((45, 55, 72, 255))     # ocupado: azul-escuro

    def make_row(row_idx: int) -> bytes:
        row = bytearray([0])  # filter type None
        for r, g, b, a in pixels[row_idx * width:(row_idx + 1) * width]:
            row.extend([r, g, b, a])
        return bytes(row)

    # Flipa Y: row 0 do PNG = maior y do mundo
    raw = b''.join(make_row(height - 1 - y) for y in range(height))
    compressed = zlib.compress(raw, 6)

    def png_chunk(tag: bytes, payload: bytes) -> bytes:
        body = tag + payload
        return struct.pack('>I', len(payload)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)

    png = b'\x89PNG\r\n\x1a\n'
    # color_type=6 → RGBA
    png += png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += png_chunk(b'IDAT', compressed)
    png += png_chunk(b'IEND', b'')
    return png


class RunConfigRequest(BaseModel):
    command: Literal["record", "replay"] = "record"
    robot: str = "default"
    route: str = "percurso1"
    collect: bool = True
    topics: list[str] = Field(default_factory=lambda: ["scan", "odom", "imu", "pose"])
    initial_pose: list[float] | None = None
    points: list[list[float]] = Field(default_factory=list)
    return_to_start: list[float] | None = None


class SaveRouteWaypointsRequest(BaseModel):
    robot_id: str = ""
    route_name: str
    waypoints: list[dict]


class SshTestRequest(BaseModel):
    host: str
    user: str = "ubuntu"
    port: int = 22


def _model_dump(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _cors_origins() -> list[str]:
    raw = os.environ.get("FLEET_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    def run_ros():
        try:
            import rclpy
            from rclpy.node import Node
            from fleet_msgs.msg import FleetStatus
            from geometry_msgs.msg import PoseWithCovarianceStamped
            from nav_msgs.msg import OccupancyGrid

            rclpy.init()
            node = Node("fleet_ui_bridge", parameter_overrides=[
                rclpy.parameter.Parameter("use_sim_time", rclpy.parameter.Parameter.Type.BOOL, True)
            ])

            def fleet_cb(msg):
                with _status_lock:
                    _fleet_status["robots"] = [
                        {
                            "robot_id": r.robot_id,
                            "role": r.role,
                            "nav_state": r.nav_state,
                            "current_route": r.current_route,
                            "collection_on": r.collection_on,
                            "collection_file": r.collection_file,
                            "last_error": r.last_error,
                            "bytes_written": r.bytes_written,
                        }
                        for r in msg.robots
                    ]

            def amcl_cb(msg):
                p = msg.pose.pose.position
                q = msg.pose.pose.orientation
                yaw = math.atan2(
                    2.0 * (q.w * q.z + q.x * q.y),
                    1.0 - 2.0 * (q.y * q.y + q.z * q.z),
                )
                with _status_lock:
                    _robot_pose.update({"x": p.x, "y": p.y, "yaw": yaw, "valid": True})

            # TF lookup: map → base_link (TurtleBot4 usa base_link)
            import tf2_ros
            from rclpy.time import Time as RclpyTime
            tf_buffer = tf2_ros.Buffer()
            tf2_ros.TransformListener(tf_buffer, node)

            def tf_timer_cb():
                try:
                    t = tf_buffer.lookup_transform("map", "base_link", RclpyTime())
                    tr = t.transform.translation
                    q = t.transform.rotation
                    yaw = math.atan2(
                        2.0 * (q.w * q.z + q.x * q.y),
                        1.0 - 2.0 * (q.y * q.y + q.z * q.z),
                    )
                    with _status_lock:
                        _robot_pose.update({"x": tr.x, "y": tr.y, "yaw": yaw, "valid": True})
                except Exception:
                    pass

            node.create_timer(0.1, tf_timer_cb)

            def map_cb(msg):
                info = msg.info
                if info.width == 0 or info.height == 0:
                    return
                try:
                    png = _encode_map_png(list(msg.data), info.width, info.height)
                    b64 = base64.b64encode(png).decode()
                    with _status_lock:
                        _map_meta.update({
                            "resolution": info.resolution,
                            "origin_x": info.origin.position.x,
                            "origin_y": info.origin.position.y,
                            "width": info.width,
                            "height": info.height,
                            "png_b64": b64,
                        })
                except Exception as e:
                    node.get_logger().warning(f"map_cb error: {e}")

            # Verifica Nav2 periodicamente via ros2 action list (mais confiável que ActionClient)
            def nav2_check_cb():
                try:
                    env = {**os.environ}
                    r = subprocess.run(
                        ["bash", "-c", "source /opt/ros/jazzy/setup.bash 2>/dev/null; ros2 action list 2>/dev/null"],
                        capture_output=True, text=True, timeout=3, env=env,
                    )
                    ready = "/navigate_to_pose" in r.stdout
                except Exception:
                    ready = False
                with _status_lock:
                    _fleet_status["nav2_ready"] = ready

            node.create_timer(3.0, nav2_check_cb)

            node.create_subscription(FleetStatus, "fleet/status", fleet_cb, 10)
            node.create_subscription(PoseWithCovarianceStamped, "amcl_pose", amcl_cb, 10)
            node.create_subscription(PoseWithCovarianceStamped, "pose", amcl_cb, 10)
            node.create_subscription(OccupancyGrid, "map", map_cb, 1)
            rclpy.spin(node)
            node.destroy_node()
            rclpy.shutdown()
        except Exception as e:
            print(f"[fleet_ui] ROS subscriber not started (source workspace?): {e}")

    t = threading.Thread(target=run_ros, daemon=True)
    t.start()
    yield


app = FastAPI(title="Fleet UI API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=_cors_origins(), allow_methods=["*"], allow_headers=["*"])


@app.get("/api/status")
async def get_status():
    with _status_lock:
        return {**_fleet_status, "pose": _robot_pose}


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    _ws_clients.append(websocket)
    try:
        with _status_lock:
            payload = {**_fleet_status, "pose": _robot_pose}
        await websocket.send_text(json.dumps(payload))
        while True:
            await asyncio.sleep(0.25)
            with _status_lock:
                payload = {**_fleet_status, "pose": _robot_pose}
            await websocket.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _ws_clients:
            _ws_clients.remove(websocket)


import uuid
import shlex

_jobs: dict = {}   # job_id → {running, lines, result, error}


def _build_cmd(cfg: dict) -> list[str]:
    return _bridge.build_experiment_cmd(cfg)


@app.post("/api/run_config")
async def run_config(cfg: RunConfigRequest):
    cfg_data = _model_dump(cfg)
    job_id = str(uuid.uuid4())[:8]
    export_path = str(Path(ROS_WS) / f"_job_{job_id}.json")
    try:
        cmd = _build_cmd(cfg_data)
        cmd += ["--export", export_path]
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=400)

    _jobs[job_id] = {"running": True, "lines": [], "result": None, "error": None, "exit_code": None}

    def _run():
        env = {**_ros_env(), "PYTHONUNBUFFERED": "1"}
        ros_setup = f"source /opt/ros/jazzy/setup.bash 2>/dev/null; source {ROS_WS}/install/setup.bash 2>/dev/null; "
        shell_cmd = ros_setup + " ".join(shlex.quote(c) for c in cmd)
        _jobs[job_id]["lines"].append(f"[CMD] {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                ["bash", "-c", shell_cmd],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, cwd=ROS_WS, env=env,
            )
            _NOISE = ("TF_OLD_DATA", "RTPS_TRANSPORT_SHM", "Possible reasons", "ros.org/tf")
            for line in proc.stdout:
                l = line.rstrip()
                if any(n in l for n in _NOISE):
                    continue
                _jobs[job_id]["lines"].append(l)
            proc.wait()
            _jobs[job_id]["exit_code"] = proc.returncode
            # load export json
            ep = Path(export_path)
            if ep.exists():
                import json as _json
                _jobs[job_id]["result"] = _json.loads(ep.read_text())
                ep.unlink(missing_ok=True)
        except Exception as ex:
            _jobs[job_id]["error"] = str(ex)
        finally:
            _jobs[job_id]["running"] = False

    threading.Thread(target=_run, daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/job/{job_id}")
async def get_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "job not found"}, status_code=404)
    return {
        "running": job["running"],
        "lines": job["lines"],
        "result": job["result"],
        "error": job["error"],
        "exit_code": job["exit_code"],
    }


@app.post("/api/save_route_waypoints")
async def save_route_waypoints(body: SaveRouteWaypointsRequest):
    """Salva lista de waypoints diretamente como yaml (sem precisar do record flow)."""
    import yaml
    data_in = _model_dump(body)
    robot_id = data_in.get("robot_id", "") or ""
    route_name = (data_in.get("route_name") or "").strip()
    waypoints = data_in.get("waypoints", [])
    if not route_name:
        return JSONResponse(content={"success": False, "message": "route_name vazio"}, status_code=400)
    if not waypoints:
        return JSONResponse(content={"success": False, "message": "waypoints vazio"}, status_code=400)
    folder = "default" if not robot_id else robot_id
    routes_dir = Path(ROS_WS) / "routes" / folder
    routes_dir.mkdir(parents=True, exist_ok=True)
    path = routes_dir / f"{route_name}.yaml"
    data = {
        "route_name": route_name,
        "frame": "map",
        "poses": [{"x": float(w.get("x", 0)), "y": float(w.get("y", 0)), "yaw": float(w.get("yaw", 0))} for w in waypoints],
    }
    path.write_text(yaml.dump(data, default_flow_style=False))
    return {"success": True, "message": f"Salvo {len(waypoints)} waypoints em {path}"}


@app.get("/api/map")
async def get_map():
    with _status_lock:
        if not _map_meta:
            return JSONResponse(content={"available": False})
        return {"available": True, **_map_meta}


@app.post("/api/save_background_map")
async def save_background_map():
    """Guarda o mapa SLAM actual como fundo persistente em public/slam_map.png + slam_map.json."""
    import base64 as _b64
    with _status_lock:
        if not _map_meta or not _map_meta.get("png_b64"):
            return JSONResponse({"success": False, "message": "Mapa SLAM não disponível ainda."}, status_code=400)
        meta = dict(_map_meta)

    public_dir = Path(WORKSPACE) / "frontend" / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    png_bytes = _b64.b64decode(meta["png_b64"])
    (public_dir / "slam_map.png").write_bytes(png_bytes)

    import json as _json
    slam_meta = {k: v for k, v in meta.items() if k != "png_b64"}
    (public_dir / "slam_map.json").write_text(_json.dumps(slam_meta))

    return {"success": True, "message": f"Mapa guardado ({meta['width']}×{meta['height']} px, res={meta['resolution']:.3f} m/px)"}


@app.get("/api/slam_map_meta")
async def get_slam_map_meta():
    """Devolve metadados do slam_map.json guardado (se existir)."""
    meta_path = Path(WORKSPACE) / "frontend" / "public" / "slam_map.json"
    if not meta_path.exists():
        return JSONResponse({"available": False})
    import json as _json
    return {"available": True, **_json.loads(meta_path.read_text())}


@app.post("/api/start_record")
async def start_record(robot_id: str = "", route_name: str = "r1"):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "start_record", "fleet_msgs/srv/StartRecord",
        json.dumps({"robot_id": robot_id, "route_name": route_name}),
    )
    return {"success": ok, "message": out}


@app.post("/api/stop_record")
async def stop_record(robot_id: str = ""):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "stop_record", "fleet_msgs/srv/StopRecord",
        json.dumps({"robot_id": robot_id}),
    )
    return {"success": ok, "message": out}


@app.post("/api/play_route")
async def play_route(robot_id: str = "", route_name: str = "r1"):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "play_route", "fleet_msgs/srv/PlayRoute",
        json.dumps({"robot_id": robot_id, "route_name": route_name}),
    )
    return {"success": ok, "message": out}


@app.post("/api/go_to_point")
async def go_to_point(robot_id: str = "", x: float = 0.0, y: float = 0.0, yaw: float = 0.0):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "go_to_point", "fleet_msgs/srv/GoToPoint",
        json.dumps({"robot_id": robot_id, "x": x, "y": y, "yaw": yaw}),
    )
    return {"success": ok, "message": out}


@app.post("/api/cancel")
async def cancel(robot_id: str = ""):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "cancel", "fleet_msgs/srv/Cancel",
        json.dumps({"robot_id": robot_id}),
    )
    return {"success": ok, "message": out}


@app.get("/api/list_robots")
async def list_robots():
    ok, out = _run_ros2_service("list_robots", "fleet_msgs/srv/ListRobots", "{}")
    if not ok:
        return JSONResponse(content={"robot_ids": []}, status_code=200)
    try:
        import yaml
        data = yaml.safe_load(out) if out else {}
        robot_ids = data.get("robot_ids", []) or []
        return {"robot_ids": robot_ids}
    except Exception:
        return {"robot_ids": []}


@app.get("/api/list_routes")
async def list_routes(robot_id: str = ""):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "list_routes", "fleet_msgs/srv/ListRoutes",
        json.dumps({"robot_id": robot_id}),
    )
    if not ok:
        return {"route_names": []}
    try:
        import yaml
        data = yaml.safe_load(out) if out else {}
        return {"route_names": data.get("route_names", []) or []}
    except Exception:
        return {"route_names": []}


@app.post("/api/enable_collection")
async def enable_collection(robot_id: str = "", topics: str = "scan,odom", output_mode: str = "rosbag2"):
    robot_id = robot_id or ""
    topic_list = [t.strip() for t in topics.split(",") if t.strip()] or ["scan", "odom"]
    ok, out = _run_ros2_service(
        "enable_collection", "fleet_msgs/srv/EnableCollection",
        json.dumps({"robot_id": robot_id, "topics": topic_list, "output_mode": output_mode}),
    )
    return {"success": ok, "message": out}


@app.post("/api/disable_collection")
async def disable_collection(robot_id: str = ""):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "disable_collection", "fleet_msgs/srv/DisableCollection",
        json.dumps({"robot_id": robot_id}),
    )
    return {"success": ok, "message": out}


@app.get("/api/discover_robots")
async def discover_robots(subnet: str = ""):
    """
    Varre a subnet por hosts com porta 22 aberta e testa se têm ROS 2.
    subnet ex: '192.168.1' (varre .1–.254).
    Se omitido, detecta automaticamente a subnet local.
    """
    return _bridge.discover_robots(subnet)


@app.post("/api/test_ssh")
async def test_ssh(body: SshTestRequest):
    """Testa SSH num host: verifica conexão e presença do ROS 2."""
    data = _model_dump(body)
    host = (data.get("host") or "").strip()
    user = (data.get("user") or "ubuntu").strip()
    port = int(data.get("port") or 22)
    if not host:
        return JSONResponse({"success": False, "message": "host vazio"}, status_code=400)
    return _bridge.test_ssh(host=host, user=user, port=port)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
