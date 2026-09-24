"""
Backend FastAPI: bridge para o fleet (ROS 2).
Rode com o workspace sourceado: source install/setup.bash && python main.py
"""
from __future__ import annotations

import base64
import json
import math
import os
import shlex
import signal
import struct
import subprocess
import threading
import time
import zlib

import yaml
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ros_bridge import RosBridge
from agents import Analyst, Executor, Planner

# Robôs simulados (mesma variável usada pelos launch files ROS 2 — precisa
# bater com quem realmente existe no Gazebo). SLAM/Nav2 publicam map,
# amcl_pose e tf por-robô em /<id>/..., não mais em tópicos globais. Ver
# fleet_orchestrator._setup_robot_tf.
_ROBOTS = [r.strip() for r in os.environ.get("FLEET_ROBOTS", "tb1,tb2").split(",") if r.strip()]
# Robô usado como default no campo "pose"/"/api/map" sem robot_id explícito
# (compat com clientes antigos que não sabem que existe mais de um robô).
_STATUS_ROBOT_ID = os.environ.get("FLEET_STATUS_ROBOT") or (_ROBOTS[0] if _ROBOTS else "tb1")

# Raiz do projeto (fleet-ui/). Use FLEET_WS para sobrescrever.
WORKSPACE = os.environ.get("FLEET_WS") or str(Path(__file__).resolve().parent.parent)
# Workspace colcon ROS 2 (fleet_ws/ dentro da raiz)
ROS_WS = os.environ.get("FLEET_ROS_WS") or str(Path(WORKSPACE) / "fleet_ws")
_bridge = RosBridge(ROS_WS, ros_distro=os.environ.get("ROS_DISTRO", "jazzy"))

# Status da frota (atualizado pelo subscriber ROS em thread)
_fleet_status: dict = {"robots": []}
_robot_poses: dict[str, dict] = {rid: {"x": 0.0, "y": 0.0, "yaw": 0.0, "valid": False} for rid in _ROBOTS}
_map_metas: dict[str, dict] = {}  # robot_id -> {resolution, origin_x, origin_y, width, height, png_b64}
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


class AgentRunRequest(BaseModel):
    instruction: str
    model: str = "claude-sonnet-5"


class AgentFleetRunRequest(BaseModel):
    instructions: dict[str, str]  # robot_id → instrução
    model: str = "claude-sonnet-5"


class RunCampaignRequest(BaseModel):
    robot: str = "default"
    route: str = "percurso1"
    points: list[list[float]] = Field(default_factory=list)  # waypoints da gravação baseline
    repetitions: int = 3
    collect: bool = True
    topics: list[str] = Field(default_factory=lambda: ["scan", "odom", "imu", "pose"])
    return_to_start: list[float] | None = None
    run_id: str | None = None  # gerado automaticamente se omitido


class StartSimulationRequest(BaseModel):
    mode: Literal["single", "multi"] = "single"
    world: str = "warehouse"
    robots: list[str] = Field(default_factory=lambda: ["tb1", "tb2"])  # ignorado se mode="single"


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

            # TF lookup: map -> base_link por robô (fallback contínuo; /pose
            # do slam_toolbox só publica esporadicamente, não dá pose ao
            # vivo). tf2_ros.TransformListener hardcoda a subscrição em /tf e
            # /tf_static (tópicos globais); nesse branch cada robô publica em
            # /<id>/tf, então replicamos manualmente 1 Buffer + subscrições
            # namespaced por robô (mesmo padrão de
            # fleet_orchestrator._setup_robot_tf). Executor trocado para
            # MultiThreadedExecutor logo abaixo para não deixar o volume alto
            # de /tf de N robôs atrasar fleet/status e os N maps.
            import tf2_ros
            from rclpy.time import Time as RclpyTime
            from rclpy.qos import QoSProfile, DurabilityPolicy, HistoryPolicy
            from tf2_msgs.msg import TFMessage

            def _setup_robot(rid: str) -> None:
                prefix = f"/{rid}" if rid else ""
                tf_buffer = tf2_ros.Buffer()

                def _tf_dynamic_cb(msg):
                    for t in msg.transforms:
                        tf_buffer.set_transform(t, "default_authority")

                def _tf_static_cb(msg):
                    for t in msg.transforms:
                        tf_buffer.set_transform_static(t, "default_authority")

                node.create_subscription(
                    TFMessage, f"{prefix}/tf", _tf_dynamic_cb,
                    QoSProfile(depth=100, durability=DurabilityPolicy.VOLATILE, history=HistoryPolicy.KEEP_LAST),
                )
                node.create_subscription(
                    TFMessage, f"{prefix}/tf_static", _tf_static_cb,
                    QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL, history=HistoryPolicy.KEEP_LAST),
                )

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
                            _robot_poses.setdefault(rid, {}).update(
                                {"x": tr.x, "y": tr.y, "yaw": yaw, "valid": True}
                            )
                    except Exception:
                        pass

                node.create_timer(0.1, tf_timer_cb)

                def amcl_cb(msg):
                    p = msg.pose.pose.position
                    q = msg.pose.pose.orientation
                    yaw = math.atan2(
                        2.0 * (q.w * q.z + q.x * q.y),
                        1.0 - 2.0 * (q.y * q.y + q.z * q.z),
                    )
                    with _status_lock:
                        _robot_poses.setdefault(rid, {}).update(
                            {"x": p.x, "y": p.y, "yaw": yaw, "valid": True}
                        )

                node.create_subscription(PoseWithCovarianceStamped, f"{prefix}/amcl_pose", amcl_cb, 10)
                node.create_subscription(PoseWithCovarianceStamped, f"{prefix}/pose", amcl_cb, 10)

                def map_cb(msg):
                    info = msg.info
                    if info.width == 0 or info.height == 0:
                        return
                    try:
                        png = _encode_map_png(list(msg.data), info.width, info.height)
                        b64 = base64.b64encode(png).decode()
                        with _status_lock:
                            _map_metas[rid] = {
                                "resolution": info.resolution,
                                "origin_x": info.origin.position.x,
                                "origin_y": info.origin.position.y,
                                "width": info.width,
                                "height": info.height,
                                "png_b64": b64,
                            }
                    except Exception as e:
                        node.get_logger().warning(f"map_cb({rid!r}) error: {e}")

                node.create_subscription(OccupancyGrid, f"{prefix}/map", map_cb, 1)

            for _rid in _ROBOTS:
                _setup_robot(_rid)

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
            executor = rclpy.executors.MultiThreadedExecutor()
            executor.add_node(node)
            executor.spin()
            node.destroy_node()
            rclpy.shutdown()
        except Exception as e:
            print(f"[fleet_ui] ROS subscriber not started (source workspace?): {e}")

    t = threading.Thread(target=run_ros, daemon=True)
    t.start()
    yield


app = FastAPI(title="Fleet UI API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=_cors_origins(), allow_methods=["*"], allow_headers=["*"])


_EMPTY_POSE = {"x": 0.0, "y": 0.0, "yaw": 0.0, "valid": False}


def _status_payload() -> dict:
    # "pose" (singular) fica de compat com quem ainda não sabe que existe
    # mais de um robô; "poses" traz todos, é o que a UI multi-robô usa.
    return {
        **_fleet_status,
        "pose": _robot_poses.get(_STATUS_ROBOT_ID, _EMPTY_POSE),
        "poses": _robot_poses,
    }


@app.get("/api/status")
async def get_status():
    with _status_lock:
        return _status_payload()


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    _ws_clients.append(websocket)
    try:
        with _status_lock:
            payload = _status_payload()
        await websocket.send_text(json.dumps(payload))
        while True:
            await asyncio.sleep(0.25)
            with _status_lock:
                payload = _status_payload()
            await websocket.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _ws_clients:
            _ws_clients.remove(websocket)


import uuid

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
        job = _jobs[job_id]
        job["lines"].append(f"[CMD] {' '.join(cmd)}")
        try:
            step = _bridge.run_experiment_step(cmd, export_path, line_callback=job["lines"].append)
            job["result"] = step["result"]
            job["error"] = step["error"]
            job["exit_code"] = step["exit_code"]
        except Exception as ex:
            job["error"] = str(ex)
        finally:
            job["running"] = False

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


_campaign_jobs: dict = {}  # run_id → {running, steps: [...], summary, analysis_log, error}


def _campaign_steps(cfg: dict) -> list[tuple[str, dict]]:
    """1 gravação baseline + N reproduções, na mesma convenção de labels
    (baseline, replay_01, ...) que analyze_runs.py/Analyst já esperam."""
    steps = [("baseline", {**cfg, "command": "record"})]
    for i in range(1, int(cfg.get("repetitions", 3)) + 1):
        steps.append((f"replay_{i:02d}", {**cfg, "command": "replay"}))
    return steps


def _run_campaign(run_id: str, cfg: dict) -> None:
    job = _campaign_jobs[run_id]
    bag_paths: list[str] = []
    labels: list[str] = []

    for label, step_cfg in _campaign_steps(cfg):
        step = {"label": label, "lines": [], "result": None, "error": None, "exit_code": None}
        job["steps"].append(step)
        try:
            cmd = _build_cmd(step_cfg)
        except Exception as e:
            step["error"] = str(e)
            job["error"] = f"{label}: {e}"
            job["running"] = False
            return
        export_path = str(Path(ROS_WS) / f"_campaign_{run_id}_{label}.json")
        cmd += ["--export", export_path]
        step["lines"].append(f"[CMD] {' '.join(cmd)}")
        outcome = _bridge.run_experiment_step(cmd, export_path, line_callback=step["lines"].append)
        step["result"] = outcome["result"]
        step["error"] = outcome["error"]
        step["exit_code"] = outcome["exit_code"]
        if outcome["error"] or outcome["exit_code"] not in (0, None):
            job["error"] = f"{label} falhou (exit={outcome['exit_code']}): {outcome['error'] or 'ver lines do passo'}"
            job["running"] = False
            return
        bag_path = (outcome["result"] or {}).get("rosbag_path")
        if not bag_path:
            job["error"] = f"{label}: rosbag_path ausente no export (coleta desligada nesse passo?)"
            job["running"] = False
            return
        bag_paths.append(bag_path)
        labels.append(label)

    out_dir = str(Path(ROS_WS) / "runs" / run_id / "analysis")
    ok, out = _bridge.analyze_bags(bag_paths, labels, out_dir)
    job["analysis_log"] = out
    if not ok:
        job["error"] = f"analyze_runs.py falhou: {out[-800:]}"
        job["running"] = False
        return

    summary_path = Path(out_dir) / "summary.json"
    if summary_path.exists():
        job["summary"] = json.loads(summary_path.read_text())
        job["run_id"] = run_id
    else:
        job["error"] = "analyze_runs.py terminou mas summary.json não foi encontrado"
    job["running"] = False


@app.post("/api/run_campaign")
async def run_campaign(cfg: RunCampaignRequest):
    """Fecha o loop planner→campanha→análise: grava 1 baseline + N reproduções
    da mesma rota, roda analyze_runs.py sobre os bags resultantes, e deixa o
    summary.json em fleet_ws/runs/<run_id>/analysis/ — o mesmo formato que
    Analyst.analyze_experiment/compare_runs já leem. Assíncrono como
    /api/run_config: devolve run_id, consulte com /api/campaign_job/{run_id}."""
    cfg_data = _model_dump(cfg)
    if cfg_data["repetitions"] < 1:
        return JSONResponse({"success": False, "message": "repetitions deve ser >= 1"}, status_code=400)
    run_id = cfg_data.get("run_id") or f"{cfg_data['route']}_{uuid.uuid4().hex[:8]}"
    if run_id in _campaign_jobs and _campaign_jobs[run_id]["running"]:
        return JSONResponse({"success": False, "message": f"Campanha '{run_id}' já em execução"}, status_code=409)

    _campaign_jobs[run_id] = {"running": True, "steps": [], "summary": None, "analysis_log": None, "error": None}
    threading.Thread(target=_run_campaign, args=(run_id, cfg_data), daemon=True).start()
    return {"run_id": run_id}


@app.get("/api/campaign_job/{run_id}")
async def get_campaign_job(run_id: str):
    job = _campaign_jobs.get(run_id)
    if not job:
        return JSONResponse({"error": "campaign not found"}, status_code=404)
    return job


# ── Simulação (Terminais 1+2 do README, lançados pela UI) ──────────────────
#
# Recurso singleton (só 1 simulação por vez nesta v1) — diferente dos jobs
# acima, que rodam até terminar; aqui o processo fica de pé indefinidamente
# até /api/simulation/stop. `preexec_fn=os.setsid` é o que permite matar a
# árvore de processos inteira depois (gz sim + todos os nós do Nav2/SLAM) —
# sem isso, `pkill -f` sozinho deixou processos órfãos repetidas vezes ao
# testar isso manualmente nesta sessão.
_SIM_WORLDS = ["warehouse", "depot"]
_sim_state: dict = {
    "running": False, "ready": False, "mode": None, "world": None,
    "robots": [], "lines": [], "error": None,
}
_sim_procs: list[tuple[str, subprocess.Popen]] = []
_sim_lock = threading.Lock()
_sim_nav_ready_count = 0
_sim_fleet_ready = False


def _read_configured_robots() -> list[str]:
    """Robôs declarados em roles.yaml (fonte de verdade de quem existe,
    diferente de /api/list_robots, que exige fleet_orchestrator já rodando)."""
    path = Path(ROS_WS) / "src" / "fleet_orchestrator" / "config" / "roles.yaml"
    try:
        data = yaml.safe_load(path.read_text()) or {}
        return list((data.get("roles") or {}).keys())
    except Exception:
        return []


def _sim_append_line(tag: str, line: str) -> None:
    with _sim_lock:
        _sim_state["lines"].append(f"[{tag}] {line}")
        if len(_sim_state["lines"]) > 500:
            del _sim_state["lines"][: len(_sim_state["lines"]) - 500]


def _sim_reader_thread(tag: str, proc: subprocess.Popen, expected_nav_ready: int) -> None:
    global _sim_nav_ready_count, _sim_fleet_ready
    for raw in proc.stdout:
        line = raw.rstrip()
        if not line:
            continue
        _sim_append_line(tag, line)
        with _sim_lock:
            if "Managed nodes are active" in line:
                _sim_nav_ready_count += 1
            if "fleet_orchestrator ready" in line:
                _sim_fleet_ready = True
            if "Aborting bringup" in line or "Failed to bring up all requested nodes" in line:
                _sim_state["error"] = line
            if _sim_nav_ready_count >= expected_nav_ready and _sim_fleet_ready:
                _sim_state["ready"] = True


def _build_sim_commands(mode: str, world: str, robots: list[str]) -> list[tuple[str, list[str], dict]]:
    """[(tag, cmd, extra_env), ...] — mesmos dois launches do README
    (Terminal 1 + Terminal 2), montados programaticamente."""
    env_extra: dict = {}
    if mode == "single":
        # nav2_minimal_tb4_sim usa PythonExpression (eval() de verdade) pra
        # decidir gzclient — precisa ser "True" com maiúscula (Python), não
        # "true": com minúscula dá `NameError: name 'true' is not defined`.
        # turtlebot4_multi_sim.launch.py não tem esse problema (usa outra
        # condição, tolerante a minúscula) — assimetria real do vendor, não
        # inconsistência nossa.
        sim_cmd = ["ros2", "launch", "fleet_orchestrator", "turtlebot4_sim.launch.py",
                   f"world:={world}", "headless:=True"]
        fleet_cmd = ["ros2", "launch", "fleet_orchestrator", "fleet.launch.py",
                     "single_robot_sim:=true"]
    else:
        env_extra["FLEET_ROBOTS"] = ",".join(robots)
        sim_cmd = ["ros2", "launch", "fleet_orchestrator", "turtlebot4_multi_sim.launch.py",
                   f"world:={world}", "headless:=true"]
        fleet_cmd = ["ros2", "launch", "fleet_orchestrator", "fleet.launch.py"]
    return [("sim", sim_cmd, env_extra), ("fleet", fleet_cmd, env_extra)]


def _start_simulation(mode: str, world: str, robots: list[str]) -> None:
    global _sim_nav_ready_count, _sim_fleet_ready
    _sim_nav_ready_count = 0
    _sim_fleet_ready = False
    expected_nav_ready = len(robots) if mode == "multi" else 1
    for tag, cmd, env_extra in _build_sim_commands(mode, world, robots):
        env = {**_bridge.ros_env(), "PYTHONUNBUFFERED": "1", **env_extra}
        shell_cmd = _bridge.ros_setup_prefix() + " ".join(shlex.quote(c) for c in cmd)
        proc = subprocess.Popen(
            ["bash", "-c", shell_cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, cwd=ROS_WS, env=env,
            preexec_fn=os.setsid,
        )
        _sim_procs.append((tag, proc))
        threading.Thread(
            target=_sim_reader_thread, args=(tag, proc, expected_nav_ready), daemon=True,
        ).start()


def _stop_simulation() -> None:
    for _tag, proc in _sim_procs:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            continue
    time.sleep(3)
    for _tag, proc in _sim_procs:
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
    _sim_procs.clear()
    with _sim_lock:
        _sim_state.update({
            "running": False, "ready": False, "mode": None, "world": None,
            "robots": [], "lines": [], "error": None,
        })


@app.get("/api/simulation/options")
async def simulation_options():
    return {"worlds": _SIM_WORLDS, "robots": _read_configured_robots()}


@app.get("/api/simulation/status")
async def simulation_status():
    with _sim_lock:
        return dict(_sim_state)


@app.post("/api/simulation/start")
async def simulation_start(cfg: StartSimulationRequest):
    with _sim_lock:
        if _sim_state["running"]:
            return JSONResponse(
                {"success": False, "message": "Já existe uma simulação rodando — pare antes de iniciar outra."},
                status_code=409,
            )
        robots = cfg.robots if cfg.mode == "multi" else []
        _sim_state.update({
            "running": True, "ready": False, "mode": cfg.mode, "world": cfg.world,
            "robots": robots, "lines": [], "error": None,
        })
    _start_simulation(cfg.mode, cfg.world, robots)
    return {"success": True}


@app.post("/api/simulation/stop")
async def simulation_stop():
    _stop_simulation()
    return {"success": True}


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
async def get_map(robot_id: str = ""):
    rid = robot_id or _STATUS_ROBOT_ID
    with _status_lock:
        meta = _map_metas.get(rid)
        if not meta:
            return JSONResponse(content={"available": False})
        return {"available": True, "robot_id": rid, **meta}


@app.post("/api/save_background_map")
async def save_background_map(robot_id: str = ""):
    """Guarda o mapa SLAM actual como fundo persistente em public/slam_map.png + slam_map.json."""
    import base64 as _b64
    rid = robot_id or _STATUS_ROBOT_ID
    with _status_lock:
        meta = _map_metas.get(rid)
        if not meta or not meta.get("png_b64"):
            return JSONResponse({"success": False, "message": "Mapa SLAM não disponível ainda."}, status_code=400)
        meta = dict(meta)

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
    return {"robot_ids": _bridge.extract_list_field(out, "robot_ids")}


@app.get("/api/list_routes")
async def list_routes(robot_id: str = ""):
    robot_id = robot_id or ""
    ok, out = _run_ros2_service(
        "list_routes", "fleet_msgs/srv/ListRoutes",
        json.dumps({"robot_id": robot_id}),
    )
    if not ok:
        return {"route_names": []}
    return {"route_names": _bridge.extract_list_field(out, "route_names")}


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


_agent_jobs: dict = {}  # job_id → {running, steps, final_text, error}
_fleet_jobs: dict = {}  # job_id → {running, robots: {robot_id → {running, steps, final_text, error}}}
_AGENT_RUNS_DIR = Path(ROS_WS) / "agent_runs"  # persistência em disco — ver _save_agent_run


def _agent_base_url() -> str:
    """URL pela qual o Executor do agente chama de volta esta própria API."""
    return os.environ.get("FLEET_UI_BASE_URL", "http://127.0.0.1:8000")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _save_agent_run(file_stem: str, data: dict) -> None:
    """Persiste um job de agente (single ou fleet) já concluído em disco, para
    sobreviver a um restart do backend — _agent_jobs/_fleet_jobs são só memória.
    Best-effort: uma falha ao salvar não deve derrubar o job em si."""
    try:
        _AGENT_RUNS_DIR.mkdir(parents=True, exist_ok=True)
        (_AGENT_RUNS_DIR / f"{file_stem}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str)
        )
    except Exception as exc:
        print(f"[fleet_ui] falha ao salvar agent_run {file_stem}: {exc}")


def _load_agent_run(file_stem: str) -> dict | None:
    path = _AGENT_RUNS_DIR / f"{file_stem}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


async def _execute_planner(state: dict, instruction: str, model: str, robot_id: str | None = None) -> None:
    """Roda um Planner até concluir, escrevendo o resultado em `state` (dict de job).
    `robot_id`, se informado, restringe o Planner a um único robô (ver Planner.robot_id)."""
    executor = Executor(base_url=_agent_base_url())
    try:
        planner = Planner(executor, Analyst(), model=model, robot_id=robot_id)
        result = await planner.run(instruction)
        state["steps"] = [
            {"tool_name": s.tool_name, "tool_input": s.tool_input, "result": s.result}
            for s in result.steps
        ]
        state["final_text"] = result.final_text
    except Exception as exc:
        state["error"] = str(exc)
    finally:
        state["running"] = False
        await executor.aclose()


@app.post("/api/agent/run")
async def agent_run(body: AgentRunRequest):
    """Dispara o Planner de IA numa instrução em linguagem natural.
    Assíncrono como /api/run_config: devolve job_id, consulte com /api/agent/job/{id}."""
    instruction = (body.instruction or "").strip()
    if not instruction:
        return JSONResponse({"success": False, "message": "instruction vazia"}, status_code=400)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return JSONResponse({"success": False, "message": "ANTHROPIC_API_KEY não configurada"}, status_code=400)

    job_id = str(uuid.uuid4())[:8]
    _agent_jobs[job_id] = {
        "running": True, "steps": [], "final_text": None, "error": None,
        "instruction": instruction, "model": body.model, "started_at": _now_iso(), "finished_at": None,
    }

    async def _run_and_persist():
        await _execute_planner(_agent_jobs[job_id], instruction, body.model)
        _agent_jobs[job_id]["finished_at"] = _now_iso()
        _save_agent_run(f"single_{job_id}", {"kind": "single", "job_id": job_id, **_agent_jobs[job_id]})

    asyncio.create_task(_run_and_persist())
    return {"job_id": job_id}


@app.get("/api/agent/job/{job_id}")
async def agent_job(job_id: str):
    job = _agent_jobs.get(job_id) or _load_agent_run(f"single_{job_id}")
    if not job:
        return JSONResponse({"error": "job not found"}, status_code=404)
    return job


@app.post("/api/agent/run_fleet")
async def agent_run_fleet(body: AgentFleetRunRequest):
    """Dispara um Planner independente por robô, cada um restrito ao seu próprio
    robot_id, rodando em paralelo. `instructions` mapeia robot_id → instrução.
    Consulte com /api/agent/fleet_job/{id}."""
    instructions = {rid: instr.strip() for rid, instr in body.instructions.items() if instr and instr.strip()}
    if not instructions:
        return JSONResponse({"success": False, "message": "instructions vazio"}, status_code=400)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return JSONResponse({"success": False, "message": "ANTHROPIC_API_KEY não configurada"}, status_code=400)

    job_id = str(uuid.uuid4())[:8]
    robots_state = {
        rid: {"running": True, "steps": [], "final_text": None, "error": None, "instruction": instr}
        for rid, instr in instructions.items()
    }
    _fleet_jobs[job_id] = {
        "running": True, "robots": robots_state, "model": body.model,
        "started_at": _now_iso(), "finished_at": None,
    }

    async def _run_all():
        await asyncio.gather(*(
            _execute_planner(robots_state[rid], instr, body.model, robot_id=rid)
            for rid, instr in instructions.items()
        ))
        _fleet_jobs[job_id]["running"] = False
        _fleet_jobs[job_id]["finished_at"] = _now_iso()
        _save_agent_run(f"fleet_{job_id}", {"kind": "fleet", "job_id": job_id, **_fleet_jobs[job_id]})

    asyncio.create_task(_run_all())
    return {"job_id": job_id}


@app.get("/api/agent/fleet_job/{job_id}")
async def agent_fleet_job(job_id: str):
    job = _fleet_jobs.get(job_id) or _load_agent_run(f"fleet_{job_id}")
    if not job:
        return JSONResponse({"error": "job not found"}, status_code=404)
    return job


def _summarize_agent_run(data: dict) -> dict:
    base = {
        "kind": data.get("kind"),
        "job_id": data.get("job_id"),
        "model": data.get("model"),
        "started_at": data.get("started_at"),
        "finished_at": data.get("finished_at"),
    }
    if data.get("kind") == "fleet":
        base["robots"] = {
            rid: {"instruction": r.get("instruction"), "final_text": r.get("final_text"), "error": r.get("error")}
            for rid, r in (data.get("robots") or {}).items()
        }
    else:
        base["instruction"] = data.get("instruction")
        base["final_text"] = data.get("final_text")
        base["error"] = data.get("error")
    return base


@app.get("/api/agent/history")
async def agent_history(limit: int = 50):
    """Lista execuções passadas de agentes (persistidas em disco por _save_agent_run),
    mais recentes primeiro — sobrevive a um restart do backend."""
    if not _AGENT_RUNS_DIR.exists():
        return {"runs": []}
    files = sorted(_AGENT_RUNS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    runs = []
    for f in files[:max(1, limit)]:
        try:
            runs.append(_summarize_agent_run(json.loads(f.read_text())))
        except Exception:
            continue
    return {"runs": runs}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
