from unittest import TestCase

from knit_graphs.knit_graph_generators.basic_knit_graph_generators import co_loops, seed_swatch, jersey_tube, kp_mesh_decrease_left_swatch, twist_cable, kp_mesh_decrease_right_swatch
from knit_graphs.knit_graph_visualizer.Stitch_Visualizer import visualize_stitches


class Test_Knitting_Visualizers(TestCase):

    def test_cast_on_row_from_left(self):
        width = 10
        knit_graph, yarn = co_loops(width)
        visualize_stitches(knit_graph)

    def test_cast_on_row_from_right(self):
        width = 11
        knit_graph, yarn = co_loops(width)
        visualize_stitches(knit_graph, start_on_left=False)

    def test_visualize_seed(self):
        width = 4
        height = 4
        knit_graph = seed_swatch(width, height)
        visualize_stitches(knit_graph)

    def test_visualize_tube(self):
        width = 3
        height = 2
        knit_graph = jersey_tube(width, height)
        visualize_stitches(knit_graph)

    def test_visualize_lace_left(self):
        width = 5
        height = 6
        knit_graph = kp_mesh_decrease_left_swatch(width, height)
        visualize_stitches(knit_graph, re_balance_to_course_width=True, left_zero_align=False)

    def test_visualize_lace_right(self):
        width = 5
        height = 6
        knit_graph = kp_mesh_decrease_right_swatch(width, height)
        visualize_stitches(knit_graph, re_balance_to_course_width=True, left_zero_align=False)

    def test_visualize_cable(self):
        width = 8
        height = 4
        knit_graph = twist_cable(width, height)
        # Check cable structure
        visualize_stitches(knit_graph)
