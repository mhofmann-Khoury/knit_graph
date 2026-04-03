"""The graph structure used to represent knitted objects.

This module contains the main Knit_Graph class which serves as the central data structure for representing knitted fabrics.
It manages the relationships between loops, yarns, and structural elements like courses and wales.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.artin_wale_braids.Loop_Braid_Graph import Loop_Braid_Graph
from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.artin_wale_braids.Wale_Group import Wale_Group
from knit_graphs.Course import Course
from knit_graphs.directed_loop_graph import Directed_Loop_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn

LoopT = TypeVar("LoopT", bound=Loop)


class Knit_Graph(Directed_Loop_Graph[LoopT, Pull_Direction]):
    """A representation of knitted structures as connections between loops on yarns.

    The Knit_Graph class is the main data structure for representing knitted fabrics.
    It maintains a directed graph of loops connected by stitch edges, manages yarn relationships,
    and provides methods for analyzing the structure of the knitted fabric including courses, wales, and cable crossings.
    """

    def __init__(self) -> None:
        """Initialize an empty knit graph with no loops or yarns."""
        super().__init__()
        self.braid_graph: Loop_Braid_Graph[LoopT] = Loop_Braid_Graph()
        self._last_loop: LoopT | None = None
        self.yarns: set[Yarn[LoopT]] = set()

    @property
    def last_loop(self) -> LoopT | None:
        """Get the most recently added loop in the graph.

        Returns:
            Loop | None: The last loop added to the graph, or None if no loops have been added.
        """
        return self._last_loop

    @property
    def stitch_iter(self) -> Iterator[tuple[LoopT, LoopT, Pull_Direction]]:
        """
        Returns:
            Iterator[tuple[LoopT, LoopT, Pull_Direction]]: Iterator over the edges and edge-data in the graph.

        Notes:
            No guarantees about the order of the edges.
        """
        return self.edge_iter

    def get_pull_direction(self, parent: LoopT | int, child: LoopT | int) -> Pull_Direction:
        """Get the pull direction of the stitch edge between parent and child loops.

        Args:
            parent (Loop | int): The parent loop of the stitch edge.
            child (Loop | int): The child loop of the stitch edge.

        Returns:
            Pull_Direction: The pull direction of the stitch-edge between the parent and child.
        """
        return self.get_edge(parent, child)

    def add_crossing(self, left_loop: LoopT, right_loop: LoopT, crossing_direction: Crossing_Direction) -> None:
        """Add a cable crossing between two loops with the specified crossing direction.

        Args:
            left_loop (Loop): The loop on the left side of the crossing.
            right_loop (Loop): The loop on the right side of the crossing.
            crossing_direction (Crossing_Direction): The direction of the crossing (over, under, or none) between the loops.
        """
        self.braid_graph.add_crossing(left_loop, right_loop, crossing_direction)

    def add_loop(self, loop: LoopT) -> None:
        """Add a loop to the knit graph as a node.

        Args:
            loop (Loop): The loop to be added as a node in the graph. If the loop's yarn is not already in the graph, it will be added automatically.
        """
        super().add_loop(loop)
        if loop.yarn not in self.yarns:
            self.add_yarn(loop.yarn)
        if self._last_loop is None or loop > self._last_loop:
            self._last_loop = loop

    def remove_loop(self, loop: LoopT | int) -> None:
        """
        Remove the given loop from the knit graph.
        Args:
            loop (Loop | int): The loop or loop_id to be removed.

        Raises:
            KeyError: If the loop is not in the knit graph.

        """
        if isinstance(loop, int):
            loop = self.get_loop(loop)
        if loop in self.braid_graph:
            self.braid_graph.remove_loop(loop)  # remove any crossing associated with this loop.
        # Remove any stitch edges involving this loop.
        if self.has_child_loop(loop):
            child_loop = self.get_child_loop(loop)
            if child_loop is not None:
                child_loop.remove_parent(loop)
        super().remove_loop(loop)
        # Remove loop from any floating positions
        for yarn in self.yarns:
            yarn.remove_loop_relative_to_floats(loop)
        # Remove loop from yarn
        yarn = loop.yarn
        yarn.remove_loop(loop)
        if len(yarn) == 0:  # This was the only loop on that yarn
            self.yarns.discard(yarn)
        # Reset last loop
        if loop is self.last_loop:
            if len(self.yarns) == 0:  # No loops left
                self._last_loop = None
            else:  # Set to the newest loop formed at the end of any yarns.
                self._last_loop = max(y.last_loop for y in self.yarns if y.last_loop is not None)

    def add_yarn(self, yarn: Yarn[LoopT]) -> None:
        """Add a yarn to the graph without adding its loops.

        Args:
            yarn (Yarn[LoopT]): The yarn to be added to the graph structure. This method assumes that loops do not need to be added separately.
        """
        self.yarns.add(yarn)

    def connect_loops(
        self,
        parent_loop: LoopT,
        child_loop: LoopT,
        pull_direction: Pull_Direction = Pull_Direction.BtF,
        stack_position: int | None = None,
    ) -> None:
        """Create a stitch edge by connecting a parent and child loop.

        Args:
            parent_loop (Loop): The parent loop to connect to the child loop.
            child_loop (Loop): The child loop to connect to the parent loop.
            pull_direction (Pull_Direction): The direction the child is pulled through the parent. Defaults to Pull_Direction.BtF (knit stitch).
            stack_position (int | None, optional): The position to insert the parent into the child's parent stack. If None, adds on top of the stack. Defaults to None.

        Raises:
            KeyError: If either the parent_loop or child_loop is not already in the knit graph.
        """
        super().add_edge(parent_loop, child_loop, pull_direction)
        child_loop.add_parent_loop(parent_loop, stack_position)

    def get_wales_ending_with_loop(self, last_loop: LoopT) -> set[Wale[LoopT]]:
        """Get all wales (vertical columns of stitches) that end at the specified loop.

        Args:
            last_loop (Loop): The last loop of the joined set of wales.

        Returns:
            set[Wale[LoopT]]: The set of wales that end at this loop.
        """
        if len(last_loop.parent_loops) == 0:
            return {Wale[LoopT](last_loop, self)}
        sources = self.source_loops(last_loop)
        return {Wale[LoopT](source, self) for source in sources}

    def get_terminal_wales(self) -> dict[LoopT, list[Wale]]:
        """
        Get wale groups organized by their terminal loops.

        Returns:
            dict[Loop, list[Wale]]: Dictionary mapping terminal loops to list of wales that terminate that wale.
        """
        wale_groups = {}
        for loop in self.terminal_loops:
            wale_groups[loop] = list(self.get_wales_ending_with_loop(loop))
        return wale_groups

    def get_courses(self) -> list[Course[LoopT]]:
        """Get all courses (horizontal rows) in the knit graph in chronological order.

        Returns:
            list[Course[LoopT]: A list of courses representing horizontal rows of loops.
        """
        courses = []
        course = Course(0, self)
        for loop in self.sorted_loops:
            if not course.isdisjoint(loop.parent_loops):  # start a new course
                courses.append(course)
                course = Course(course.course_number + 1, self)
            course.add_loop(loop)
        courses.append(course)
        return courses

    def get_wale_groups(self) -> set[Wale_Group]:
        """Get wale groups organized by their terminal loops.

        Returns:
            set[Wale_Group]: The set of wale-groups that lead to the terminal loops of this graph. Each wale group represents a collection of wales that end at the same terminal loop.
        """
        return {Wale_Group(terminal_loop, self) for terminal_loop in self.terminal_loops}
