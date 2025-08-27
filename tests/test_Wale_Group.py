from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import co_loops


class TestWale_Group(TestCase):

    def test_single_loop_wale_in_groups(self):
        knit_graph, yarn = co_loops(4)
        wale_groups = knit_graph.get_wale_groups()
        for loop in knit_graph:
            if knit_graph.is_terminal_loop(loop):
                self.assertIn(loop, wale_groups, f"Expected terminal loop {loop} to be in wale_groups")
