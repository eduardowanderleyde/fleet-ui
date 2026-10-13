import itertools
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from mission import load_scenario, make_allocator  # noqa: E402
from mission.allocators import LLMAllocator, build_user_prompt, response_schema  # noqa: E402
from mission.model import Mission, plan_costs  # noqa: E402

SCENARIO = ROOT / "backend" / "mission" / "scenarios" / "warehouse.yaml"


class FakeMessages:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def fake_client(payload=None, stop_reason="end_turn", text=None):
    body = text if text is not None else json.dumps(payload)
    response = SimpleNamespace(
        id="msg_test", model="claude-opus-5-5", stop_reason=stop_reason, stop_details=None,
        content=[SimpleNamespace(type="text", text=body)],
        usage=SimpleNamespace(input_tokens=100, output_tokens=20, iterations=None),
    )
    messages = FakeMessages(response)
    return SimpleNamespace(messages=messages, beta=SimpleNamespace(messages=messages)), messages


class ScenarioTests(unittest.TestCase):
    def test_warehouse_scenario_loads_and_missions_reference_known_zones(self):
        scenario = load_scenario(SCENARIO)
        self.assertEqual([r.robot_id for r in scenario.movable_robots()], ["tb1", "tb2"])
        self.assertFalse(scenario.robots["tb3"].movable)
        for mission in scenario.missions.values():
            self.assertTrue(set(mission.zones) <= set(scenario.zones))


class DeterministicAllocatorTests(unittest.TestCase):
    def setUp(self):
        self.scenario = load_scenario(SCENARIO)

    def test_fixed_is_round_robin_over_movable_robots(self):
        mission = self.scenario.missions["m2_tres_corredores"]
        alloc = make_allocator("fixed").allocate(self.scenario, mission)
        self.assertEqual(alloc.plans, {"tb1": ["corredor_A", "corredor_C"], "tb2": ["corredor_B"]})
        self.assertTrue(alloc.valid)

    def test_no_deterministic_allocator_assigns_the_fuut_robot(self):
        for name in ("fixed", "greedy", "optimal"):
            for mission in self.scenario.missions.values():
                alloc = make_allocator(name).allocate(self.scenario, mission)
                self.assertNotIn("tb3", alloc.plans, f"{name}/{mission.mission_id}")
                self.assertTrue(alloc.valid, f"{name}/{mission.mission_id}: {alloc.issues}")

    def test_optimal_matches_brute_force_and_beats_or_ties_heuristics(self):
        movable = [r.robot_id for r in self.scenario.movable_robots()]
        for mission in self.scenario.missions.values():
            zones = list(mission.zones)
            brute = min(
                plan_costs(self.scenario, {
                    rid: [z for z, a in zip(order, assign) if a == rid] for rid in movable
                })[0]
                for order in itertools.permutations(zones)
                for assign in itertools.product(movable, repeat=len(zones))
            )
            best = make_allocator("optimal").allocate(self.scenario, mission)
            self.assertAlmostEqual(best.makespan, brute, places=9, msg=mission.mission_id)
            for name in ("fixed", "greedy"):
                other = make_allocator(name).allocate(self.scenario, mission)
                self.assertGreaterEqual(other.makespan, best.makespan - 1e-9)

    def test_deterministic_allocators_repeat_exactly(self):
        mission = self.scenario.missions["m5_armazem_completo"]
        for name in ("fixed", "greedy", "optimal"):
            sigs = {make_allocator(name).allocate(self.scenario, mission).signature() for _ in range(3)}
            self.assertEqual(len(sigs), 1, name)


class LLMAllocatorTests(unittest.TestCase):
    def setUp(self):
        self.scenario = load_scenario(SCENARIO)
        self.mission = self.scenario.missions["m1_dois_corredores"]

    def test_valid_response_is_parsed_and_costed(self):
        client, messages = fake_client({
            "assignments": [{"robot_id": "tb1", "zones": ["corredor_A"]}, {"robot_id": "tb2", "zones": ["corredor_C"]}],
            "justification": "cada robô no corredor mais próximo",
        })
        alloc = LLMAllocator(client=client).allocate(self.scenario, self.mission)
        self.assertTrue(alloc.valid, alloc.issues)
        self.assertEqual(alloc.plans, {"tb1": ["corredor_A"], "tb2": ["corredor_C"]})
        self.assertEqual(alloc.meta["model_served"], "claude-opus-5-5")
        self.assertEqual(alloc.meta["input_tokens"], 100)
        call = messages.calls[0]
        self.assertEqual(call["model"], "claude-opus-5-5")
        self.assertEqual(call["fallbacks"], "default")
        self.assertNotIn("temperature", call)
        self.assertEqual(call["output_config"]["format"]["type"], "json_schema")

    def test_role_violation_and_missing_zone_are_reported(self):
        client, _ = fake_client({
            "assignments": [{"robot_id": "tb3", "zones": ["corredor_A"]}], "justification": "tb3 está mais perto",
        })
        alloc = LLMAllocator(client=client).allocate(self.scenario, self.mission)
        self.assertFalse(alloc.valid)
        kinds = {i.split(":")[0] for i in alloc.issues}
        self.assertEqual(kinds, {"papel_violado", "zona_faltando"})

    def test_extra_zone_and_invalid_json_are_reported(self):
        client, _ = fake_client({
            "assignments": [{"robot_id": "tb1", "zones": ["corredor_A", "doca"]},
                            {"robot_id": "tb2", "zones": ["corredor_C"]}],
            "justification": "",
        })
        alloc = LLMAllocator(client=client).allocate(self.scenario, self.mission)
        self.assertEqual(alloc.issues, ["zona_extra: doca"])

        client, _ = fake_client(text="não é json")
        alloc = LLMAllocator(client=client).allocate(self.scenario, self.mission)
        self.assertTrue(alloc.issues[0].startswith("json_invalido"))

    def test_refusal_is_recorded_not_raised(self):
        client, _ = fake_client({}, stop_reason="refusal")
        alloc = LLMAllocator(client=client).allocate(self.scenario, self.mission)
        self.assertTrue(alloc.issues[0].startswith("refusal"))

    def test_no_fallback_uses_plain_messages_endpoint(self):
        client, messages = fake_client({"assignments": [], "justification": ""})
        LLMAllocator(client=client, use_fallback=False).allocate(self.scenario, self.mission)
        self.assertNotIn("fallbacks", messages.calls[0])
        self.assertNotIn("betas", messages.calls[0])

    def test_prompt_and_schema_expose_roles_and_close_the_name_sets(self):
        prompt = build_user_prompt(self.scenario, self.mission, include_distances=True)
        self.assertIn(self.mission.text, prompt)
        self.assertIn("tb3: papel FUUT", prompt)
        self.assertIn("Distância em linha reta", prompt)
        self.assertNotIn("Distância", build_user_prompt(self.scenario, self.mission, include_distances=False))
        item = response_schema(self.scenario)["properties"]["assignments"]["items"]["properties"]
        self.assertEqual(item["robot_id"]["enum"], ["tb1", "tb2", "tb3"])
        self.assertIn("prateleira_sul", item["zones"]["items"]["enum"])


class StudySummaryTests(unittest.TestCase):
    def test_summary_measures_stability_and_gap(self):
        sys.path.insert(0, str(ROOT / "fleet_ws" / "scripts"))
        from mission_allocation_study import summarize

        def row(sig, makespan, issues=()):
            return {"valid": not issues, "signature": sig, "partition": sig, "makespan": makespan,
                    "issues": list(issues), "meta": {}}

        a, b = '{"tb1": ["x"]}', '{"tb2": ["x"]}'
        runs = [row(a, 10.0), row(a, 10.0), row(b, 12.0), row("{}", None, ["zona_faltando: x"])]
        s = summarize(runs, optimal_makespan=10.0)
        self.assertEqual(s["n_valid"], 3)
        self.assertEqual(s["distinct_allocations"], 2)
        self.assertAlmostEqual(s["modal_share"], 0.5)
        self.assertAlmostEqual(s["gap_pct_max"], 20.0)
        self.assertAlmostEqual(s["optimal_hit_rate"], 0.5)
        self.assertEqual(s["modal_allocation"], {"tb1": ["x"]})
        self.assertEqual(s["issues"], {"zona_faltando": 1})


if __name__ == "__main__":
    unittest.main()
