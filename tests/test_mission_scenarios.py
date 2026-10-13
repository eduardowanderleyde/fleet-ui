import itertools
import math
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

try:
    import numpy  # noqa: F401
    from PIL import Image

    HAS_MAP_DEPS = True
except ImportError:
    HAS_MAP_DEPS = False

HARD = ROOT / "backend" / "mission" / "scenarios" / "warehouse_dificil.yaml"


@unittest.skipUnless(HAS_MAP_DEPS, "numpy/pillow ausentes")
class GridMapTests(unittest.TestCase):
    def setUp(self):
        from mission.gridmap import GridMap

        # 10 m x 10 m, célula de 0,1 m: parede em x=5 de y=0 a y=8 (passagem só no topo)
        img = Image.new("L", (100, 100), 244)
        for row in range(20, 100):  # linha 0 = topo (y=10); linhas 20..99 = y de 8 a 0
            for col in range(49, 51):
                img.putpixel((col, row), 54)
        self.tmp = tempfile.TemporaryDirectory()
        path = Path(self.tmp.name) / "map.png"
        img.save(path)
        self.grid = GridMap(path, resolution=0.1, origin=(0.0, 0.0), inflate_m=0.2, cell_m=0.1)

    def tearDown(self):
        self.tmp.cleanup()

    def test_path_goes_around_the_wall(self):
        a, b = (2.0, 1.0), (8.0, 1.0)
        straight = math.dist(a, b)
        around = self.grid.distance(a, b)
        self.assertGreater(around, straight + 10.0)  # sobe até y≈8.3 e desce de novo
        self.assertAlmostEqual(self.grid.distance(b, a), around, places=6)

    def test_points_in_wall_or_inflation_are_not_free(self):
        self.assertFalse(self.grid.is_free((5.0, 4.0)))
        self.assertFalse(self.grid.is_free((5.25, 4.0)))  # dentro da inflação
        self.assertTrue(self.grid.is_free((6.0, 4.0)))
        self.assertTrue(math.isinf(self.grid.distance((2.0, 1.0), (5.0, 4.0))))


@unittest.skipUnless(HAS_MAP_DEPS, "numpy/pillow ausentes")
class HardScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mission import load_scenario

        cls.scenario = load_scenario(HARD)

    def test_scenario_uses_grid_metric_and_has_all_categories(self):
        self.assertEqual(self.scenario.metric_name, "grid")
        categories = {m.category for m in self.scenario.missions.values()}
        self.assertEqual(categories, {"escala", "obstaculo", "linguagem", "falha", "papel"})

    def test_dynamic_programming_matches_brute_force(self):
        from mission import make_allocator
        from mission.model import plan_costs

        for mid in ("o3_corredores_sul", "l1_norte_vago", "f1_tb2_falhou", "p1_fuut_ao_lado"):
            mission = self.scenario.missions[mid]
            sc = self.scenario.for_mission(mission)
            movable = [r.robot_id for r in sc.movable_robots()]
            zones = list(mission.zones)
            brute = min(
                plan_costs(sc, {rid: [z for z, a in zip(order, assign) if a == rid] for rid in movable})[0]
                for order in itertools.permutations(zones)
                for assign in itertools.product(movable, repeat=len(zones))
            )
            best = make_allocator("optimal").allocate(self.scenario, mission)
            self.assertAlmostEqual(best.makespan, brute, places=6, msg=mid)

    def test_failed_robot_is_unavailable_and_survivor_starts_where_it_stopped(self):
        from mission.allocators import build_allocation

        mission = self.scenario.missions["f1_tb2_falhou"]
        sc = self.scenario.for_mission(mission)
        self.assertFalse(sc.robots["tb2"].available)
        self.assertEqual(sc.robots["tb1"].start, (2.0, -20.0))
        self.assertTrue(self.scenario.robots["tb2"].available)  # cenário base intocado

        bad = build_allocation("t", sc, mission, {"tb2": ["corredor_sul_oeste"], "tb1": ["corredor_sul_leste"]})
        self.assertEqual([i.split(":")[0] for i in bad.issues], ["robo_indisponivel"])

    def test_straight_line_trap_on_single_zone_missions(self):
        import dataclasses

        from mission import make_allocator
        from mission.model import dist

        straight = dataclasses.replace(self.scenario, metric=dist, metric_name="euclidean")
        for mid, right, wrong in (("o1_doca", "tb1", "tb2"), ("o2_sala", "tb2", "tb3")):
            mission = self.scenario.missions[mid]
            self.assertEqual(list(make_allocator("optimal").allocate(self.scenario, mission).plans), [right], mid)
            self.assertEqual(list(make_allocator("optimal").allocate(straight, mission).plans), [wrong], mid)

    def test_prompt_reports_failure_map_notes_and_path_table(self):
        from mission.allocators import build_user_prompt

        mission = self.scenario.missions["f1_tb2_falhou"]
        prompt = build_user_prompt(self.scenario.for_mission(mission), mission, include_distances=True)
        self.assertIn("tb2: papel MUUT, INDISPONÍVEL", prompt)
        self.assertIn("tb1: papel MUUT, posição atual (2.0, -20.0)", prompt)
        self.assertIn("Sobre o mapa:", prompt)
        self.assertIn("caminho livre no mapa", prompt)
        self.assertNotIn("Distância em linha reta", prompt)


if __name__ == "__main__":
    unittest.main()
