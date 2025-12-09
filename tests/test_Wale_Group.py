from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import co_loops, jersey_tube, lace_mesh


class TestWale_Group(TestCase):
    def test_single_loop_wale_in_groups(self):
        knit_graph, yarn = co_loops(4)
        wale_groups = knit_graph.get_wale_groups()
        terminal_groups = {w.terminal_loop for w in wale_groups}
        for loop in knit_graph.terminal_loops():
            self.assertIn(
                loop,
                terminal_groups,
                f"Expected terminal loop {loop} to be in wale_groups",
            )

    def test_tube_in_round(self):
        width = 4
        height = 4
        knit_graph = jersey_tube(width, height)
        wale_groups = knit_graph.get_wale_groups()
        self.assertEqual(len(wale_groups), width * 2)
        for wg in wale_groups:
            self.assertEqual(len(wg), height + 1)

    def test_mesh(self):
        width = 7
        height = 3
        knit_graph = lace_mesh(width, height)
        wale_groups = knit_graph.get_wale_groups()
        self.assertEqual(len(wale_groups), 7)
        for wg in wale_groups:
            if len(wg.wale_graph.nodes) == 1:
                if len(wg) != 2:
                    self.assertEqual(len(wg), 6, "Expected single wale of 2 or 6")
            else:
                self.assertEqual(len(wg.wale_graph.nodes), 5)
                self.assertEqual(len(wg.wale_graph.edges), 4)
