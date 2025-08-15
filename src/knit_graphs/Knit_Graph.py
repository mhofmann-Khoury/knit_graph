"""The graph structure used to represent knitted objects.

This module contains the main Knit_Graph class which serves as the central data structure for representing knitted fabrics.
It manages the relationships between loops, yarns, and structural elements like courses and wales.
"""
from __future__ import annotations

from typing import Any, cast

from knit_graphs._base_classes import _Base_Knit_Graph
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.artin_wale_braids.Loop_Braid_Graph import Loop_Braid_Graph
from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.artin_wale_braids.Wale_Group import Wale_Group
from knit_graphs.Course import Course
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn


class Knit_Graph(_Base_Knit_Graph):
    """A representation of knitted structures as connections between loops on yarns.

    The Knit_Graph class is the main data structure for representing knitted fabrics.
    It maintains a directed graph of loops connected by stitch edges, manages yarn relationships,
    and provides methods for analyzing the structure of the knitted fabric including courses, wales, and cable crossings.
    """

    def __init__(self) -> None:
        """Initialize an empty knit graph with no loops or yarns."""
        super().__init__()
        self.braid_graph: Loop_Braid_Graph = Loop_Braid_Graph()
        self._last_loop: None | Loop = None
        self.yarns: set[Yarn] = set()

    @property
    def last_loop(self) -> None | Loop:
        """Get the most recently added loop in the graph.

        Returns:
            None | Loop: The last loop added to the graph, or None if no loops have been added.
        """
        return self._last_loop

    @property
    def has_loop(self) -> bool:
        """Check if the graph contains any loops.

        Returns:
            bool: True if the graph has at least one loop, False otherwise.
        """
        return self.last_loop is not None

    def add_crossing(self, left_loop: Loop, right_loop: Loop, crossing_direction: Crossing_Direction) -> None:
        """Add a cable crossing between two loops with the specified crossing direction.

        Args:
            left_loop (Loop): The loop on the left side of the crossing.
            right_loop (Loop): The loop on the right side of the crossing.
            crossing_direction (Crossing_Direction): The direction of the crossing (over, under, or none) between the loops.
        """
        self.braid_graph.add_crossing(left_loop, right_loop, crossing_direction)

    def add_loop(self, loop: Loop) -> None:
        """Add a loop to the knit graph as a node.

        Args:
            loop (Loop): The loop to be added as a node in the graph. If the loop's yarn is not already in the graph, it will be added automatically.
        """
        self.stitch_graph.add_node(loop)
        if loop.yarn not in self.yarns:
            self.add_yarn(cast(Yarn, loop.yarn))
        if self._last_loop is None or loop > self._last_loop:
            self._last_loop = loop

    def add_yarn(self, yarn: Yarn) -> None:
        """Add a yarn to the graph without adding its loops.

        Args:
            yarn (Yarn): The yarn to be added to the graph structure. This method assumes that loops do not need to be added separately.
        """
        self.yarns.add(yarn)

    def connect_loops(self, parent_loop: Loop, child_loop: Loop,
                      pull_direction: Pull_Direction = Pull_Direction.BtF,
                      stack_position: int | None = None) -> None:
        """Create a stitch edge by connecting a parent and child loop.

        Args:
            parent_loop (Loop): The parent loop to connect to the child loop.
            child_loop (Loop): The child loop to connect to the parent loop.
            pull_direction (Pull_Direction): The direction the child is pulled through the parent. Defaults to Pull_Direction.BtF (knit stitch).
            stack_position (int | None, optional): The position to insert the parent into the child's parent stack. If None, adds on top of the stack. Defaults to None.

        Raises:
            KeyError: If either the parent_loop or child_loop is not already in the knit graph.
        """
        if parent_loop not in self:
            raise KeyError(f"parent loop {parent_loop} not in Knit Graph")
        if child_loop not in self:
            raise KeyError(f"child loop {parent_loop} not in Knit Graph")
        self.stitch_graph.add_edge(parent_loop, child_loop, pull_direction=pull_direction)
        child_loop.add_parent_loop(parent_loop, stack_position)

    def get_wale_starting_with_loop(self, first_loop: Loop) -> Wale:
        """Get a wale (vertical column of stitches) starting from the specified loop.

        Args:
            first_loop (Loop): The loop at the start of the wale to be constructed.

        Returns:
            Wale: A wale object representing the vertical column of stitches starting from the given loop.
        """
        wale = Wale(first_loop)
        cur_loop = first_loop
        while len(self.stitch_graph.successors(cur_loop)) == 1:
            cur_loop = [*self.stitch_graph.successors(cur_loop)][0]
            assert isinstance(wale.last_loop, Loop)
            wale.add_loop_to_end(cur_loop, self.get_pull_direction(wale.last_loop, cur_loop))
        return wale

    def get_wales_ending_with_loop(self, last_loop: Loop) -> list[Wale]:
        """Get all wales (vertical columns of stitches) that end at the specified loop.

        Args:
            last_loop (Loop): The last loop of the joined set of wales.

        Returns:
            list[Wale]: The set of wales that end at this loop. Only returns multiple wales if this loop is a child of a decrease stitch.
        """
        wales = []
        for top_stitch_parent in self.stitch_graph.predecessors(last_loop):
            wale = Wale(last_loop)
            wale.add_loop_to_beginning(top_stitch_parent, cast(Pull_Direction, self.get_pull_direction(top_stitch_parent, last_loop)))
            cur_loop = top_stitch_parent
            while len(cur_loop.parent_loops) == 1:  # stop at split for decrease or start of wale
                cur_loop = [*self.stitch_graph.predecessors(cur_loop)][0]
                wale.add_loop_to_beginning(cur_loop, cast(Pull_Direction, self.get_pull_direction(cur_loop, cast(Loop, wale.first_loop))))
            wales.append(wale)
        return wales

    def get_courses(self) -> list[Course]:
        """Get all courses (horizontal rows) in the knit graph in chronological order.

        Returns:
            list[Course]: A list of courses representing horizontal rows of loops.
            The first course contains the initial set of loops. A course change occurs when a loop has a parent loop in the previous course.
        """
        courses = []
        course = Course(self)
        for loop in sorted([*self.stitch_graph.nodes]):
            for parent in self.stitch_graph.predecessors(loop):
                if parent in course:  # start a new course
                    courses.append(course)
                    course = Course(self)
                    break
            course.add_loop(loop)
        courses.append(course)
        return courses

    def get_wale_groups(self) -> dict[Loop, Wale_Group]:
        """Get wale groups organized by their terminal loops.

        Returns:
            dict[Loop, Wale_Group]: Dictionary mapping terminal loops to the wale groups they terminate. Each wale group represents a collection of wales that end at the same terminal loop.
        """
        wale_groups = {}
        for loop in self.stitch_graph.nodes:
            if self.is_terminal_loop(loop):
                wale_groups.update({loop: Wale_Group(wale, self) for wale in self.get_wales_ending_with_loop(loop)})
        return wale_groups

    def __contains__(self, item: Loop) -> bool:
        """Check if a loop is contained in the knit graph.

        Args:
            item (Loop): The loop being checked for in the graph.

        Returns:
            bool: True if the loop is in the graph, False otherwise.
        """
        return bool(self.stitch_graph.has_node(item))

    def get_pull_direction(self, parent: Loop, child: Loop) -> Pull_Direction | None:
        """Get the pull direction of the stitch edge between parent and child loops.

        Args:
            parent (Loop): The parent loop of the stitch edge.
            child (Loop): The child loop of the stitch edge.

        Returns:
            Pull_Direction | None: The pull direction of the stitch-edge between the parent and child, or None if there is no edge between these loops.
        """
        edge = self.get_stitch_edge(parent, child)
        if edge is None:
            return None
        else:
            return cast(Pull_Direction, edge['pull_direction'])

    def get_stitch_edge(self, parent: Loop, child: Loop) -> dict[str, Any] | None:
        """Get the stitch edge data between two loops.

        Args:
            parent (Loop): The parent loop of the stitch edge.
            child (Loop): The child loop of the stitch edge.

        Returns:
            dict[str, Any] | None: The edge data dictionary for this stitch edge, or None if no edge exists between these loops.
        """
        if self.stitch_graph.has_edge(parent, child):
            return cast(dict[str, Any], self.stitch_graph.get_edge_data(parent, child))
        else:
            return None

    def get_child_loop(self, loop: Loop) -> Loop | None:
        """Get the child loop of the specified parent loop.

        Args:
            loop (Loop): The loop to look for a child loop from.

        Returns:
            Loop | None: The child loop if one exists, or None if no child loop is found.
        """
        successors = [*self.stitch_graph.successors(loop)]
        if len(successors) == 0:
            return None
        return cast(Loop, successors[0])

    def has_child_loop(self, loop: Loop) -> bool:
        """Check if a loop has a child loop connected to it.

        Args:
            loop (Loop): The loop to check for child connections.

        Returns:
            bool: True if the loop has a child loop, False otherwise.
        """
        return self.get_child_loop(loop) is not None

    def is_terminal_loop(self, loop: Loop) -> bool:
        """Check if a loop is terminal (has no child loops and terminates a wale).

        Args:
            loop (Loop): The loop to check for terminal status.

        Returns:
            bool: True if the loop has no child loops and terminates a wale, False otherwise.
        """
        return not self.has_child_loop(loop)
