"""Unit tests for Knit Graph Visualizer with safe socket handling.

This test suite ensures that visualization functions work correctly without
creating socket connection issues that can cause browser hangs.
"""

import os
from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import (
    co_loops,
    jersey_swatch,
    jersey_tube,
    kp_rib_swatch,
    lace_mesh,
    seed_swatch,
    twist_cable,
)
from knit_graphs.Knit_Graph_Visualizer import visualize_knit_graph_safe


class Test_Knitting_Visualizers_Safe(TestCase):
    """Test suite for knit graph visualization with safe socket handling."""

    def setUp(self):
        """Set up test environment."""
        # Set environment variable to indicate we're testing
        os.environ["TESTING"] = "1"

        # Control visualization display - set to True only for local debugging
        self.show_visualization = False  # Set this to True for local testing if you want to see figures

        # If you want to see visualizations during local testing, uncomment the next line:
        # self.show_visualization = True

    def tearDown(self):
        """Clean up after tests."""
        # Clean up environment variable
        if "TESTING" in os.environ:
            del os.environ["TESTING"]

    def test_cast_on_row_from_left(self):
        """Test visualization of cast-on row starting from left."""
        width = 10
        knit_graph, yarn = co_loops(width)

        # Use safe version for testing - no socket issues
        fig = visualize_knit_graph_safe(knit_graph, graph_title="Left Cast On")

        # Optional: Show figure if enabled for local debugging
        if self.show_visualization:
            fig.show()

    def test_cast_on_row_from_right(self):
        """Test visualization of cast-on row starting from right."""
        width = 11
        knit_graph, yarn = co_loops(width)

        fig = visualize_knit_graph_safe(knit_graph, start_on_left=False, graph_title="Right Cast On")

        if self.show_visualization:
            fig.show()

    def test_visualize_rib(self):
        """Test visualization of ribbing pattern."""
        width = 4
        height = 4
        knit_graph = kp_rib_swatch(width, height)

        fig = visualize_knit_graph_safe(knit_graph, start_on_left=True, graph_title="Rib")

        if self.show_visualization:
            fig.show()

    def test_visualize_jersey(self):
        """Test visualization of jersey (stockinette) pattern."""
        width = 4
        height = 4
        knit_graph = jersey_swatch(width, height)

        fig = visualize_knit_graph_safe(knit_graph, start_on_left=True, graph_title="Jersey")

        if self.show_visualization:
            fig.show()

    def test_visualize_seed(self):
        """Test visualization of seed stitch pattern."""
        width = 4
        height = 4
        knit_graph = seed_swatch(width, height)

        fig = visualize_knit_graph_safe(knit_graph, start_on_left=True, graph_title="Seed Stitch")

        if self.show_visualization:
            fig.show()

    def test_visualize_tube(self):
        """Test visualization of tubular knitting."""
        width = 3
        height = 2
        knit_graph = jersey_tube(width, height)

        fig = visualize_knit_graph_safe(knit_graph, start_on_left=True, graph_title="Tube")

        if self.show_visualization:
            fig.show()

    def test_visualize_lace(self):
        width = 7
        height = 6
        knit_graph = lace_mesh(width, height)

        fig = visualize_knit_graph_safe(
            knit_graph,
            start_on_left=True,
            balance_by_base_width=True,
            left_zero_align=True,
            graph_title="Alternating Lace",
        )

        if self.show_visualization:
            fig.show()

    def test_visualize_cable(self):
        """Test visualization of cable knitting pattern."""
        width = 8
        height = 4
        knit_graph = twist_cable(width, height)

        fig = visualize_knit_graph_safe(knit_graph, graph_title="Cable")

        if self.show_visualization:
            fig.show()
