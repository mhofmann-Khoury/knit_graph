from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import (
    co_loops,
    jersey_swatch,
    jersey_tube,
    kp_mesh_decrease_left_swatch,
    kp_mesh_decrease_right_swatch,
    kp_rib_swatch,
    seed_swatch,
    twist_cable,
)
from knit_graphs.Knit_Graph_Visualizer import visualize_knit_graph


class Test_Knitting_Visualizers(TestCase):

    def setUp(self):
        self.show_visualization = False  # Set this to true for local testing.

    def test_cast_on_row_from_left(self):
        width = 10
        knit_graph, yarn = co_loops(width)
        visualize_knit_graph(knit_graph, graph_title="Left Cast On", show_figure=self.show_visualization)

    def test_cast_on_row_from_right(self):
        width = 11
        knit_graph, yarn = co_loops(width)
        visualize_knit_graph(knit_graph, start_on_left=False, graph_title="Right Cast On", show_figure=self.show_visualization)

    def test_visualize_rib(self):
        width = 4
        height = 4
        knit_graph = kp_rib_swatch(width, height)
        visualize_knit_graph(knit_graph, start_on_left=True, graph_title="Rib", show_figure=self.show_visualization)

    def test_visualize_jersey(self):
        width = 4
        height = 4
        knit_graph = jersey_swatch(width, height)
        visualize_knit_graph(knit_graph, start_on_left=True, graph_title="Jersey", show_figure=self.show_visualization)

    def test_visualize_seed(self):
        width = 4
        height = 4
        knit_graph = seed_swatch(width, height)
        visualize_knit_graph(knit_graph, start_on_left=True, graph_title="Seed Stitch", show_figure=self.show_visualization)

    def test_visualize_tube(self):
        width = 3
        height = 2
        knit_graph = jersey_tube(width, height)
        visualize_knit_graph(knit_graph, start_on_left=True, graph_title="Tube", show_figure=self.show_visualization)

    def test_visualize_lace_left(self):
        width = 5
        height = 6
        knit_graph = kp_mesh_decrease_left_swatch(width, height)
        visualize_knit_graph(knit_graph, start_on_left=True, balance_by_base_width=True, left_zero_align=False, graph_title="Left leaning lace", show_figure=self.show_visualization)

    def test_visualize_lace_right(self):
        width = 5
        height = 6
        knit_graph = kp_mesh_decrease_right_swatch(width, height)
        visualize_knit_graph(knit_graph, start_on_left=True, balance_by_base_width=True, left_zero_align=False, graph_title="Right leaning lace", show_figure=self.show_visualization)

    def test_visualize_cable(self):
        width = 8
        height = 4
        knit_graph = twist_cable(width, height)
        # Check cable structure
        visualize_knit_graph(knit_graph, graph_title="Cable", show_figure=self.show_visualization)
