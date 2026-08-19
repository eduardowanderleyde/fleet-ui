from __future__ import annotations

import concurrent.futures
import json
import os
import shlex
import socket
import subprocess
from pathlib import Path


class RosBridge:
    """Boundary for shell/ROS integration used by the FastAPI layer."""

    def __init__(self, ros_ws: str, *, ros_distro: str = "jazzy") -> None:
        self.ros_ws = str(Path(ros_ws))
        self.ros_distro = ros_distro

    def ros_env(self) -> dict:
        return {
            **os.environ,
            "ROS_DOMAIN_ID": os.environ.get("ROS_DOMAIN_ID", "0"),
        }

    def ros_setup_prefix(self) -> str:
        return (
            f"source /opt/ros/{shlex.quote(self.ros_distro)}/setup.bash 2>/dev/null; "
            f"source {shlex.quote(self.ros_ws)}/install/setup.bash 2>/dev/null; "
        )

    def run_service(self, service: str, service_type: str, request: dict | str, timeout: int = 10) -> tuple[bool, str]:
        request_json = request if isinstance(request, str) else json.dumps(request)
        cmd = f"{self.ros_setup_prefix()}ros2 service call {shlex.quote(service)} {shlex.quote(service_type)} {shlex.quote(request_json)}"
        try:
            result = subprocess.run(
                ["bash", "-c", cmd],
                env=self.ros_env(),
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.ros_ws,
            )
            out = (result.stdout or "").strip() + (result.stderr or "").strip()
            if result.returncode != 0:
                return False, out or "ros2 service call failed"
            return True, out
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as exc:
            return False, str(exc)

    def build_experiment_cmd(self, cfg: dict) -> list[str]:
        command = cfg.get("command", "record")
        robot = cfg.get("robot", "")
        single = not robot or robot == "default"
        route = cfg.get("route", "percurso1")
        collect = cfg.get("collect", True)
        topics = cfg.get("topics", ["scan", "odom", "imu", "pose"])
        initial_pose = cfg.get("initial_pose")
        args = [
            "python3", str(Path(self.ros_ws) / "scripts" / "experiment_repeatability.py"),
            command, "--route", route,
        ]
        if single:
            args += ["--single-robot"]
        else:
            args += ["--robot", robot]
        if not collect:
            args += ["--skip-collection"]
        elif topics:
            args += ["--topics"] + topics
        if initial_pose is not None and any(v != 0 for v in initial_pose):
            args += [f"--initial-pose={initial_pose[0]},{initial_pose[1]},{initial_pose[2]}"]
        if command == "record":
            points = cfg.get("points", [])
            if points:
                joined = ";".join(f"{p[0]},{p[1]},{p[2] if len(p) > 2 else 0}" for p in points)
                args += [f"--points={joined}"]
        elif command == "replay":
            return_to_start = cfg.get("return_to_start")
            if return_to_start and any(v != 0 for v in return_to_start):
                args += [f"--return-to-start={return_to_start[0]},{return_to_start[1]},{return_to_start[2]}"]
        return args

    def discover_robots(self, subnet: str = "") -> dict:
        subnet = subnet.strip()
        if not subnet:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(("8.8.8.8", 80))
                local_ip = sock.getsockname()[0]
                sock.close()
                subnet = ".".join(local_ip.split(".")[:3])
            except Exception:
                return {
                    "found": [],
                    "subnet_scanned": "",
                    "error": "Não foi possível detectar subnet local. Informe manualmente (ex: 192.168.1)",
                }

        parts = subnet.split(".")
        if len(parts) != 3 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            return {
                "found": [],
                "subnet_scanned": subnet,
                "error": f"Subnet inválida: {subnet}. Use formato X.X.X (ex: 192.168.1)",
            }

        targets = [f"{subnet}.{i}" for i in range(1, 255)]

        def check(ip: str) -> dict | None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                result = sock.connect_ex((ip, 22))
                sock.close()
                if result != 0:
                    return None
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = ip
                is_robot = any(kw in hostname.lower() for kw in ("tb", "turtle", "robot", "pi", "nano", "jetson", "ros"))
                return {"ip": ip, "hostname": hostname, "ssh": True, "likely_robot": is_robot}
            except Exception:
                return None

        found = []
        max_workers = int(os.environ.get("FLEET_DISCOVERY_WORKERS", "32"))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(check, targets):
                if result:
                    found.append(result)

        found.sort(key=lambda item: (not item["likely_robot"], item["ip"]))
        return {"found": found, "subnet_scanned": subnet}

    def test_ssh(self, host: str, user: str = "ubuntu", port: int = 22) -> dict:
        if not host:
            return {"success": False, "message": "host vazio"}

        strict = os.environ.get("FLEET_SSH_STRICT_HOST_KEY_CHECKING", "accept-new")
        known_hosts = os.environ.get("FLEET_SSH_KNOWN_HOSTS")
        options = [
            "-o", "ConnectTimeout=4",
            "-o", f"StrictHostKeyChecking={strict}",
            "-o", "BatchMode=yes",
        ]
        if known_hosts:
            options += ["-o", f"UserKnownHostsFile={known_hosts}"]

        remote = f"{user}@{host}"
        cmd = [
            "ssh",
            *options,
            "-p", str(port),
            remote,
            "which ros2 && ros2 --version 2>/dev/null || echo NO_ROS2",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            out = (result.stdout or "").strip()
            err = (result.stderr or "").strip()
            if result.returncode != 0:
                return {"success": False, "message": err or f"SSH falhou (exit {result.returncode})"}
            has_ros = "NO_ROS2" not in out and bool(out)
            return {
                "success": True,
                "has_ros2": has_ros,
                "ros2_version": out if has_ros else None,
                "message": f"ROS 2 encontrado: {out}" if has_ros else "SSH OK mas ROS 2 não encontrado",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Timeout ao conectar via SSH"}
        except Exception as exc:
            return {"success": False, "message": str(exc)}
