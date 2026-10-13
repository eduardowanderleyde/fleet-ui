"""Cenário de missão: zonas nomeadas, robôs com papel e custo de um plano.

Um *plano* é ``{robot_id: [zona, zona, ...]}``: cada robô percorre suas zonas
na ordem da lista (entra pelo primeiro waypoint da zona, sai pelo último) e
no fim volta à própria posição inicial. Os robôs trabalham em paralelo, então
o custo da missão é o *makespan* (maior distância percorrida por um robô),
com a distância total como desempate.

A distância entre dois pontos é a métrica do cenário: linha reta
(`distance: euclidean`, padrão) ou caminho livre no mapa de ocupação
(`distance: grid`, ver gridmap.py). Uma missão pode sobrescrever o estado de
robôs (indisponível, posição atual) para simular uma falha no meio da missão.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import yaml

Point = tuple[float, float]
Metric = Callable[[Point, Point], float]

MOVABLE_ROLE = "MUUT"


def dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


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


@dataclass(frozen=True)
class Robot:
    robot_id: str
    role: str
    start: Point
    available: bool = True

    @property
    def movable(self) -> bool:
        return self.role == MOVABLE_ROLE and self.available


@dataclass(frozen=True)
class Mission:
    mission_id: str
    text: str
    zones: tuple[str, ...]  # gabarito: zonas que a missão realmente pede
    category: str = ""
    robot_overrides: dict = field(default_factory=dict, compare=False)


@dataclass(frozen=True)
class Scenario:
    name: str
    frame: str
    robots: dict[str, Robot]
    zones: dict[str, Zone]
    missions: dict[str, Mission]
    metric: Metric = field(default=dist, compare=False, repr=False)
    metric_name: str = "euclidean"
    map_notes: str = ""

    def movable_robots(self) -> list[Robot]:
        return sorted((r for r in self.robots.values() if r.movable), key=lambda r: r.robot_id)

    def zone_length(self, zone: Zone) -> float:
        return sum(self.metric(a, b) for a, b in zip(zone.waypoints, zone.waypoints[1:]))

    def for_mission(self, mission: Mission) -> "Scenario":
        """Cenário com o estado dos robôs no momento da missão (falhas, posição atual)."""
        if not mission.robot_overrides:
            return self
        robots = dict(self.robots)
        for rid, changes in mission.robot_overrides.items():
            robots[rid] = dataclasses.replace(robots[rid], **changes)
        return dataclasses.replace(self, robots=robots)


def robot_plan_cost(scenario: Scenario, robot: Robot, zones: list[Zone]) -> float:
    """Distância que o robô percorre executando `zones` em ordem e voltando ao início."""
    if not zones:
        return 0.0
    metric = scenario.metric
    pos = robot.start
    total = 0.0
    for zone in zones:
        total += metric(pos, zone.entry) + scenario.zone_length(zone)
        pos = zone.exit
    return total + metric(pos, robot.start)


def plan_costs(scenario: Scenario, plans: dict[str, list[str]]) -> tuple[float, float]:
    """(makespan, distância total) de um plano já validado."""
    costs = [
        robot_plan_cost(scenario, scenario.robots[rid], [scenario.zones[z] for z in zones])
        for rid, zones in plans.items()
    ]
    return max(costs, default=0.0), sum(costs)


def _point(raw, where: str) -> Point:
    if not (isinstance(raw, (list, tuple)) and len(raw) == 2):
        raise ValueError(f"{where}: esperado [x, y], veio {raw!r}")
    return float(raw[0]), float(raw[1])


def _robot_overrides(raw: dict, robots: dict[str, Robot], where: str) -> dict:
    overrides = {}
    for rid, cfg in (raw or {}).items():
        if rid not in robots:
            raise ValueError(f"{where}: robô desconhecido {rid}")
        changes = {}
        if "start" in cfg:
            changes["start"] = _point(cfg["start"], f"{where}.{rid}.start")
        if "available" in cfg:
            changes["available"] = bool(cfg["available"])
        overrides[rid] = changes
    return overrides


class GridMetric:
    """Métrica de caminho no mapa; guarda o grid para a validação de alcance."""

    def __init__(self, grid) -> None:
        self.grid = grid

    def __call__(self, a: Point, b: Point) -> float:
        return self.grid.distance(a, b)


def _grid_metric(path: Path, cfg: dict) -> Metric:
    from .gridmap import GridMap

    return GridMetric(GridMap(
        image_path=(path.parent / cfg["image"]).resolve(),
        resolution=float(cfg["resolution"]),
        origin=_point(cfg["origin"], "map.origin"),
        inflate_m=float(cfg.get("inflate_m", 0.25)),
        cell_m=float(cfg.get("cell_m", 0.1)),
    ))


def _check_reachable(scenario: Scenario) -> None:
    grid = getattr(scenario.metric, "grid", None)
    if grid is None:
        return
    points = {f"robots.{r.robot_id}.start": r.start for r in scenario.robots.values()}
    for z in scenario.zones.values():
        points.update({f"zones.{z.name}.waypoints[{i}]": p for i, p in enumerate(z.waypoints)})
    for m in scenario.missions.values():
        for rid, changes in m.robot_overrides.items():
            if "start" in changes:
                points[f"missions.{m.mission_id}.robots.{rid}.start"] = changes["start"]
    blocked = [k for k, p in points.items() if not grid.is_free(p)]
    if blocked:
        raise ValueError(f"pontos em obstáculo (após inflar): {blocked}")
    ref = next(iter(scenario.robots.values())).start
    unreachable = [k for k, p in points.items() if math.isinf(scenario.metric(ref, p))]
    if unreachable:
        raise ValueError(f"pontos sem caminho até {ref}: {unreachable}")


def load_scenario(path: str | Path) -> Scenario:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

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
        missions[mid] = Mission(
            mission_id=mid,
            text=" ".join(str(cfg["text"]).split()),
            zones=mission_zones,
            category=str(cfg.get("category", "")),
            robot_overrides=_robot_overrides(cfg.get("robots"), robots, f"missions.{mid}.robots"),
        )

    metric_name = str(data.get("distance", "euclidean"))
    if metric_name == "euclidean":
        metric = dist
    elif metric_name == "grid":
        metric = _grid_metric(path, data["map"])
    else:
        raise ValueError(f"distance desconhecida: {metric_name}")

    scenario = Scenario(
        name=str(data.get("name", path.stem)),
        frame=str(data.get("frame", "map")),
        robots=robots,
        zones=zones,
        missions=missions,
        metric=metric,
        metric_name=metric_name,
        map_notes=" ".join(str(data.get("map_notes", "")).split()),
    )
    _check_reachable(scenario)
    return scenario
