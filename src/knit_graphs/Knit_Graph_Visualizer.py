"""Module used to visualize a Knit graph as an SVG file.

This module provides comprehensive visualization capabilities for knit graphs by
rendering them as SVG. It handles the positioning of loops, rendering of yarn paths,
stitch edges, and cable crossings to create 2D visualizations of knitted structures.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Any, Generic, TypedDict, TypeVar, cast

from networkx import DiGraph

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Course import Course
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction

LoopT = TypeVar("LoopT", bound=Loop)


class TraceData(TypedDict, Generic[LoopT]):
    """Typing specification for stitch edge data."""

    x: list[float | None]
    y: list[float | None]
    edge: list[tuple[LoopT, LoopT]]
    is_start: list[bool]


class Knit_Graph_Visualizer(Generic[LoopT]):
    """A class used to visualize a knit graph by rendering it as an SVG file.

    This class converts knit graph data structures into SVG visualizations by calculating
    loop positions, rendering yarn paths as Bézier curves, and displaying stitch
    relationships with appropriate styling for different stitch types and cable crossings.

    Attributes:
        knit_graph (Knit_Graph): The knit graph to visualize.
        courses (list[Course]): List of courses (horizontal rows) in the knit graph.
        base_width (float): The width of the base course used for scaling.
        base_left (float): The leftmost position of the base course.
        loops_to_course (dict[Loop, Course]): Mapping from loops to their containing courses.
        data_graph (DiGraph): Internal graph for storing loop positions and visualization data.
        left_zero_align (bool): Whether to align the left edge of courses to zero.
        balance_by_base_width (bool): Whether to scale course widths to match the base course.
        start_on_left (bool): Whether to start knitting visualization from the left side.
        top_course_index (int): The index of the topmost course to visualize.
        first_course_index (int): The index of the first (bottom) course to visualize.
    """

    def __init__(
        self,
        knit_graph: Knit_Graph[LoopT],
        first_course_index: int = 0,
        top_course_index: int | None = None,
        start_on_left: bool = True,
        balance_by_base_width: bool = False,
        left_zero_align: bool = True,
    ):
        """Initialize the knit graph SVG visualizer with specified configuration options.

        Args:
            knit_graph: The knit graph to be visualized.
            first_course_index: The index of the first course to include. Defaults to 0.
            top_course_index: The index of the last course to include. If None, includes all.
            start_on_left: Whether to position the first loop on the left side. Defaults to True.
            balance_by_base_width: Whether to scale all course widths to match the base. Defaults to False.
            left_zero_align: Whether to align the leftmost loop of each course to x=0. Defaults to True.
        """
        self.left_zero_align: bool = left_zero_align
        self.balance_by_base_width: bool = balance_by_base_width
        self.start_on_left: bool = start_on_left
        self.knit_graph: Knit_Graph = knit_graph
        self.courses: list[Course[LoopT]] = knit_graph.get_courses()
        if top_course_index is None:
            top_course_index = len(self.courses)
        self.top_course_index: int = top_course_index
        self.first_course_index: int = first_course_index
        self.base_width: float = float(len(self.courses[first_course_index]))
        self.base_left: float = 0.0
        self.loops_to_course: dict[LoopT, Course] = {}
        for course in self.courses:
            self.loops_to_course.update({loop: course for loop in course})
        self.data_graph: DiGraph = DiGraph()
        self._loops_need_placement: set[LoopT] = set()

        # Stitch trace data categorized by pull direction and cable crossing.
        self._top_knit_trace_data: TraceData = {"x": [], "y": [], "edge": [], "is_start": []}
        self._bot_knit_trace_data: TraceData = {"x": [], "y": [], "edge": [], "is_start": []}
        self._top_purl_trace_data: TraceData = {"x": [], "y": [], "edge": [], "is_start": []}
        self._bot_purl_trace_data: TraceData = {"x": [], "y": [], "edge": [], "is_start": []}
        self._knit_trace_data: TraceData = {"x": [], "y": [], "edge": [], "is_start": []}
        self._purl_trace_data: TraceData = {"x": [], "y": [], "edge": [], "is_start": []}

        # Calculate all positions.
        self._position_loops()
        self._add_stitch_edges()

    # ── SVG rendering ────────────────────────────────────────────────────

    def make_svg(
        self,
        graph_title: str = "Knit Graph",
        scale: float = 80.0,
        loop_radius: float = 0.15,
        padding: float = 0.6,
        knit_color: str = "blue",
        purl_color: str = "red",
        font_size: float = 0.14,
        loop_border_width: float = 0.02,
        yarn_line_width: float = 0.02,
        background_color: str | None = None,
    ) -> str:
        """Generate an SVG string visualizing this knit graph.

        Args:
            graph_title: Title text rendered at the top of the SVG.
            scale: Pixels per graph-coordinate unit. Controls overall image size.
            loop_radius: Radius of loop circles in graph-coordinate units.
            padding: Extra space around the content in graph-coordinate units.
            knit_color: Stroke color for knit-stitch edges.
            purl_color: Stroke color for purl-stitch edges.
            font_size: Font size for loop id labels in graph-coordinate units.
            loop_border_width: Stroke width of loop circle borders in graph-coordinate units.
            yarn_line_width: Stroke width of yarn traces in graph-coordinate units.
            background_color: Optional background rectangle color. None for transparent.

        Returns:
            The SVG document as a string.
        """
        if len(self.data_graph.nodes) == 0:
            return self._empty_svg(graph_title, scale)

        # Determine bounding box in graph coordinates.
        all_x = [self._get_x_of_loop(n) for n in self.data_graph.nodes]
        all_y = [self._get_y_of_loop(n) for n in self.data_graph.nodes]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        # We flip y so that course 0 is at the bottom visually.
        # In SVG, y increases downward, but we want higher courses higher on screen.
        # Transform: svg_x = (x - min_x + padding) * scale
        #            svg_y = (max_y - y + padding) * scale  (flipped)
        title_height = 1.0  # graph-coordinate units reserved for the title
        content_w = max_x - min_x + 2 * padding
        content_h = max_y - min_y + 2 * padding + title_height
        svg_w = content_w * scale
        svg_h = content_h * scale

        def tx(x: float) -> float:
            return (x - min_x + padding) * scale

        def ty(y: float) -> float:
            return (max_y - y + padding + title_height) * scale

        root = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(round(svg_w, 2)),
            height=str(round(svg_h, 2)),
            viewBox=f"0 0 {round(svg_w, 2)} {round(svg_h, 2)}",
        )

        # Optional background.
        if background_color is not None:
            ET.SubElement(
                root,
                "rect",
                x="0",
                y="0",
                width=str(round(svg_w, 2)),
                height=str(round(svg_h, 2)),
                fill=background_color,
            )

        # Title.
        title_el = ET.SubElement(
            root,
            "text",
            x=str(round(svg_w / 2, 2)),
            y=str(round(title_height * scale * 0.6, 2)),
        )
        title_el.set("text-anchor", "middle")
        title_el.set("font-family", "sans-serif")
        title_el.set("font-size", str(round(0.3 * scale, 2)))
        title_el.set("fill", "black")
        title_el.text = graph_title

        # ── Layer 1: Yarn traces (behind everything) ────────────────────
        yarn_group = ET.SubElement(root, "g", id="yarn-traces")
        for yarn in self.knit_graph.yarns:
            points: list[tuple[float, float]] = []
            for loop in yarn:
                if self._loop_has_position(loop):
                    points.append((tx(self._get_x_of_loop(loop)), ty(self._get_y_of_loop(loop))))
            if len(points) < 2:
                continue
            path_d = self._bezier_path(points)
            ET.SubElement(
                yarn_group,
                "path",
                d=path_d,
                fill="none",
                stroke=yarn.properties.color,
            ).set("stroke-width", str(round(yarn_line_width * scale, 2)))

        # ── Layer 2: Stitch edges ────────────────────────────────────────
        stitch_group = ET.SubElement(root, "g", id="stitch-edges")
        stitch_configs: list[tuple[TraceData, str, float, float]] = [
            # (trace_data, color, width_multiplier, opacity)
            # Bottom-of-cable (drawn first so top-of-cable overlaps)
            (self._bot_knit_trace_data, knit_color, 0.04, 0.5),
            (self._bot_purl_trace_data, purl_color, 0.04, 0.5),
            # No-cross
            (self._knit_trace_data, knit_color, 0.05, 0.8),
            (self._purl_trace_data, purl_color, 0.05, 0.8),
            # Top-of-cable (drawn last, on top)
            (self._top_knit_trace_data, knit_color, 0.06, 1.0),
            (self._top_purl_trace_data, purl_color, 0.06, 1.0),
        ]
        for trace_data, color, width_mult, opacity in stitch_configs:
            self._render_stitch_trace_to_svg(
                stitch_group,
                trace_data,
                color,
                width_mult * scale,
                opacity,
                tx,
                ty,
            )

        # ── Layer 3: Loop markers (on top) ───────────────────────────────
        loop_group = ET.SubElement(root, "g", id="loop-markers")
        r_px = loop_radius * scale
        border_px = loop_border_width * scale
        fs_px = font_size * scale
        for yarn in self.knit_graph.yarns:
            for loop in yarn:
                if not self._loop_has_position(loop):
                    continue
                cx = round(tx(self._get_x_of_loop(loop)), 2)
                cy = round(ty(self._get_y_of_loop(loop)), 2)
                ET.SubElement(
                    loop_group,
                    "circle",
                    cx=str(cx),
                    cy=str(cy),
                    r=str(round(r_px, 2)),
                    fill=yarn.properties.color,
                    stroke="black",
                ).set("stroke-width", str(round(border_px, 2)))
                label = ET.SubElement(
                    loop_group,
                    "text",
                    x=str(cx),
                    y=str(round(cy + fs_px * 0.35, 2)),
                )
                label.set("text-anchor", "middle")
                label.set("font-family", "sans-serif")
                label.set("font-size", str(round(fs_px, 2)))
                label.set("fill", "white")
                label.text = str(loop.loop_id)

        ET.indent(root, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")

    def save_svg(
        self,
        filepath: str | Path = "knit_graph.svg",
        **kwargs: Any,
    ) -> Path:
        """Generate and save the SVG visualization to a file.

        Args:
            filepath: The path to write the SVG file. Defaults to "knit_graph.svg".
            **kwargs: Additional keyword arguments forwarded to :meth:`make_svg`.

        Returns:
            The resolved Path where the file was written.
        """
        path = Path(filepath)
        svg_content = self.make_svg(**kwargs)
        path.write_text(svg_content, encoding="utf-8")
        return path.resolve()

    # ── SVG helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _empty_svg(title: str, scale: float) -> str:
        """Return a minimal SVG when there are no loops to render."""
        w = 4 * scale
        h = 2 * scale
        root = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(round(w, 2)),
            height=str(round(h, 2)),
            viewBox=f"0 0 {round(w, 2)} {round(h, 2)}",
        )
        t = ET.SubElement(root, "text", x=str(round(w / 2, 2)), y=str(round(h / 2, 2)))
        t.set("text-anchor", "middle")
        t.set("font-family", "sans-serif")
        t.set("font-size", str(round(0.3 * scale, 2)))
        t.text = f"{title} (empty)"
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")

    @staticmethod
    def _bezier_path(points: list[tuple[float, float]]) -> str:
        """Build an SVG cubic Bézier path string through a sequence of points.

        Uses Catmull-Rom-to-Bézier conversion so the curve passes through every
        point while staying smooth.

        Args:
            points: Ordered list of (x, y) coordinates.

        Returns:
            An SVG path ``d`` attribute string.
        """
        if len(points) == 0:
            return ""
        if len(points) == 1:
            return f"M {round(points[0][0], 2)} {round(points[0][1], 2)}"
        if len(points) == 2:
            return f"M {round(points[0][0], 2)} {round(points[0][1], 2)} " f"L {round(points[1][0], 2)} {round(points[1][1], 2)}"

        # Catmull-Rom → cubic Bézier, tension factor 1/6.
        d_parts: list[str] = [f"M {round(points[0][0], 2)} {round(points[0][1], 2)}"]
        n = len(points)
        for i in range(n - 1):
            p0 = points[max(i - 1, 0)]
            p1 = points[i]
            p2 = points[min(i + 1, n - 1)]
            p3 = points[min(i + 2, n - 1)]

            # Control point 1: p1 + (p2 - p0) / 6
            cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
            cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
            # Control point 2: p2 - (p3 - p1) / 6
            cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
            cp2y = p2[1] - (p3[1] - p1[1]) / 6.0

            d_parts.append(f"C {round(cp1x, 2)} {round(cp1y, 2)}, " f"{round(cp2x, 2)} {round(cp2y, 2)}, " f"{round(p2[0], 2)} {round(p2[1], 2)}")
        return " ".join(d_parts)

    @staticmethod
    def _render_stitch_trace_to_svg(
        parent: ET.Element,
        trace_data: TraceData,
        color: str,
        stroke_width: float,
        opacity: float,
        tx: Callable[[float], float],
        ty: Callable[[float], float],
    ) -> None:
        """Render a set of stitch edges as SVG line elements.

        The trace data stores edges as triplets: start-point, end-point, None-separator.
        We iterate in groups of three to draw each edge.

        Args:
            parent: The SVG group element to append lines to.
            trace_data: The stitch trace data containing coordinates.
            color: Stroke color.
            stroke_width: Stroke width in pixels.
            opacity: Line opacity.
            tx: Transform function for x coordinates.
            ty: Transform function for y coordinates.
        """
        xs = trace_data["x"]
        ys = trace_data["y"]
        i = 0
        while i + 1 < len(xs):
            x1, y1 = xs[i], ys[i]
            x2, y2 = xs[i + 1], ys[i + 1]
            if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
                line = ET.SubElement(
                    parent,
                    "line",
                    x1=str(round(tx(x1), 2)),
                    y1=str(round(ty(y1), 2)),
                    x2=str(round(tx(x2), 2)),
                    y2=str(round(ty(y2), 2)),
                    stroke=color,
                )
                line.set("stroke-width", str(round(stroke_width, 2)))
                line.set("opacity", str(opacity))
            # Skip past the None separator (every 3rd entry).
            i += 3

    # ── Position calculation (unchanged from Plotly version) ─────────────

    def _position_loops(self) -> None:
        """Calculate and set the x,y coordinate positions of all loops to be visualized."""
        self._position_base_course()
        self._place_loops_in_courses()
        self._shift_knit_purl()
        self._shift_loops_by_float_alignment()

    def _shift_knit_purl(self, shift: float = 0.1) -> None:
        """Adjust the horizontal position of loops to visually distinguish knit from purl stitches."""
        has_knits = any(pd is Pull_Direction.BtF for _u, _v, pd in self.knit_graph.edge_iter)
        has_purls = any(pd is Pull_Direction.FtB for _u, _v, pd in self.knit_graph.edge_iter)
        if not (has_knits and has_purls):
            return
        yarn_over_align = set()
        for loop in self.data_graph.nodes:
            if not loop.has_parent_loops:
                if self.knit_graph.has_child_loop(loop):
                    yarn_over_align.add(loop)
                continue
            knit_parents = len([u for u in loop.parent_loops if self.knit_graph.get_pull_direction(u, loop) is Pull_Direction.BtF])
            purl_parents = len([u for u in loop.parent_loops if self.knit_graph.get_pull_direction(u, loop) is Pull_Direction.FtB])
            if knit_parents > purl_parents:
                self._set_x_of_loop(loop, self._get_x_of_loop(loop) - shift)
            elif purl_parents > knit_parents:
                self._set_x_of_loop(loop, self._get_x_of_loop(loop) + shift)

        for loop in yarn_over_align:
            child_loop = self.knit_graph.get_child_loop(loop)
            assert child_loop is not None
            self._set_x_of_loop(loop, self._get_x_of_loop(child_loop))

    def _shift_loops_by_float_alignment(self, float_increment: float = 0.25) -> None:
        """Adjust the vertical position of loops based on their float relationships."""
        float_adjusted = {}
        for yarn in self.knit_graph.yarns:
            for loop in yarn:
                relative_positions = [self._get_y_of_loop(f) + float_increment for f in loop.loops_in_front_of_floats if f < loop]
                relative_positions.extend([self._get_y_of_loop(b) - float_increment for b in loop.loops_behind_floats if b < loop])
                if len(relative_positions) > 0:
                    float_adjusted[loop] = self._get_y_of_loop(loop)
                    y = sum(relative_positions) / len(relative_positions)
                    self._set_y_of_loop(loop, y)
                else:
                    prior_loop = loop.prior_loop_on_yarn
                    if prior_loop is not None and prior_loop in float_adjusted and self._get_y_of_loop(loop) == float_adjusted[prior_loop]:
                        float_adjusted[loop] = self._get_y_of_loop(loop)
                        self._set_y_of_loop(loop, self._get_y_of_loop(prior_loop))

    def _get_course_of_loop(self, loop: LoopT) -> Course[LoopT]:
        """Get the course (horizontal row) that contains the specified loop."""
        return self.loops_to_course[loop]

    def _place_loop(self, loop: LoopT, x: float, y: float) -> None:
        """Add a loop to the visualization data graph at the specified coordinates."""
        if self._loop_has_position(loop):
            self._set_x_of_loop(loop, x)
            self._set_y_of_loop(loop, y)
        else:
            self.data_graph.add_node(loop, x=x, y=y)

    def _set_x_of_loop(self, loop: LoopT, x: float) -> None:
        """Update the x coordinate of a loop in the visualization data graph."""
        if self._loop_has_position(loop):
            self.data_graph.nodes[loop]["x"] = x
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _set_y_of_loop(self, loop: LoopT, y: float) -> None:
        """Update the y coordinate of a loop in the visualization data graph."""
        if self._loop_has_position(loop):
            self.data_graph.nodes[loop]["y"] = y
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _get_x_of_loop(self, loop: LoopT) -> float:
        """Get the x coordinate of a loop from the visualization data graph."""
        if self._loop_has_position(loop):
            return float(self.data_graph.nodes[loop]["x"])
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _get_y_of_loop(self, loop: LoopT) -> float:
        """Get the y coordinate of a loop from the visualization data graph."""
        if self._loop_has_position(loop):
            return float(self.data_graph.nodes[loop]["y"])
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _loop_has_position(self, loop: LoopT) -> bool:
        """Check if a loop has been positioned in the visualization data graph."""
        return bool(self.data_graph.has_node(loop))

    def _stitch_has_position(self, u: LoopT, v: LoopT) -> bool:
        """Check if a stitch edge between two loops has been added to the visualization."""
        return bool(self.data_graph.has_edge(u, v))

    def _place_loops_in_courses(self, course_spacing: float = 1.0) -> None:
        """Position loops in all courses above the base course."""
        y = course_spacing
        for course in self.courses[self.first_course_index + 1 : self.top_course_index]:
            self._place_loops_by_parents(course, y)
            self._swap_loops_in_cables(course)
            self._left_align_course(course)
            self._balance_course(course)
            y += course_spacing

    def _swap_loops_in_cables(self, course: Course[LoopT]) -> None:
        """Swap the horizontal positions of loops involved in cable crossings."""
        for left_loop in course:
            for right_loop in self.knit_graph.braid_graph.left_crossing_loops(left_loop):
                crossing_direction = self.knit_graph.braid_graph.get_crossing(left_loop, right_loop)
                if crossing_direction is not Crossing_Direction.No_Cross:
                    left_x = self._get_x_of_loop(left_loop)
                    self._set_x_of_loop(left_loop, self._get_x_of_loop(right_loop))
                    self._set_x_of_loop(right_loop, left_x)

    def _place_loops_by_parents(self, course: Course[LoopT], y: float) -> None:
        """Position loops in a course based on the average position of their parent loops."""
        for _x, loop in enumerate(course):
            self._set_loop_x_by_parent_average(loop, y)
        placed_loops = set()
        for loop in self._loops_need_placement:
            placed = self._set_loop_between_yarn_neighbors(loop, y)
            if placed:
                placed_loops.add(loop)
        self._loops_need_placement.difference_update(placed_loops)
        assert len(self._loops_need_placement) == 0, f"Loops {self._loops_need_placement} remain unplaced."

    def _set_loop_x_by_parent_average(self, loop: LoopT, y: float) -> None:
        """Set the x coordinate of a loop based on the weighted average of its parent positions."""
        if len(loop.parent_loops) == 0:
            self._loops_need_placement.add(loop)
            return

        def _parent_weight(stack_position: int) -> float:
            return float(len(loop.parent_loops) - stack_position)

        parent_positions = {
            self._get_x_of_loop(parent_loop) * _parent_weight(stack_pos): _parent_weight(stack_pos) for stack_pos, parent_loop in enumerate(loop.parent_loops) if self.data_graph.has_node(parent_loop)
        }
        x = sum(parent_positions.keys()) / sum(parent_positions.values())
        self._place_loop(loop, x=x, y=y)

    def _set_loop_between_yarn_neighbors(self, loop: LoopT, y: float, spacing: float = 1.0) -> bool:
        """Position a loop based on the average position of its yarn neighbors."""
        spacing = abs(spacing)
        x_neighbors = []
        prior_loop = loop.prior_loop_on_yarn
        next_loop = loop.next_loop_on_yarn
        if prior_loop is not None and self._loop_has_position(prior_loop):
            if self._get_y_of_loop(prior_loop) == y:
                x_neighbors.append(self._get_x_of_loop(prior_loop) + spacing)
            else:
                x_neighbors.append(self._get_x_of_loop(prior_loop))
        if next_loop is not None and self._loop_has_position(next_loop):
            if self._get_y_of_loop(next_loop) == y:
                x_neighbors.append(self._get_x_of_loop(next_loop) - spacing)
            else:
                x_neighbors.append(self._get_x_of_loop(next_loop))
        if len(x_neighbors) == 0:
            return False
        x = sum(x_neighbors) / float(len(x_neighbors))
        self._place_loop(loop, x=x, y=y)
        return True

    def _position_base_course(self, loop_space: float = 1.0) -> None:
        """Position the loops in the bottom course and establish base metrics."""
        base_course = self.courses[self.first_course_index]
        faces = base_course.get_faces()
        if len(faces) == 0:
            self.base_left = 0
            self.base_width = 0
            return
        first_face = faces[0]
        for x, loop in enumerate(first_face if self.start_on_left else reversed(first_face)):
            self._place_loop(loop, x=x * loop_space, y=0)

        moving_leftward = self.start_on_left
        for face in faces[1:]:
            for loop in face:
                prior_loop = loop.prior_loop_on_yarn
                if prior_loop is not None:
                    if moving_leftward:
                        self._place_loop(loop, x=self._get_x_of_loop(prior_loop) - loop_space, y=0)
                    else:
                        self._place_loop(loop, x=self._get_x_of_loop(prior_loop) + loop_space, y=0)
            moving_leftward = not moving_leftward
        self._left_align_course(base_course)
        self.base_left = min(self._get_x_of_loop(loop) for loop in base_course)
        max_x = max(self._get_x_of_loop(loop) for loop in base_course)
        self.base_width = max_x - self.base_left

    def _left_align_course(self, course: Course[LoopT]) -> None:
        """Align the leftmost loop of a course to x=0 if left alignment is enabled."""
        if self.left_zero_align:
            current_left = min(self._get_x_of_loop(loop) for loop in course)
            if current_left != 0.0:
                for loop in course:
                    self._set_x_of_loop(loop, self._get_x_of_loop(loop) - current_left)

    def _balance_course(self, course: Course[LoopT]) -> None:
        """Scale the width of a course to match the base course width if balancing is enabled."""
        current_left = min(self._get_x_of_loop(loop) for loop in course)
        max_x = max(self._get_x_of_loop(loop) for loop in course)
        course_width = max_x - current_left
        if self.balance_by_base_width and course_width != self.base_width:

            def _target_distance_from_left(l: LoopT) -> float:
                current_distance_from_left = self._get_x_of_loop(l) - current_left
                return (current_distance_from_left * self.base_width) / course_width

            for loop in course:
                self._set_x_of_loop(loop, _target_distance_from_left(loop) + current_left)

    # ── Stitch edge collection (unchanged logic) ─────────────────────────

    def _add_cable_edges(self) -> None:
        """Add all stitch edges involved in cable crossings to the appropriate trace data."""
        for left_loop, right_loop, crossing_direction in self.knit_graph.braid_graph.edge_iter:
            for left_parent in left_loop.parent_loops:
                self._add_stitch_edge(left_parent, left_loop, crossing_direction)
            for right_parent in right_loop.parent_loops:
                self._add_stitch_edge(right_parent, right_loop, ~crossing_direction)

    def _add_stitch_edges(self) -> None:
        """Add all stitch edges to the trace data based on their type and cable position."""
        self._add_cable_edges()
        for u, v, _ in self.knit_graph.edge_iter:
            if not self._stitch_has_position(u, v) and self._loop_has_position(u) and self._loop_has_position(v):
                self._add_stitch_edge(u, v, Crossing_Direction.No_Cross)

    def _add_stitch_edge(self, u: LoopT, v: LoopT, crossing_direction: Crossing_Direction) -> None:
        """Add a single stitch edge to the appropriate trace data."""
        pull_direction = self.knit_graph.get_pull_direction(u, v)
        if pull_direction is Pull_Direction.BtF:
            if crossing_direction is Crossing_Direction.Over_Right:
                trace_data = self._top_knit_trace_data
            elif crossing_direction is Crossing_Direction.Under_Right:
                trace_data = self._bot_knit_trace_data
            else:
                trace_data = self._knit_trace_data
        else:
            if crossing_direction is Crossing_Direction.Over_Right:
                trace_data = self._top_purl_trace_data
            elif crossing_direction is Crossing_Direction.Under_Right:
                trace_data = self._bot_purl_trace_data
            else:
                trace_data = self._purl_trace_data
        self.data_graph.add_edge(u, v, pull_direction=pull_direction)
        trace_data["x"].append(self._get_x_of_loop(u))
        trace_data["y"].append(self._get_y_of_loop(u))
        trace_data["edge"].append((u, v))
        trace_data["is_start"].append(True)
        trace_data["x"].append(self._get_x_of_loop(v))
        trace_data["y"].append(self._get_y_of_loop(v))
        trace_data["edge"].append((u, v))
        trace_data["is_start"].append(False)
        trace_data["x"].append(None)
        trace_data["y"].append(None)

    # ── Comparison utilities ─────────────────────────────────────────────

    def x_coordinate_differences(
        self,
        other: Knit_Graph_Visualizer[LoopT],
    ) -> dict[LoopT, tuple[float | None, float | None]]:
        """Find the differences in x-coordinates between two visualizations.

        Args:
            other: The visualization to compare to.

        Returns:
            A dict mapping loops with coordinate differences to (self_x, other_x) tuples.
        """
        differences: dict[LoopT, tuple[float | None, float | None]] = {cast(LoopT, l): (self._get_x_of_loop(l), None) for l in self.data_graph.nodes if not other.data_graph.has_node(l)}
        differences.update({cast(LoopT, l): (None, other._get_x_of_loop(l)) for l in other.data_graph.nodes if not self.data_graph.has_node(l)})
        differences.update(
            {cast(LoopT, l): (self._get_x_of_loop(l), other._get_x_of_loop(l)) for l in self.data_graph.nodes if other.data_graph.has_node(l) and self._get_x_of_loop(l) != other._get_x_of_loop(l)}
        )
        return differences

    def y_coordinate_differences(
        self,
        other: Knit_Graph_Visualizer[LoopT],
    ) -> dict[LoopT, tuple[float | None, float | None]]:
        """Find the differences in y-coordinates between two visualizations.

        Args:
            other: The visualization to compare to.

        Returns:
            A dict mapping loops with coordinate differences to (self_y, other_y) tuples.
        """
        differences: dict[LoopT, tuple[float | None, float | None]] = {cast(LoopT, l): (self._get_y_of_loop(l), None) for l in self.data_graph.nodes if not other.data_graph.has_node(l)}
        differences.update({cast(LoopT, l): (None, other._get_y_of_loop(l)) for l in other.data_graph.nodes if not self.data_graph.has_node(l)})
        differences.update(
            {cast(LoopT, l): (self._get_y_of_loop(l), other._get_y_of_loop(l)) for l in self.data_graph.nodes if other.data_graph.has_node(l) and self._get_y_of_loop(l) != other._get_y_of_loop(l)}
        )
        return differences

    def __eq__(self, other: object) -> bool:
        """Two visualizations are equal if they share the same coordinates for all loops."""
        return (
            isinstance(other, Knit_Graph_Visualizer)
            and len(self.data_graph.nodes) == len(other.data_graph.nodes)
            and len(self.x_coordinate_differences(other)) == 0
            and len(self.y_coordinate_differences(other)) == 0
        )


# ── Convenience functions ────────────────────────────────────────────────


def visualize_knit_graph(
    knit_graph: Knit_Graph,
    first_course_index: int = 0,
    top_course_index: int | None = None,
    start_on_left: bool = True,
    balance_by_base_width: bool = False,
    left_zero_align: bool = True,
    graph_title: str = "knit_graph",
    filepath: str | Path = "knit_graph.svg",
    **svg_kwargs: Any,
) -> Path:
    """Generate and save an SVG visualization of the given knit graph.

    Args:
        knit_graph: The knit graph to visualize.
        first_course_index: Index of the first (bottom) course. Defaults to 0.
        top_course_index: Index of the last (top) course. If None, visualizes all.
        start_on_left: Whether the first loop is on the left. Defaults to True.
        balance_by_base_width: Whether to scale course widths to match the base. Defaults to False.
        left_zero_align: Whether to left-align each course to x=0. Defaults to True.
        graph_title: Title displayed on the SVG. Defaults to "knit_graph".
        filepath: Output file path. Defaults to "knit_graph.svg".
        **svg_kwargs: Additional keyword arguments forwarded to
            :meth:`Knit_Graph_SVG_Visualizer.make_svg`.

    Returns:
        The resolved Path where the SVG file was written.
    """
    visualizer = Knit_Graph_Visualizer(
        knit_graph,
        first_course_index,
        top_course_index,
        start_on_left,
        balance_by_base_width,
        left_zero_align,
    )
    return visualizer.save_svg(filepath=filepath, graph_title=graph_title, **svg_kwargs)
