from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import (
    jersey_swatch,
    jersey_tube,
    kp_rib_swatch,
    lace_mesh,
    seed_swatch,
    twist_cable,
)
from knit_graphs.Pull_Direction import Pull_Direction


class TestKnit_Graph(TestCase):

    def test_knit_graph_get_and_in(self):
        knit_graph = jersey_swatch(4, 4)
        for i in range(0, knit_graph.last_loop.loop_id):
            self.assertTrue(i in knit_graph)
            loop = knit_graph[i]
            self.assertTrue(loop in knit_graph)

        for loop in knit_graph:
            self.assertTrue(loop in knit_graph)

        for p, c, d in knit_graph.stitch_iter:
            self.assertTrue((p, c) in knit_graph)
            self.assertIs(d["pull_direction"], Pull_Direction.BtF)

    def test_mesh(self):
        generators = [lace_mesh]
        width = 13
        height = 6
        for generator in generators:
            _knit_graph = generator(width, height)

    def test_twist_cable(self):
        generators = [twist_cable]
        width = 12
        height = 10
        for generator in generators:
            _knit_graph = generator(width, height)

    def test_tube_in_round(self):
        width = 4
        height = 4
        knit_graph = jersey_tube(width, height)
        courses = knit_graph.get_courses()
        assert len(courses) == height + 1, f"Expected tube courses to be {height + 1} but got {len(courses)}"
        for prior_course, next_course in zip(courses[:-1], courses[1:], strict=False):
            assert prior_course.in_round_with(next_course), f"{prior_course} not in round with {next_course}"

    def test_course_count(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        width = 10
        for generator in generators:
            height = 10
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"

            height = 11
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"

    def test_wale_count(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        height = 10
        for generator in generators:
            width = 10
            knit_graph = generator(width, height)
            wale_groups = knit_graph.get_wale_groups()
            assert len(wale_groups) == width, f"Expected wale_groups to be {width} but got {len(wale_groups)}"

            width = 11
            knit_graph = generator(width, height)
            wale_groups = knit_graph.get_wale_groups()
            assert len(wale_groups) == width, f"Expected wale_groups to be {width} but got {len(wale_groups)}"

        width = 10
        knit_graph = jersey_tube(width, height)
        wale_groups = knit_graph.get_wale_groups()
        assert len(wale_groups) == width * 2, f"Expected wale_groups to be {width * 2} but got {len(wale_groups)}"

    def test_delete_loop(self):
        knit_graph = jersey_swatch(4, 4)
        self.assertEqual(len(knit_graph.stitch_graph), 20)
        loop_0 = knit_graph[0]
        knit_graph.remove_loop(loop_0)
        self.assertEqual(len(knit_graph.stitch_graph), 19)
        self.assertEqual(len(loop_0.yarn), 19)
        self.assertNotIn(loop_0, loop_0.yarn)
        loop_5 = knit_graph[5]
        parent_5 = loop_5.parent_loops
        child_5 = knit_graph.get_child_loop(loop_5)
        self.assertIsNotNone(child_5)
        self.assertEqual(len(parent_5), 1)
        knit_graph.remove_loop(loop_5)
        for p in parent_5:
            self.assertFalse(knit_graph.has_child_loop(p))
        self.assertFalse(child_5.has_parent_loops())
        self.assertEqual(len(knit_graph.stitch_graph), 18)
        self.assertEqual(len(loop_5.yarn), 18)
        self.assertNotIn(loop_5, loop_5.yarn)

    def test_delete_loop_floats(self):
        knit_graph = jersey_tube(3, 4)
        self.assertEqual(len(knit_graph.stitch_graph), 30)
        loop_10 = knit_graph[10]
        yarn = loop_10.yarn
        loop_7 = knit_graph[7]
        loop_8 = knit_graph[8]
        loop_11 = knit_graph[11]
        loop_9 = knit_graph[9]
        self.assertTrue(yarn.has_float(loop_7, loop_8))
        behind_float = yarn.get_loops_behind_float(loop_7, loop_8)
        self.assertEqual(len(behind_float), 1)
        self.assertIn(loop_10, behind_float)
        knit_graph.remove_loop(loop_10)
        self.assertEqual(len(knit_graph.stitch_graph), 29)
        self.assertTrue(yarn.has_float(loop_9, loop_11))
        front_float = yarn.get_loops_in_front_of_float(loop_9, loop_11)
        self.assertEqual(len(front_float), 2)
        self.assertIn(loop_8, front_float)
        self.assertIn(loop_7, front_float)
