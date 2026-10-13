"""Cenário de missão: zonas nomeadas, robôs com papel e custo de um plano.

Um *plano* é ``{robot_id: [zona, zona, ...]}``: cada robô percorre suas zonas
na ordem da lista (entra pelo primeiro waypoint da zona, sai pelo último) e
no fim volta à própria posição inicial. Os robôs trabalham em paralelo, então
o custo da missão é o *makespan* (maior distância percorrida por um robô),
com a distância total como desempate.

Nesta fase o custo é distância euclidiana entre waypoints. Na execução em
simulação ele pode ser trocado pelo comprimento do caminho planejado pelo
Nav2 (ComputePathToPose) sem mudar a interface dos alocadores.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml

Point = tuple[float, float]

MOVABLE_ROLE = "MUUT"


def dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def path_length(points: tuple[Point, ...]) -> float:
    return sum(dist(a, b) for a, b in zip(points, points[1:]))


@dataclass(frozen=True)
class Zone:
    name: str
    description: str
    waypoints: tuple[Point, ...]

    @property
    def entry(self) -> Point:
        return self.waypoints[0]

    @property
    def exit(self) -> Point:
        return self.waypoints[-1]

    @property
    def length(self) -> float:
        return path_length(self.waypoints)


@dataclass(frozen=True)
class Robot:
    robot_id: str
    role: str
    start: Point

    @property
    def movable(self) -> bool:
        return self.role == MOVABLE_ROLE


@dataclass(frozen=True)
class Mission:
    mission_id: str
    text: str
    zones: tuple[str, ...]  # gabarito: zonas que a missão realmente pede


@dataclass(frozen=True)
class Scenario:
    name: str
    frame: str
    robots: dict[str, Robot]
    zones: dict[str, Zone]
    missions: dict[str, Mission]

    def movable_robots(self) -> list[Robot]:
        return sorted((r for r in self.robots.values() if r.movable), key=lambda r: r.robot_id)


def robot_plan_cost(robot: Robot, zones: list[Zone]) -> float:
    """Distância que o robô percorre executando `zones` em ordem e voltando ao início."""
    if not zones:
        return 0.0
    pos = robot.start
    total = 0.0
    for zone in zones:
        total += dist(pos, zone.entry) + zone.length
        pos = zone.exit
    return total + dist(pos, robot.start)


def plan_costs(scenario: Scenario, plans: dict[str, list[str]]) -> tuple[float, float]:
    """(makespan, distância total) de um plano já validado."""
    costs = [
        robot_plan_cost(scenario.robots[rid], [scenario.zones[z] for z in zones])
        for rid, zones in plans.items()
    ]
    return max(costs, default=0.0), sum(costs)


def _point(raw, where: str) -> Point:
    if not (isinstance(raw, (list, tuple)) and len(raw) == 2):
        raise ValueError(f"{where}: esperado [x, y], veio {raw!r}")
    return float(raw[0]), float(raw[1])


def load_scenario(path: str | Path) -> Scenario:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    robots = {
        rid: Robot(robot_id=rid, role=str(cfg["role"]), start=_point(cfg["start"], f"robots.{rid}.start"))
        for rid, cfg in data["robots"].items()
    }
    zones = {}
    for name, cfg in data["zones"].items():
        waypoints = tuple(_point(p, f"zones.{name}.waypoints") for p in cfg["waypoints"])
        if not waypoints:
            raise ValueError(f"zones.{name}: precisa de pelo menos 1 waypoint")
        zones[name] = Zone(name=name, description=str(cfg.get("description", "")), waypoints=waypoints)

    missions = {}
    for mid, cfg in data["missions"].items():
        mission_zones = tuple(cfg["zones"])
        unknown = [z for z in mission_zones if z not in zones]
        if unknown:
            raise ValueError(f"missions.{mid}: zonas desconhecidas {unknown}")
        missions[mid] = Mission(mission_id=mid, text=str(cfg["text"]).strip(), zones=mission_zones)

    return Scenario(
        name=str(data.get("name", Path(path).stem)),
        frame=str(data.get("frame", "map")),
        robots=robots,
        zones=zones,
        missions=missions,
    )
