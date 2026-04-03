"""Unit tests for Knit Graph SVG Visualizer.

This test suite ensures that SVG visualization functions produce valid output
for various knit graph patterns. Generated SVG files are written to a temporary
directory and cleaned up after each test.
"""

import tempfile
from pathlib import Path
from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import co_loops, jersey_swatch, jersey_tube, kp_rib_swatch, lace_mesh, seed_swatch, twist_cable
from knit_graphs.Knit_Graph_Visualizer import Knit_Graph_Visualizer, visualize_knit_graph


class Test_Knit_Graph_Visualizer(TestCase):
    """Test suite for knit graph SVG visualization.

    Set KEEP_SVG=1 to write SVG files to a persistent ``test_svg_output/``
    directory for visual inspection instead of a temporary directory::

        KEEP_SVG=1 python -m pytest tests/test_knit_graph_svg_visualizer.py
    """

    # Toggle: when True, SVGs are written to a persistent directory.
    keep_svg: bool = False
    persistent_dir: Path = Path(__file__).parent / "test_svg_output"

    def setUp(self):
        """Create output directory for SVG files."""
        if self.keep_svg:
            self.persistent_dir.mkdir(exist_ok=True)
            self.output_dir = self.persistent_dir
            self._tmp_dir = None
        else:
            self._tmp_dir = tempfile.TemporaryDirectory()
            self.output_dir = Path(self._tmp_dir.name)

    def tearDown(self):
        """Clean up temporary directory if used."""
        if self._tmp_dir is not None:
            self._tmp_dir.cleanup()

    def _output_path(self, name: str) -> Path:
        return self.output_dir / f"{name}.svg"

    def _assert_valid_svg(self, path: Path) -> str:
        """Assert the file exists, is non-empty, and contains SVG content."""
        self.assertTrue(path.exists(), f"SVG file was not created: {path}")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content), 0, "SVG file is empty")
        self.assertIn("<svg", content, "File does not contain SVG element")
        self.assertIn("</svg>", content, "SVG element is not closed")
        return content

    def test_cast_on_row_from_left(self):
        """Test visualization of cast-on row starting from left."""
        width = 10
        builder, knit_graph, yarn = co_loops(width)

        path = visualize_knit_graph(
            knit_graph,
            graph_title="Left Cast On",
            filepath=self._output_path("left_cast_on"),
        )

        content = self._assert_valid_svg(path)
        # Should have loop markers for each cast-on loop.
        self.assertEqual(content.count("<circle"), width)

    def test_cast_on_row_from_right(self):
        """Test visualization of cast-on row starting from right."""
        width = 11
        builder, knit_graph, yarn = co_loops(width)

        path = visualize_knit_graph(
            knit_graph,
            start_on_left=False,
            graph_title="Right Cast On",
            filepath=self._output_path("right_cast_on"),
        )

        content = self._assert_valid_svg(path)
        self.assertEqual(content.count("<circle"), width)

    def test_visualize_rib(self):
        """Test visualization of ribbing pattern."""
        width = 4
        height = 4
        knit_graph = kp_rib_swatch(width, height)

        path = visualize_knit_graph(
            knit_graph,
            start_on_left=True,
            graph_title="Rib",
            filepath=self._output_path("rib"),
        )

        self._assert_valid_svg(path)

    def test_visualize_jersey(self):
        """Test visualization of jersey (stockinette) pattern."""
        width = 4
        height = 4
        knit_graph = jersey_swatch(width, height)

        path = visualize_knit_graph(
            knit_graph,
            start_on_left=True,
            graph_title="Jersey",
            filepath=self._output_path("jersey"),
        )

        self._assert_valid_svg(path)

    def test_visualize_seed(self):
        """Test visualization of seed stitch pattern."""
        width = 4
        height = 4
        knit_graph = seed_swatch(width, height)

        path = visualize_knit_graph(
            knit_graph,
            start_on_left=True,
            graph_title="Seed Stitch",
            filepath=self._output_path("seed"),
        )

        self._assert_valid_svg(path)

    def test_visualize_tube(self):
        """Test visualization of tubular knitting."""
        width = 3
        height = 2
        knit_graph = jersey_tube(width, height)

        path = visualize_knit_graph(
            knit_graph,
            start_on_left=True,
            graph_title="Tube",
            filepath=self._output_path("tube"),
        )

        self._assert_valid_svg(path)

    def test_visualize_lace(self):
        """Test visualization of lace mesh pattern."""
        width = 7
        height = 6
        knit_graph = lace_mesh(width, height)

        path = visualize_knit_graph(
            knit_graph,
            start_on_left=True,
            balance_by_base_width=True,
            left_zero_align=True,
            graph_title="Alternating Lace",
            filepath=self._output_path("lace"),
        )

        self._assert_valid_svg(path)

    def test_visualize_cable(self):
        """Test visualization of cable knitting pattern."""
        width = 8
        height = 4
        knit_graph = twist_cable(width, height)

        path = visualize_knit_graph(
            knit_graph,
            graph_title="Cable",
            filepath=self._output_path("cable"),
        )

        content = self._assert_valid_svg(path)
        # Cable patterns should have stitch edges rendered as lines.
        self.assertIn("<line", content)

    def test_make_svg_returns_string(self):
        """Test that make_svg returns a valid SVG string without writing a file."""
        width = 4
        height = 2
        knit_graph = jersey_swatch(width, height)

        visualizer = Knit_Graph_Visualizer(knit_graph)
        svg_string = visualizer.make_svg(graph_title="String Test")

        self.assertIsInstance(svg_string, str)
        self.assertIn("<svg", svg_string)
        self.assertIn("</svg>", svg_string)

    def test_visualizer_equality(self):
        """Test that two visualizers of the same graph produce equal positions."""
        knit_graph = jersey_swatch(4, 4)

        viz_a = Knit_Graph_Visualizer(knit_graph)
        viz_b = Knit_Graph_Visualizer(knit_graph)

        self.assertEqual(viz_a, viz_b)
        self.assertEqual(len(viz_a.x_coordinate_differences(viz_b)), 0)
        self.assertEqual(len(viz_a.y_coordinate_differences(viz_b)), 0)

    def test_custom_svg_kwargs(self):
        """Test that custom SVG rendering parameters are accepted."""
        knit_graph = jersey_swatch(3, 2)

        path = visualize_knit_graph(
            knit_graph,
            graph_title="Custom Style",
            filepath=self._output_path("custom"),
            scale=120.0,
            loop_radius=0.2,
            knit_color="darkblue",
            purl_color="darkred",
            background_color="white",
        )

        content = self._assert_valid_svg(path)
        self.assertIn("darkblue", content)
        self.assertIn("white", content)
