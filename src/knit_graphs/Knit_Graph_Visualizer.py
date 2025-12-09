"""Module used to visualize a Knit graph with the plotly graph object library.

This module provides comprehensive visualization capabilities for knit graphs using Plotly.
It handles the positioning of loops, rendering of yarn paths, stitch edges, and cable crossings to create interactive 2D visualizations of knitted structures.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from typing import TypedDict, cast

import plotly.io as pio
from networkx import DiGraph
from plotly.graph_objs import Figure, Layout, Scatter

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Course import Course
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction


class TraceData(TypedDict):
    """Typing specification for the dictionaries passes as traces to Plotly"""

    x: list[float | None]
    y: list[float | None]
    edge: list[tuple[Loop, Loop]]
    is_start: list[bool]


def configure_plotly_environment() -> None:
    """Auto-configure Plotly based on environment detection to avoid socket issues."""
    # Check if we're in a testing environment
    if "pytest" in sys.modules or "unittest" in sys.modules or os.environ.get("TESTING") or os.environ.get("CI"):
        # For testing, don't set a default renderer - we'll handle this with show_figure=False
        pass
    elif "ipykernel" in sys.modules or "jupyter" in sys.modules:
        # Jupyter environment - use notebook renderer
        pio.renderers.default = "notebook"
    else:
        # Development environment - use browser but with timeout to prevent hanging
        pio.renderers.default = "browser"


# Configure environment on import
configure_plotly_environment()


class Knit_Graph_Visualizer:
    """A class used to visualize a knit graph using the plotly graph objects library.

    This class converts knit graph data structures into interactive 2D visualizations by calculating loop positions,
    rendering yarn paths, and displaying stitch relationships with appropriate styling for different stitch types and cable crossings.

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
        knit_graph: Knit_Graph,
        first_course_index: int = 0,
        top_course_index: int | None = None,
        start_on_left: bool = True,
        balance_by_base_width: bool = False,
        left_zero_align: bool = True,
    ):
        """Initialize the knit graph visualizer with specified configuration options.

        Args:
            knit_graph (Knit_Graph): The knit graph to be visualized.
            first_course_index (int, optional): The index of the first course to include in the visualization. Defaults to 0.
            top_course_index (int | None, optional): The index of the last course to include in the visualization. If None, includes all courses up to the top.
            start_on_left (bool, optional): Whether to position the first loop on the left side of the visualization. Defaults to True.
            balance_by_base_width (bool, optional): Whether to scale all course widths to match the base course width. Defaults to False.
            left_zero_align (bool, optional): Whether to align the leftmost loop of each course to x=0. Defaults to True.
        """
        self.left_zero_align: bool = left_zero_align
        self.balance_by_base_width: bool = balance_by_base_width
        self.start_on_left: bool = start_on_left
        self.knit_graph: Knit_Graph = knit_graph
        self.courses: list[Course] = knit_graph.get_courses()
        if top_course_index is None:
            top_course_index = len(self.courses)
        self.top_course_index: int = top_course_index
        self.first_course_index: int = first_course_index
        self.base_width: float = float(len(self.courses[first_course_index]))  # Updates when creating base course.
        self.base_left: float = 0.0  # Updates when creating the base course.
        self.loops_to_course: dict[Loop, Course] = {}
        for course in self.courses:
            self.loops_to_course.update({loop: course for loop in course})
        self.data_graph: DiGraph = DiGraph()
        self._loops_need_placement: set[Loop] = set()
        self._loop_markers: list[Scatter] = []
        self._yarn_traces: list[Scatter] = []
        self._top_knit_trace_data: TraceData = {
            "x": [],
            "y": [],
            "edge": [],
            "is_start": [],
        }
        self._bot_knit_trace_data: TraceData = {
            "x": [],
            "y": [],
            "edge": [],
            "is_start": [],
        }
        self._top_purl_trace_data: TraceData = {
            "x": [],
            "y": [],
            "edge": [],
            "is_start": [],
        }
        self._bot_purl_trace_data: TraceData = {
            "x": [],
            "y": [],
            "edge": [],
            "is_start": [],
        }
        self._knit_trace_data: TraceData = {
            "x": [],
            "y": [],
            "edge": [],
            "is_start": [],
        }
        self._purl_trace_data: TraceData = {
            "x": [],
            "y": [],
            "edge": [],
            "is_start": [],
        }
        # Form the visualization.
        self._position_loops()
        self._set_loop_markers()
        self._set_yarn_traces()
        self._add_stitch_edges()

    def make_figure(self, graph_title: str = "Knit Graph") -> Figure:
        """Generate the interactive figure to visualize this knit graph.

        Args:
            graph_title (str, optional): The title to display on the figure. Defaults to "Knit Graph".

        Returns:
            Figure: The plotly figure object.
        """
        go_layout = Layout(
            title=graph_title,
            showlegend=True,
            hovermode="closest",
            margin={"b": 20, "l": 5, "r": 5, "t": 40},
        )
        figure_data = [
            self._top_knit_trace(),
            self._top_purl_trace(),
            self._no_cross_knit_trace(),
            self._no_cross_purl_trace(),
            self._bot_knit_trace(),
            self._bot_purl_trace(),
        ]
        figure_data.extend(self._yarn_traces)
        figure_data.extend(self._loop_markers)
        fig = Figure(data=figure_data, layout=go_layout)
        return fig

    def show_figure(self, graph_title: str = "Knit Graph", renderer: str | None = None) -> None:
        """Generate and display the interactive figure to visualize this knit graph.

        Args:
            graph_title (str, optional): The title to display on the figure. Defaults to "Knit Graph".
            renderer (str, optional): Plotly renderer to use. If None, uses the default configured renderer.
        """
        fig = self.make_figure(graph_title)

        # Configure display to minimize resource usage
        config = {
            "displayModeBar": False,  # Hide toolbar to reduce resource usage
            "displaylogo": False,  # Hide plotly logo
            "staticPlot": False,  # Keep interactive
            "scrollZoom": False,  # Allow zoom
            "doubleClick": "reset+autosize",  # Double-click behavior
        }

        try:
            if renderer:
                fig.show(renderer=renderer, config=config)
            else:
                fig.show(config=config)
        except Exception as e:
            print(f"Warning: Could not display figure: {e}")
            print(
                "Figure created successfully but display failed. Consider using show_figure=False and accessing the returned Figure object directly."
            )

    def _no_cross_knit_trace(self, line_width: float = 4.0, knit_color: str = "blue") -> Scatter:
        """Create a scatter trace for knit stitches not involved in cable crossings.

        Args:
            line_width (float, optional): The width of the lines representing the stitch edges. Defaults to 4.0.
            knit_color (str, optional): The color of knit stitches in the visualization. Defaults to 'blue'.

        Returns:
            Scatter: The plotly scatter object used to visualize knit stitches not involved in cables.
        """
        return self._stitch_trace(self._knit_trace_data, "Knit Stitches", knit_color, line_width, opacity=0.8)

    def _top_knit_trace(self, line_width: float = 5.0, knit_color: str = "blue") -> Scatter:
        """Create a scatter trace for knit stitches that cross over other stitches in cables.

        Args:
            line_width (float, optional): The width of the lines representing the stitch edges. Defaults to 5.0.
            knit_color (str, optional): The color of knit stitches in the visualization. Defaults to 'blue'.

        Returns:
            Scatter: The plotly scatter object used to visualize knit stitches on top of cable crossings.
        """
        return self._stitch_trace(
            self._top_knit_trace_data,
            "Knit Stitches on Top of Cable",
            knit_color,
            line_width,
            opacity=1.0,
        )

    def _bot_knit_trace(self, line_width: float = 3.0, knit_color: str = "blue") -> Scatter:
        """Create a scatter trace for knit stitches that cross under other stitches in cables.

        Args:
            line_width (float, optional): The width of the lines representing the stitch edges. Defaults to 3.0.
            knit_color (str, optional): The color of knit stitches in the visualization. Defaults to 'blue'.

        Returns:
            Scatter: The plotly scatter object used to visualize knit stitches below cable crossings.
        """
        return self._stitch_trace(
            self._bot_knit_trace_data,
            "Knit Stitches Below Cable",
            knit_color,
            line_width,
            opacity=0.5,
        )

    def _no_cross_purl_trace(self, line_width: float = 4.0, purl_color: str = "red") -> Scatter:
        """Create a scatter trace for purl stitches not involved in cable crossings.

        Args:
            line_width (float, optional): The width of the lines representing the stitch edges. Defaults to 4.0.
            purl_color (str, optional): The color of purl stitches in the visualization. Defaults to 'red'.

        Returns:
            Scatter: The plotly scatter object used to visualize purl stitches not involved in cables.
        """
        return self._stitch_trace(self._purl_trace_data, "Purl Stitches", purl_color, line_width, opacity=0.8)

    def _top_purl_trace(self, line_width: float = 5.0, purl_color: str = "red") -> Scatter:
        """Create a scatter trace for purl stitches that cross over other stitches in cables.

        Args:
            line_width (float, optional): The width of the lines representing the stitch edges. Defaults to 5.0.
            purl_color (str, optional): The color of purl stitches in the visualization. Defaults to 'red'.

        Returns:
            Scatter: The plotly scatter object used to visualize purl stitches on top of cable crossings.
        """
        return self._stitch_trace(
            self._top_purl_trace_data,
            "Purl Stitches on Top of Cable",
            purl_color,
            line_width,
            opacity=1.0,
        )

    def _bot_purl_trace(self, line_width: float = 3.0, purl_color: str = "red") -> Scatter:
        """Create a scatter trace for purl stitches that cross under other stitches in cables.

        Args:
            line_width (float, optional): The width of the lines representing the stitch edges. Defaults to 3.0.
            purl_color (str, optional): The color of purl stitches in the visualization. Defaults to 'red'.

        Returns:
            Scatter: The plotly scatter object used to visualize purl stitches below cable crossings.
        """
        return self._stitch_trace(
            self._bot_purl_trace_data,
            "Purl Stitches Below Cable",
            purl_color,
            line_width,
            opacity=0.5,
        )

    @staticmethod
    def _stitch_trace(
        trace_data: TraceData,
        trace_name: str,
        trace_color: str,
        line_width: float,
        opacity: float,
    ) -> Scatter:
        """Create a generic scatter trace for stitch visualization with specified styling.

        Args:
            trace_data (dict[str, list[float | None] | list[tuple[Loop, Loop] | list[bool]]]): The trace data containing x, y coordinates and edge information to be plotted.
            trace_name (str): The name of the trace to show in the figure legend.
            trace_color (str): The color of the trace lines.
            line_width (float): The width of lines representing the stitch edges.
            opacity (float): The opacity of the trace lines (0.0 to 1.0).

        Returns:
            Scatter: The plotly scatter object configured to visualize the given stitch traces.
        """
        return Scatter(
            name=trace_name,
            x=trace_data["x"],
            y=trace_data["y"],
            line={"width": line_width, "color": trace_color, "dash": "solid"},
            opacity=opacity,
            mode="lines",
        )

    def _add_cable_edges(self) -> None:
        """Add all stitch edges that are involved in cable crossings to the appropriate trace data."""
        for (
            left_loop,
            right_loop,
        ) in self.knit_graph.braid_graph.loop_crossing_graph.edges:
            crossing_direction = self.knit_graph.braid_graph.get_crossing(left_loop, right_loop)
            for left_parent in left_loop.parent_loops:
                self._add_stitch_edge(left_parent, left_loop, crossing_direction)
            for right_parent in right_loop.parent_loops:
                self._add_stitch_edge(right_parent, right_loop, ~crossing_direction)

    def _add_stitch_edges(self) -> None:
        """Add all stitch edges to the visualization trace data based on their type and cable position."""
        self._add_cable_edges()
        # Add remaining stitches as though they have no cable crossing.
        for u, v in self.knit_graph.stitch_graph.edges:
            if (
                not self._stitch_has_position(u, v)  # This edge has not been placed
                and self._loop_has_position(u)
                and self._loop_has_position(v)
            ):  # Both loops do have positions.
                self._add_stitch_edge(u, v, Crossing_Direction.No_Cross)

    def _add_stitch_edge(self, u: Loop, v: Loop, crossing_direction: Crossing_Direction) -> None:
        """Add a single stitch edge to the appropriate trace data based on stitch type and cable crossing."""
        pull_direction = self.knit_graph.get_pull_direction(u, v)
        if pull_direction is None:
            return  # No edge between these loops
        elif pull_direction is Pull_Direction.BtF:  # Knit Stitch:
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

    def _set_loop_markers(self, loop_size: float = 30.0, loop_border_width: float = 2.0) -> None:
        """Create plotly scatter objects to mark the position of each loop in the visualization."""
        yarns_to_loop_data = {
            yarn: {
                "x": [self._get_x_of_loop(loop) for loop in yarn],
                "y": [self._get_y_of_loop(loop) for loop in yarn],
                "loop_id": [loop.loop_id for loop in yarn],
            }
            for yarn in self.knit_graph.yarns
        }
        self._loop_markers = [
            Scatter(
                name=f"Loops on {yarn.yarn_id}",
                x=yarn_data["x"],
                y=yarn_data["y"],
                text=yarn_data["loop_id"],
                textposition="middle center",
                mode="markers+text",
                marker={
                    "reversescale": True,
                    "color": yarn.properties.color,
                    "size": loop_size,
                    "line_width": loop_border_width,
                },
            )
            for yarn, yarn_data in yarns_to_loop_data.items()
        ]

    def _set_yarn_traces(self, line_width: float = 1.0, smoothing: float = 1.3) -> None:
        """Create plotly traces representing the path of each yarn through the knitted structure."""
        yarns_to_float_data = {}
        for yarn in self.knit_graph.yarns:
            float_data: dict[str, list[float]] = {"x": [], "y": []}
            for u in yarn:
                if self._loop_has_position(u):
                    float_data["x"].append(self._get_x_of_loop(u))
                    float_data["y"].append(self._get_y_of_loop(u))
            yarns_to_float_data[yarn] = float_data
        self._yarn_traces = [
            Scatter(
                name=yarn.yarn_id,
                x=float_data["x"],
                y=float_data["y"],
                line={
                    "width": line_width,
                    "color": yarn.properties.color,
                    "shape": "spline",
                    "smoothing": smoothing,
                },
                mode="lines",
            )
            for yarn, float_data in yarns_to_float_data.items()
        ]

    def _position_loops(self) -> None:
        """Calculate and set the x,y coordinate positions of all loops to be visualized."""
        self._position_base_course()
        self._place_loops_in_courses()
        self._shift_knit_purl()
        self._shift_loops_by_float_alignment()

    def _shift_knit_purl(self, shift: float = 0.1) -> None:
        """Adjust the horizontal position of loops to visually distinguish knit from purl stitches."""
        has_knits = any(
            self.knit_graph.get_pull_direction(u, v) is Pull_Direction.BtF
            for u, v in self.knit_graph.stitch_graph.edges
        )
        has_purls = any(
            self.knit_graph.get_pull_direction(u, v) is Pull_Direction.FtB
            for u, v in self.knit_graph.stitch_graph.edges
        )
        if not (has_knits and has_purls):
            return  # Don't make any changes, because all stitches are of the same type.
        yarn_over_align = set()
        for loop in self.data_graph.nodes:
            if not loop.has_parent_loops():  # Yarn-over
                if self.knit_graph.has_child_loop(loop):  # Align yarn-overs with one child to its child
                    yarn_over_align.add(loop)
                continue  # Don't shift yarn-overs
            knit_parents = len(
                [u for u in loop.parent_loops if self.knit_graph.get_pull_direction(u, loop) is Pull_Direction.BtF]
            )
            purl_parents = len(
                [u for u in loop.parent_loops if self.knit_graph.get_pull_direction(u, loop) is Pull_Direction.FtB]
            )
            if knit_parents > purl_parents:  # Shift the loop as though it is being knit.
                self._set_x_of_loop(loop, self._get_x_of_loop(loop) - shift)
            elif purl_parents > knit_parents:  # Shift the loop as though it is being purled.
                self._set_x_of_loop(loop, self._get_x_of_loop(loop) + shift)

        for loop in yarn_over_align:
            child_loop = self.knit_graph.get_child_loop(loop)
            assert isinstance(child_loop, Loop)
            self._set_x_of_loop(loop, self._get_x_of_loop(child_loop))

    def _shift_loops_by_float_alignment(self, float_increment: float = 0.25) -> None:
        """Adjust the vertical position of loops based on their float relationships."""
        for yarn in self.knit_graph.yarns:
            for u, v, front_loops in yarn.loops_in_front_of_floats():
                for front_loop in front_loops:
                    if u in self._get_course_of_loop(front_loop) and v in self._get_course_of_loop(
                        front_loop
                    ):  # same course, adjust float position
                        self._set_y_of_loop(
                            front_loop,
                            self._get_y_of_loop(front_loop) - float_increment,
                        )  # shift loop down to show it is in front of the float.
            for u, v, back_loops in yarn.loops_behind_floats():
                for back_loop in back_loops:
                    if u in self._get_course_of_loop(back_loop) and v in self._get_course_of_loop(
                        back_loop
                    ):  # same course, adjust float position
                        self._set_y_of_loop(
                            back_loop, self._get_y_of_loop(back_loop) + float_increment
                        )  # shift loop up to show it is behind the float.

    def _get_course_of_loop(self, loop: Loop) -> Course:
        """Get the course (horizontal row) that contains the specified loop."""
        return self.loops_to_course[loop]

    def _place_loop(self, loop: Loop, x: float, y: float) -> None:
        """Add a loop to the visualization data graph at the specified coordinates."""
        if self._loop_has_position(loop):
            self._set_x_of_loop(loop, x)
            self._set_y_of_loop(loop, y)
        else:
            self.data_graph.add_node(loop, x=x, y=y)

    def _set_x_of_loop(self, loop: Loop, x: float) -> None:
        """Update the x coordinate of a loop that already exists in the visualization data graph."""
        if self._loop_has_position(loop):
            self.data_graph.nodes[loop]["x"] = x
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _set_y_of_loop(self, loop: Loop, y: float) -> None:
        """Update the y coordinate of a loop that already exists in the visualization data graph."""
        if self._loop_has_position(loop):
            self.data_graph.nodes[loop]["y"] = y
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _get_x_of_loop(self, loop: Loop) -> float:
        """Get the x coordinate of a loop from the visualization data graph."""
        if self._loop_has_position(loop):
            return float(self.data_graph.nodes[loop]["x"])
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _get_y_of_loop(self, loop: Loop) -> float:
        """Get the y coordinate of a loop from the visualization data graph."""
        if self._loop_has_position(loop):
            return float(self.data_graph.nodes[loop]["y"])
        else:
            raise KeyError(f"Loop {loop} is not in the data graph")

    def _loop_has_position(self, loop: Loop) -> bool:
        """Check if a loop has been positioned in the visualization data graph."""
        return bool(self.data_graph.has_node(loop))

    def _stitch_has_position(self, u: Loop, v: Loop) -> bool:
        """Check if a stitch edge between two loops has been added to the visualization data graph."""
        return bool(self.data_graph.has_edge(u, v))

    def _place_loops_in_courses(self, course_spacing: float = 1.0) -> None:
        """Position loops in all courses above the base course using parent relationships and yarn connections."""
        y = course_spacing
        for course in self.courses[self.first_course_index + 1 : self.top_course_index]:
            self._place_loops_by_parents(course, y)
            self._swap_loops_in_cables(course)
            self._left_align_course(course)
            self._balance_course(course)
            y += course_spacing  # Shift y coordinate up with each course

    def _swap_loops_in_cables(self, course: Course) -> None:
        """Swap the horizontal positions of loops involved in cable crossings within a course."""
        for left_loop in course:
            for right_loop in self.knit_graph.braid_graph.left_crossing_loops(left_loop):
                crossing_direction = self.knit_graph.braid_graph.get_crossing(left_loop, right_loop)
                if (
                    crossing_direction is not Crossing_Direction.No_Cross
                ):  # Swap the position of loops that cross each other.
                    left_x = self._get_x_of_loop(left_loop)
                    self._set_x_of_loop(left_loop, self._get_x_of_loop(right_loop))
                    self._set_x_of_loop(right_loop, left_x)

    def _place_loops_by_parents(self, course: Course, y: float) -> None:
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
        # A loops past the first course should have at least one yarn neighbor to place them.

    def _set_loop_x_by_parent_average(self, loop: Loop, y: float) -> None:
        """Set the x coordinate of a loop based on the weighted average position of its parent loops."""
        if len(loop.parent_loops) == 0:
            self._loops_need_placement.add(loop)
            return

        def _parent_weight(stack_position: int) -> float:
            return float(len(loop.parent_loops) - stack_position)

        parent_positions = {
            self._get_x_of_loop(parent_loop)
            * _parent_weight(stack_pos): _parent_weight(  # position of parents weighted by their stack position.
                stack_pos
            )  # weight of the stack position.
            for stack_pos, parent_loop in enumerate(loop.parent_loops)
            if self.data_graph.has_node(parent_loop)
        }  # Only include parent loops that are positioned.
        x = sum(parent_positions.keys()) / sum(parent_positions.values())
        self._place_loop(loop, x=x, y=y)

    def _set_loop_between_yarn_neighbors(self, loop: Loop, y: float, spacing: float = 1.0) -> bool:
        """Position a loop based on the average position of its neighboring loops along the yarn."""
        spacing = abs(spacing)  # Ensure spacing is positive.
        x_neighbors = []
        prior_loop = loop.prior_loop_on_yarn()
        next_loop = loop.next_loop_on_yarn()
        if prior_loop is not None and self._loop_has_position(prior_loop):
            if (
                self._get_y_of_loop(prior_loop) == y
            ):  # Include the spacing to ensure these are not at overlapping positions.
                x_neighbors.append(self._get_x_of_loop(prior_loop) + spacing)
            else:  # Don't include spacing because the prior loop is on the prior course.
                x_neighbors.append(self._get_x_of_loop(prior_loop))
        if next_loop is not None and self._loop_has_position(next_loop):
            if (
                self._get_y_of_loop(next_loop) == y
            ):  # Include the spacing to ensure these are not at overlapping positions.
                x_neighbors.append(self._get_x_of_loop(next_loop) - spacing)
            else:  # Don't include spacing because the prior loop is on the prior course.
                x_neighbors.append(self._get_x_of_loop(next_loop))
        if len(x_neighbors) == 0:
            return False
        x = sum(x_neighbors) / float(len(x_neighbors))  # the average of the two neighbors
        self._place_loop(loop, x=x, y=y)
        return True

    def _position_base_course(self) -> None:
        """Position the loops in the bottom course of the visualization and establish base metrics."""
        base_course = self.courses[self.first_course_index]
        if len(
            self.courses
        ) > self.first_course_index + 1 and base_course.in_round_with(  # There are more courses to show after the base course
            self.courses[self.first_course_index + 1]
        ):  # The first course is knit in the round to form a tube structure.
            self._get_base_round_course_positions(base_course)
        else:
            self._get_base_row_course_positions(base_course)
        self._left_align_course(base_course)
        self.base_left = min(self._get_x_of_loop(loop) for loop in base_course)
        max_x = max(self._get_x_of_loop(loop) for loop in base_course)
        self.base_width = max_x - self.base_left

    def _get_base_round_course_positions(
        self, base_course: Course, loop_space: float = 1.0, back_shift: float = 0.5
    ) -> None:
        """Position loops in the base course for circular/tube knitting structure."""
        split_index = len(base_course) // 2  # Split the course in half to form a tube.
        front_loops: list[Loop] = cast(list[Loop], base_course[:split_index])
        front_set: set[Loop] = set(front_loops)
        back_loops: list[Loop] = cast(list[Loop], base_course[split_index:])
        if self.start_on_left:
            back_loops = [*reversed(back_loops)]
        else:
            front_loops = [*reversed(front_loops)]
        for x, front_loop in enumerate(front_loops):
            self._place_loop(front_loop, x=x, y=0)
        for x, back_loop in enumerate(back_loops):
            float_positions = [
                self._get_x_of_loop(front_loop) for front_loop in back_loop.front_floats if front_loop in front_set
            ]
            if (
                len(float_positions) > 0
            ):  # If the back loop is floating behind other loops in the front of the course, set the position to be centered between the loops it is floating behind.
                self._place_loop(
                    back_loop,
                    x=sum(float_positions) / float(len(float_positions)),
                    y=0.0,
                )
            elif self.start_on_left:
                self._place_loop(back_loop, x=(x * loop_space) + back_shift, y=0)
            else:
                self._place_loop(back_loop, x=(x * loop_space) - back_shift, y=0)

    def _get_base_row_course_positions(self, base_course: Course, loop_space: float = 1.0) -> None:
        """Position loops in the base course for flat/row knitting structure."""
        loops: Iterable[Loop] = list(base_course)
        if not self.start_on_left:
            loops = reversed(base_course)
        for x, loop in enumerate(loops):
            self._place_loop(loop, x=x * loop_space, y=0)

    def _left_align_course(self, course: Course) -> None:
        """Align the leftmost loop of a course to x=0 if left alignment is enabled."""
        if self.left_zero_align:
            current_left = min(self._get_x_of_loop(loop) for loop in course)
            if current_left != 0.0:
                for loop in course:
                    self._set_x_of_loop(loop, self._get_x_of_loop(loop) - current_left)

    def _balance_course(self, course: Course) -> None:
        """Scale the width of a course to match the base course width if balancing is enabled."""
        current_left = min(self._get_x_of_loop(loop) for loop in course)
        max_x = max(self._get_x_of_loop(loop) for loop in course)
        course_width = max_x - current_left
        if self.balance_by_base_width and course_width != self.base_width:

            def _target_distance_from_left(l: Loop) -> float:
                current_distance_from_left = self._get_x_of_loop(l) - current_left
                return (current_distance_from_left * self.base_width) / course_width

            for loop in course:
                self._set_x_of_loop(loop, _target_distance_from_left(loop) + current_left)

    def x_coordinate_differences(self, other: Knit_Graph_Visualizer) -> dict[Loop, tuple[float | None, float | None]]:
        """Find the differences in x-coordinates between two knitgraph visualizations. Used for testing and comparing visualization results.

        Args:
            other (Knit_Graph_Visualizer): The knitgraph visualization to compare to.

        Returns:
            dict[Loop: tuple[float | None, float | None]]: The differences in x-coordinates.
            * The keys of the dictionary are loops with differences between the two visualizations.
            * The values of the dictionary are tuples of floats or None.
            ** The first value in each tuple is the x-coordinate of the loop in this knitgraph visualization or None if the loop is not in this visualization.
            ** The second value of each tuple is the x-coordinate of the loop in the other visualization or NOne if the loop is not in that visualization.

        """
        differences: dict[Loop, tuple[float | None, float | None]] = {
            cast(Loop, l): (self._get_x_of_loop(l), None)
            for l in self.data_graph.nodes
            if not other.data_graph.has_node(l)
        }
        differences.update(
            {
                cast(Loop, l): (None, other._get_x_of_loop(l))
                for l in other.data_graph.nodes
                if not self.data_graph.has_node(l)
            }
        )
        differences.update(
            {
                cast(Loop, l): (self._get_x_of_loop(l), other._get_x_of_loop(l))
                for l in self.data_graph.nodes
                if other.data_graph.has_node(l) and self._get_x_of_loop(l) != other._get_x_of_loop(l)
            }
        )
        return differences

    def y_coordinate_differences(self, other: Knit_Graph_Visualizer) -> dict[Loop, tuple[float | None, float | None]]:
        """Find the differences in y-coordinates between two knitgraph visualizations. Used for testing and comparing visualization results.

        Args:
            other (Knit_Graph_Visualizer): The knitgraph visualization to compare to.

        Returns:
            dict[Loop: tuple[float | None, float | None]]: The differences in y-coordinates.
            * The keys of the dictionary are loops with differences between the two visualizations.
            * The values of the dictionary are tuples of floats or None.
            ** The first value in each tuple is the y-coordinate of the loop in this knitgraph visualization or None if the loop is not in this visualization.
            ** The second value of each tuple is the y-coordinate of the loop in the other visualization or NOne if the loop is not in that visualization.

        """
        differences: dict[Loop, tuple[float | None, float | None]] = {
            cast(Loop, l): (self._get_y_of_loop(l), None)
            for l in self.data_graph.nodes
            if not other.data_graph.has_node(l)
        }
        differences.update(
            {
                cast(Loop, l): (None, other._get_y_of_loop(l))
                for l in other.data_graph.nodes
                if not self.data_graph.has_node(l)
            }
        )
        differences.update(
            {
                cast(Loop, l): (self._get_y_of_loop(l), other._get_y_of_loop(l))
                for l in self.data_graph.nodes
                if other.data_graph.has_node(l) and self._get_y_of_loop(l) != other._get_y_of_loop(l)
            }
        )
        return differences

    def __eq__(self, other: object) -> bool:
        """Two visualizations are equal if share the same x,y coordinates for all loops in the visualization and both contain the same set of loop nodes.
        Args:
            other (Knit_Graph_Visualizer): The knitgraph visualization to compare to.

        Returns:
            bool: True if the knitgraph visualizations are equal, False otherwise.
        """
        return (
            isinstance(other, Knit_Graph_Visualizer)
            and len(self.data_graph.nodes) == len(other.data_graph.nodes)
            and len(self.x_coordinate_differences(other)) == 0
            and len(self.y_coordinate_differences(other)) == 0
        )


def visualize_knit_graph(
    knit_graph: Knit_Graph,
    first_course_index: int = 0,
    top_course_index: int | None = None,
    start_on_left: bool = True,
    balance_by_base_width: bool = False,
    left_zero_align: bool = True,
    graph_title: str = "knit_graph",
    show_figure: bool = True,
    renderer: str | None = None,
) -> Figure:
    """Generate and optionally display a plotly visualization of the given knit graph with specified configuration.

    Args:
        knit_graph (Knit_Graph): The knit graph to visualize.
        first_course_index (int): Index of the first (bottom) course to include in the visualization. Defaults to 0.
        top_course_index (int | None): Index of the last (top) course to include in the visualization. If None, visualizes up to the top of the knit graph.
        start_on_left (bool): Whether the first loop knit is presumed to be positioned on the left of the pattern. Defaults to True.
        balance_by_base_width (bool): Whether to scale all course widths to match the first course width. Defaults to False.
        left_zero_align (bool): Whether to align the leftmost position of each course with x=0 in the figure. Defaults to True.
        graph_title (str): The title to display on the generated figure. Defaults to "knit_graph".
        show_figure (bool, optional): If True, the visualization will be shown. Defaults to True.
        renderer (str, optional): Plotly renderer to use. Common options: 'browser', 'notebook'. Defaults to None (uses configured default).

    Returns:
        Figure: The plotly figure object.
    """
    visualizer = Knit_Graph_Visualizer(
        knit_graph,
        first_course_index,
        top_course_index,
        start_on_left,
        balance_by_base_width,
        left_zero_align,
    )
    fig = visualizer.make_figure(graph_title)

    if show_figure:
        try:
            # Configure display to minimize resource usage
            config = {
                "displayModeBar": False,  # Hide toolbar to reduce resource usage
                "displaylogo": False,  # Hide plotly logo
                "staticPlot": False,  # Keep interactive
                "scrollZoom": True,  # Allow zoom
                "doubleClick": "reset+autosize",  # Double-click behavior
            }

            if renderer:
                fig.show(renderer=renderer, config=config)
            else:
                fig.show(config=config)
        except Exception as e:
            print(f"Warning: Could not display figure '{graph_title}': {e}")
            print("Figure created successfully but display failed.")

    return fig


def visualize_knit_graph_safe(
    knit_graph: Knit_Graph,
    first_course_index: int = 0,
    top_course_index: int | None = None,
    start_on_left: bool = True,
    balance_by_base_width: bool = False,
    left_zero_align: bool = True,
    graph_title: str = "knit_graph",
) -> Figure:
    """Generate a plotly visualization of the given knit graph with specified configuration.
    This function is safe for UnitTest and other headless environments because it does not attempt to show the visualization.

    Args:
        knit_graph (Knit_Graph): The knit graph to visualize.
        first_course_index (int): Index of the first (bottom) course to include in the visualization. Defaults to 0.
        top_course_index (int | None): Index of the last (top) course to include in the visualization. If None, visualizes up to the top of the knit graph.
        start_on_left (bool): Whether the first loop knit is presumed to be positioned on the left of the pattern. Defaults to True.
        balance_by_base_width (bool): Whether to scale all course widths to match the first course width. Defaults to False.
        left_zero_align (bool): Whether to align the leftmost position of each course with x=0 in the figure. Defaults to True.
        graph_title (str): The title to display on the generated figure. Defaults to "knit_graph".

    Returns:
        Figure: The plotly figure object.
    """
    return visualize_knit_graph(
        knit_graph,
        first_course_index=first_course_index,
        top_course_index=top_course_index,
        start_on_left=start_on_left,
        balance_by_base_width=balance_by_base_width,
        left_zero_align=left_zero_align,
        graph_title=graph_title,
        show_figure=False,
    )
