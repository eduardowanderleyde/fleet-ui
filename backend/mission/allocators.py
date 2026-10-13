"""Alocadores de zonas para uma missão multi-robô.

Todos recebem o mesmo cenário e a mesma missão e devolvem uma `Allocation`
com o mesmo critério de custo (makespan, depois distância total), para que a
comparação entre eles seja justa:

- `FixedAllocator`: zona i vai pro robô i % N, na ordem da missão — o que o
  painel Missão Coordenada faz hoje. Referência ingênua.
- `GreedyAllocator`: cada zona, na ordem da missão, vai pro robô que menos
  aumenta o makespan. Determinístico, barato.
- `OptimalAllocator`: busca exaustiva (atribuição + ordem por robô). Ótimo
  para o critério acima; viável para missões pequenas (até 8 zonas).
- `LLMAllocator`: o Claude lê o texto da missão, decide quais zonas ela pede
  e a quem atribuir. Não determinístico — por isso o estudo o repete N vezes.

Só robôs de papel MUUT podem receber zonas (mesma regra do orquestrador).
"""
from __future__ import annotations

import itertools
import json
import time
from dataclasses import asdict, dataclass, field
from functools import lru_cache

from .model import Mission, Scenario, dist, plan_costs, robot_plan_cost

DEFAULT_MODEL = "claude-opus-5-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
MAX_OPTIMAL_ZONES = 8


@dataclass
class Allocation:
    allocator: str
    mission_id: str
    plans: dict[str, list[str]]  # robot_id -> zonas na ordem de execução
    makespan: float | None = None
    total_distance: float | None = None
    issues: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.issues

    def signature(self) -> str:
        """Forma canônica do plano (ordem importa dentro de cada robô)."""
        return json.dumps({r: z for r, z in sorted(self.plans.items()) if z}, sort_keys=True)

    def partition_signature(self) -> str:
        """Quem ficou com quais zonas, ignorando a ordem de execução."""
        return json.dumps({r: sorted(z) for r, z in sorted(self.plans.items()) if z}, sort_keys=True)

    def to_dict(self) -> dict:
        return {**asdict(self), "valid": self.valid, "signature": self.signature()}


def validate_plans(scenario: Scenario, mission: Mission, plans: dict[str, list[str]]) -> list[str]:
    issues = []
    assigned: list[str] = []
    for rid, zones in plans.items():
        robot = scenario.robots.get(rid)
        if robot is None:
            issues.append(f"robo_desconhecido: {rid}")
            continue
        if zones and not robot.movable:
            issues.append(f"papel_violado: {rid} ({robot.role}) recebeu {zones}")
        for z in zones:
            if z not in scenario.zones:
                issues.append(f"zona_desconhecida: {z}")
        assigned.extend(zones)

    for z in sorted({z for z in assigned if assigned.count(z) > 1}):
        issues.append(f"zona_repetida: {z}")
    for z in mission.zones:
        if z not in assigned:
            issues.append(f"zona_faltando: {z}")
    for z in sorted(set(assigned) - set(mission.zones)):
        if z in scenario.zones:
            issues.append(f"zona_extra: {z}")
    return issues


def build_allocation(
    name: str, scenario: Scenario, mission: Mission, plans: dict[str, list[str]], meta: dict | None = None,
) -> Allocation:
    plans = {rid: list(zones) for rid, zones in plans.items() if zones}
    issues = validate_plans(scenario, mission, plans)
    alloc = Allocation(allocator=name, mission_id=mission.mission_id, plans=plans, issues=issues, meta=meta or {})
    names_known = all(r in scenario.robots for r in plans) and all(
        z in scenario.zones for zones in plans.values() for z in zones
    )
    if names_known:
        alloc.makespan, alloc.total_distance = plan_costs(scenario, plans)
    return alloc


class FixedAllocator:
    name = "fixed"
    deterministic = True

    def allocate(self, scenario: Scenario, mission: Mission) -> Allocation:
        robots = scenario.movable_robots()
        plans: dict[str, list[str]] = {r.robot_id: [] for r in robots}
        for i, zone in enumerate(mission.zones):
            plans[robots[i % len(robots)].robot_id].append(zone)
        return build_allocation(self.name, scenario, mission, plans)


class GreedyAllocator:
    name = "greedy"
    deterministic = True

    def allocate(self, scenario: Scenario, mission: Mission) -> Allocation:
        robots = scenario.movable_robots()
        plans: dict[str, list[str]] = {r.robot_id: [] for r in robots}
        for zone in mission.zones:
            best = None
            for robot in robots:
                trial = {**plans, robot.robot_id: plans[robot.robot_id] + [zone]}
                makespan, total = plan_costs(scenario, trial)
                key = (round(makespan, 9), round(total, 9), robot.robot_id)
                if best is None or key < best[0]:
                    best = (key, robot.robot_id)
            plans[best[1]].append(zone)
        return build_allocation(self.name, scenario, mission, plans)


class OptimalAllocator:
    name = "optimal"
    deterministic = True

    def allocate(self, scenario: Scenario, mission: Mission) -> Allocation:
        zones = list(mission.zones)
        if len(zones) > MAX_OPTIMAL_ZONES:
            raise ValueError(f"OptimalAllocator: {len(zones)} zonas > {MAX_OPTIMAL_ZONES} (busca exaustiva)")
        robots = scenario.movable_robots()

        @lru_cache(maxsize=None)
        def best_order(robot_id: str, subset: frozenset) -> tuple[float, tuple[str, ...]]:
            robot = scenario.robots[robot_id]
            best = (0.0, ())
            for order in itertools.permutations(sorted(subset)):
                cost = robot_plan_cost(robot, [scenario.zones[z] for z in order])
                if not best[1] or cost < best[0] - 1e-9:
                    best = (cost, order)
            return best

        best_key, best_plans = None, None
        for assignment in itertools.product(range(len(robots)), repeat=len(zones)):
            plans = {}
            costs = []
            for i, robot in enumerate(robots):
                subset = frozenset(z for z, a in zip(zones, assignment) if a == i)
                cost, order = best_order(robot.robot_id, subset)
                plans[robot.robot_id] = list(order)
                costs.append(cost)
            key = (round(max(costs), 9), round(sum(costs), 9), json.dumps(plans, sort_keys=True))
            if best_key is None or key < best_key:
                best_key, best_plans = key, plans
        return build_allocation(self.name, scenario, mission, best_plans)


SYSTEM_PROMPT = """\
Você distribui as zonas de uma missão de inspeção entre os robôs de uma frota.

Regras:
1. Só robôs de papel MUUT (unidade móvel) podem receber zonas. Robôs FUUT \
(sensor fixo) e SU (suporte) nunca se movem.
2. Identifique quais zonas a missão pede e atribua cada uma a exatamente um \
robô. Não inclua zonas que a missão não pede.
3. Cada robô percorre suas zonas na ordem da lista: entra pelo primeiro ponto \
da zona, sai pelo último e, ao terminar todas, volta à própria posição inicial.
4. Os robôs trabalham em paralelo. Minimize o tempo total da missão, ou seja, \
a maior distância percorrida por um único robô; em caso de empate, a soma das \
distâncias de todos os robôs.

Robôs sem zona podem ficar fora da resposta. Em "justification", explique a \
decisão em uma ou duas frases."""


def _fmt(p) -> str:
    return f"({p[0]:.1f}, {p[1]:.1f})"


def build_user_prompt(scenario: Scenario, mission: Mission, include_distances: bool) -> str:
    lines = [f"Missão: {mission.text}", "", f"Zonas do ambiente (metros, frame {scenario.frame}):"]
    for zone in scenario.zones.values():
        route = " → ".join(_fmt(p) for p in zone.waypoints)
        lines.append(f"- {zone.name}: {zone.description} Percurso {route} ({zone.length:.1f} m).")
    lines += ["", "Robôs:"]
    for robot in sorted(scenario.robots.values(), key=lambda r: r.robot_id):
        lines.append(f"- {robot.robot_id}: papel {robot.role}, posição inicial {_fmt(robot.start)}.")
    if include_distances:
        lines += ["", "Distância em linha reta (m) de cada robô MUUT até a entrada de cada zona:"]
        for robot in scenario.movable_robots():
            cells = ", ".join(f"{z.name} {dist(robot.start, z.entry):.2f}" for z in scenario.zones.values())
            lines.append(f"- {robot.robot_id}: {cells}")
    return "\n".join(lines)


def response_schema(scenario: Scenario) -> dict:
    # enum fecha os nomes possíveis: um erro do modelo vira "zona errada" ou
    # "robô errado" mensurável, nunca um nome inventado.
    return {
        "type": "object",
        "properties": {
            "assignments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "robot_id": {"type": "string", "enum": sorted(scenario.robots)},
                        "zones": {"type": "array", "items": {"type": "string", "enum": sorted(scenario.zones)}},
                    },
                    "required": ["robot_id", "zones"],
                    "additionalProperties": False,
                },
            },
            "justification": {"type": "string"},
        },
        "required": ["assignments", "justification"],
        "additionalProperties": False,
    }


def _api_error_tags():
    """Classes de erro do SDK, da mais específica pra mais geral."""
    try:
        import anthropic
    except ImportError:
        return []
    return [
        ("rate_limit", anthropic.RateLimitError),
        ("api_status", anthropic.APIStatusError),
        ("api_connection", anthropic.APIConnectionError),
    ]


class LLMAllocator:
    deterministic = False

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        effort: str = "medium",
        include_distances: bool = False,
        use_fallback: bool = True,
        max_tokens: int = 16000,
        client=None,
    ) -> None:
        self.model = model
        self.effort = effort
        self.include_distances = include_distances
        self.use_fallback = use_fallback
        self.max_tokens = max_tokens
        self.name = "llm_dist" if include_distances else "llm"
        self._client = client

    def _get_client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic()
        return self._client

    def request_kwargs(self, scenario: Scenario, mission: Mission) -> dict:
        # Claude Opus 5.5 não aceita temperature/top_p: a variabilidade entre
        # chamadas não é controlável pelo cliente, só mensurável — é o que o
        # estudo de alocação mede.
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": build_user_prompt(scenario, mission, self.include_distances)}],
            "output_config": {
                "effort": self.effort,
                "format": {"type": "json_schema", "schema": response_schema(scenario)},
            },
        }

    def allocate(self, scenario: Scenario, mission: Mission) -> Allocation:
        kwargs = self.request_kwargs(scenario, mission)
        meta = {
            "model_requested": self.model,
            "effort": self.effort,
            "include_distances": self.include_distances,
            "fallback_enabled": self.use_fallback,
        }
        client = self._get_client()
        t0 = time.perf_counter()
        try:
            if self.use_fallback:
                response = client.beta.messages.create(**kwargs, betas=[FALLBACK_BETA], fallbacks="default")
            else:
                response = client.messages.create(**kwargs)
        except Exception as exc:
            tag = next((t for t, cls in _api_error_tags() if isinstance(exc, cls)), None)
            if tag is None:
                raise
            meta["latency_s"] = round(time.perf_counter() - t0, 3)
            return Allocation(self.name, mission.mission_id, {}, issues=[f"{tag}: {exc}"], meta=meta)

        meta["latency_s"] = round(time.perf_counter() - t0, 3)
        meta["response_id"] = getattr(response, "id", None)
        # Modelo que de fato respondeu: com fallback ligado pode não ser o pedido.
        # Execuções servidas por outro modelo devem ser separadas na análise.
        meta["model_served"] = getattr(response, "model", None)
        meta["stop_reason"] = response.stop_reason
        usage = getattr(response, "usage", None)
        meta["input_tokens"] = getattr(usage, "input_tokens", None)
        meta["output_tokens"] = getattr(usage, "output_tokens", None)
        meta["fallback_ran"] = any(
            getattr(it, "type", None) == "fallback_message" for it in (getattr(usage, "iterations", None) or [])
        )

        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None)
            return Allocation(self.name, mission.mission_id, {}, issues=[f"refusal: {category}"], meta=meta)
        if response.stop_reason == "max_tokens":
            return Allocation(self.name, mission.mission_id, {}, issues=["max_tokens: resposta truncada"], meta=meta)

        text = next((b.text for b in response.content if b.type == "text"), "")
        meta["raw_text"] = text
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return Allocation(self.name, mission.mission_id, {}, issues=[f"json_invalido: {exc}"], meta=meta)

        meta["justification"] = data.get("justification", "")
        plans: dict[str, list[str]] = {}
        for item in data.get("assignments", []):
            plans.setdefault(item["robot_id"], []).extend(item["zones"])
        alloc = build_allocation(self.name, scenario, mission, plans, meta)
        if len({item["robot_id"] for item in data.get("assignments", [])}) < len(data.get("assignments", [])):
            alloc.meta["robot_listed_twice"] = True
        return alloc


def make_allocator(name: str, **llm_kwargs):
    if name == "fixed":
        return FixedAllocator()
    if name == "greedy":
        return GreedyAllocator()
    if name == "optimal":
        return OptimalAllocator()
    if name == "llm":
        return LLMAllocator(include_distances=False, **llm_kwargs)
    if name == "llm_dist":
        return LLMAllocator(include_distances=True, **llm_kwargs)
    raise ValueError(f"alocador desconhecido: {name}")
