"""The graph structure used to represent knitted objects.

This module contains the main Knit_Graph class which serves as the central data structure for representing knitted fabrics.
It manages the relationships between loops, yarns, and structural elements like courses and wales.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypedDict, cast, overload

from networkx import DiGraph

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.artin_wale_braids.Loop_Braid_Graph import Loop_Braid_Graph
from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.artin_wale_braids.Wale_Group import Wale_Group
from knit_graphs.Course import Course
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn


class Stitch_Edge(TypedDict):
    """Type safe dict for accessing the edge data of stitch edges in Knit Graphs"""

    pull_direction: Pull_Direction


class Knit_Graph:
    """A representation of knitted structures as connections between loops on yarns.

    The Knit_Graph class is the main data structure for representing knitted fabrics.
    It maintains a directed graph of loops connected by stitch edges, manages yarn relationships,
    and provides methods for analyzing the structure of the knitted fabric including courses, wales, and cable crossings.
    """

    def __init__(self) -> None:
        """Initialize an empty knit graph with no loops or yarns."""
        self.stitch_graph: DiGraph = DiGraph()
        self._loop_ids: dict[int, Loop] = {}
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
        self._loop_ids[loop.loop_id] = loop
        if loop.yarn not in self.yarns:
            self.add_yarn(loop.yarn)
        if self._last_loop is None or loop > self._last_loop:
            self._last_loop = loop

    def remove_loop(self, loop: Loop | int) -> None:
        """
        Remove the given loop from the knit graph.
        Args:
            loop (Loop | int): The loop or loop_id to be removed.

        Raises:
            KeyError: If the loop is not in the knit graph.

        """
        if loop not in self:
            raise KeyError(f"Loop {loop} not on the knit graph")
        if isinstance(loop, int):
            loop = self._loop_ids[loop]
        self.braid_graph.remove_loop(loop)  # remove any crossing associated with this loop.
        # Remove any stitch edges involving this loop.
        loop.remove_parent_loops()
        if self.has_child_loop(loop):
            child_loop = self.get_child_loop(loop)
            assert isinstance(child_loop, Loop)
            child_loop.remove_parent(loop)
        self.stitch_graph.remove_node(loop)
        del self._loop_ids[loop.loop_id]
        # Remove loop from any floating positions
        loop.remove_loop_from_front_floats()
        loop.remove_loop_from_back_floats()
        # Remove loop from yarn
        yarn = loop.yarn
        yarn.remove_loop(loop)
        if len(yarn) == 0:  # This was the only loop on that yarn
            self.yarns.discard(yarn)
        # Reset last loop
        if loop is self.last_loop:
            if len(self.yarns) == 0:  # No loops left
                assert len(self.stitch_graph.nodes) == 0
                self._last_loop = None
            else:  # Set to the newest loop formed at the end of any yarns.
                self._last_loop = max(y.last_loop for y in self.yarns if isinstance(y.last_loop, Loop))

    def add_yarn(self, yarn: Yarn) -> None:
        """Add a yarn to the graph without adding its loops.

        Args:
            yarn (Yarn): The yarn to be added to the graph structure. This method assumes that loops do not need to be added separately.
        """
        self.yarns.add(yarn)

    def connect_loops(
        self,
        parent_loop: Loop,
        child_loop: Loop,
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
        if parent_loop not in self:
            raise KeyError(f"parent loop {parent_loop} not in Knit Graph")
        if child_loop not in self:
            raise KeyError(f"child loop {parent_loop} not in Knit Graph")
        self.stitch_graph.add_edge(parent_loop, child_loop, pull_direction=pull_direction)
        child_loop.add_parent_loop(parent_loop, stack_position)

    def get_wales_ending_with_loop(self, last_loop: Loop) -> set[Wale]:
        """Get all wales (vertical columns of stitches) that end at the specified loop.

        Args:
            last_loop (Loop): The last loop of the joined set of wales.

        Returns:
            set[Wale]: The set of wales that end at this loop.
        """
        if len(last_loop.parent_loops) == 0:
            return {Wale(last_loop, self)}
        ancestors = last_loop.ancestor_loops()
        return {Wale(ancestor_loop, self) for ancestor_loop in ancestors}

    def get_terminal_wales(self) -> dict[Loop, list[Wale]]:
        """
        Get wale groups organized by their terminal loops.

        Returns:
            dict[Loop, list[Wale]]: Dictionary mapping terminal loops to list of wales that terminate that wale.
        """
        wale_groups = {}
        for loop in self.terminal_loops():
            wale_groups[loop] = list(self.get_wales_ending_with_loop(loop))
        return wale_groups

    def get_courses(self) -> list[Course]:
        """Get all courses (horizontal rows) in the knit graph in chronological order.

        Returns:
            list[Course]: A list of courses representing horizontal rows of loops.
            The first course contains the initial set of loops. A course change occurs when a loop has a parent loop in the previous course.
        """
        courses = []
        course = Course(self)
        for loop in self.sorted_loops():
            for parent in loop.parent_loops:
                if parent in course:  # start a new course
                    courses.append(course)
                    course = Course(self)
                    break
            course.add_loop(loop)
        courses.append(course)
        return courses

    def get_wale_groups(self) -> set[Wale_Group]:
        """Get wale groups organized by their terminal loops.

        Returns:
            set[Wale_Group]: The set of wale-groups that lead to the terminal loops of this graph. Each wale group represents a collection of wales that end at the same terminal loop.
        """
        return {Wale_Group(terminal_loop, self) for terminal_loop in self.terminal_loops()}

    def __contains__(self, item: int | Loop | tuple[Loop | int, Loop | int]) -> bool:
        """Check if a loop is contained in the knit graph.

        Args:
            item (int | Loop | tuple[Loop, Loop]): The loop being checked for in the graph or the parent-child stitch edge to check for in the knit graph.

        Returns:
            bool: True if the given loop or stitch edge is in the graph, False otherwise.
        """
        if isinstance(item, int):
            return item in self._loop_ids
        elif isinstance(item, Loop):
            return bool(self.stitch_graph.has_node(item))
        else:
            return self.has_stitch_edge(item[0], item[1])

    def __iter__(self) -> Iterator[Loop]:
        """
        Returns:
            Iterator[Loop]: An iterator over all loops in the knit graph.
        """
        return cast(Iterator[Loop], iter(self.stitch_graph.nodes))

    @property
    def stitch_iter(self) -> Iterator[tuple[Loop, Loop, Stitch_Edge]]:
        """
        Returns:
            Iterator[tuple[Loop, Loop, Stitch_Edge]]:
                An iterator over all the stitch edges in the knit graph.
                Each element is a parent loop, child loop, and then the stitch edge data.

        Notes:
            There are no guarantees about the order of the stitch edges.
        """
        return iter(
            (cast(Loop, u), cast(Loop, v), cast(Stitch_Edge, d)) for u, v, d in self.stitch_graph.edges(data=True)
        )

    @overload
    def __getitem__(self, item: Loop | int) -> Loop: ...

    @overload
    def __getitem__(self, item: tuple[Loop | int, Loop | int]) -> Loop: ...

    def __getitem__(self, item: int | Loop | tuple[Loop | int, Loop | int]) -> Loop | tuple[Loop, Loop, Stitch_Edge]:
        """
        Args:
            item (int | Loop | tuple[Loop | int, Loop | int]):
                A loop or loop_id used to access a specific loop in the knit graph.
                If given a tuple, the result is the stitch-edge data for two loops or loop_ids.

        Returns:

        """
        if item not in self:
            if isinstance(item, tuple):
                raise KeyError(f"Stitch between of {item[0]} and {item[1]} not in knit graph")
            else:
                raise KeyError(f"Loop {item} not in knit graph")
        if isinstance(item, tuple) and self.has_stitch_edge(item[0], item[1]):
            return self[item[0]], self[item[1]], cast(Stitch_Edge, self.get_stitch_edge(item[0], item[1]))
        elif isinstance(item, int):
            return self._loop_ids[item]
        else:
            return cast(Loop, self.stitch_graph.nodes[item])

    def sorted_loops(self) -> list[Loop]:
        """
        Returns:
            list[Loop]: The list of loops in the stitch graph sorted from the earliest formed loop to the latest formed loop.
        """
        return sorted(self.stitch_graph.nodes)

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
            return edge["pull_direction"]

    def has_stitch_edge(self, parent: Loop | int, child: Loop | int) -> bool:
        """
        Args:
            parent (Loop | int): The loop or loop_id of the parent of the stitch being searched for.
            child (Loop | int): The loop or loop_id of the child of the stitch being searched for.

        Returns:
            bool: True if there is a stitch from the parent to the child loop, False otherwise.

        """
        if isinstance(parent, int):
            parent = self[parent]
        if isinstance(child, int):
            child = self[child]
        return bool(self.stitch_graph.has_edge(parent, child))

    def get_stitch_edge(self, parent: Loop | int, child: Loop | int) -> Stitch_Edge | None:
        """Get the stitch edge data between two loops.

        Args:
            parent (Loop | int): The parent loop of the stitch edge.
            child (Loop | int): The child loop of the stitch edge.

        Returns:
            Stitch_Edge | None: The edge data dictionary for this stitch edge, or None if no edge exists between these loops.
        """
        if isinstance(parent, int):
            parent = self[parent]
        if isinstance(child, int):
            child = self[child]
        if self.has_stitch_edge(parent, child):
            return cast(Stitch_Edge, self.stitch_graph.get_edge_data(parent, child))
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

    def terminal_loops(self) -> Iterator[Loop]:
        """
        Returns:
            Iterator[Loop]: An iterator over all terminal loops in the knit graph.
        """
        return iter(loop for loop in self if self.is_terminal_loop(loop))
