"""Module containing the Loop Braid Graph class.

This module provides the Loop_Braid_Graph class which tracks crossing relationships between loops in cable knitting patterns using a directed graph structure.
"""
from typing import cast

from networkx import DiGraph

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Loop import Loop


class Loop_Braid_Graph:
    """A graph structure that tracks crossing braid edges between loops in cable patterns.

    This class maintains a directed graph where nodes are loops and edges represent cable crossings between those loops.
    It provides methods to add crossings, query crossing relationships, and determine which loops cross with a given loop.

    Attributes:
        loop_crossing_graph (DiGraph): A NetworkX directed graph storing loop crossing relationships with crossing direction attributes.
    """

    def __init__(self) -> None:
        """Initialize an empty loop braid graph with no crossings."""
        self.loop_crossing_graph: DiGraph = DiGraph()

    def add_crossing(self, left_loop: Loop, right_loop: Loop, crossing_direction: Crossing_Direction) -> None:
        """Add a crossing edge between two loops with the specified crossing direction.

        Args:
            left_loop (Loop): The loop on the left side of the crossing.
            right_loop (Loop): The loop on the right side of the crossing.
            crossing_direction (Crossing_Direction): The direction of the crossing (over, under, or none) between the loops.
        """
        self.loop_crossing_graph.add_edge(left_loop, right_loop, crossing=crossing_direction)

    def __contains__(self, item: Loop | tuple[Loop, Loop]) -> bool:
        """Check if a loop or loop pair is contained in the braid graph.

        Args:
            item (Loop | tuple[Loop, Loop]): Either a single loop to check for node membership, or a tuple of loops to check for edge membership.

        Returns:
            bool: True if the loop is a node in the graph (for single loop) or if there is an edge between the loops (for tuple).
        """
        if isinstance(item, Loop):
            return item in self.loop_crossing_graph.nodes
        else:
            return bool(self.loop_crossing_graph.has_edge(item[0], item[1]))

    def left_crossing_loops(self, left_loop: Loop) -> list[Loop]:
        """Get all loops that cross with the given loop when it is on the left side.

        Args:
            left_loop (Loop): The loop on the left side of potential crossings.

        Returns:
            list[Loop]: List of loops that this loop crosses over on the right side. Empty list if the loop is not in the graph or has no crossings.
        """
        if left_loop not in self:
            return []
        else:
            return [rl for rl in self.loop_crossing_graph.successors(left_loop)
                    if self.get_crossing(left_loop, rl) is not Crossing_Direction.No_Cross]

    def right_crossing_loops(self, right_loop: Loop) -> list[Loop]:
        """Get all loops that cross with the given loop when it is on the right side.

        Args:
            right_loop (Loop): The loop on the right side of potential crossings.

        Returns:
            list[Loop]: List of loops that cross this loop from the left side. Empty list if the loop is not in the graph or has no crossings.
        """
        if right_loop not in self:
            return []
        else:
            return [l for l in self.loop_crossing_graph.predecessors(right_loop)
                    if self.get_crossing(l, right_loop) is not Crossing_Direction.No_Cross]

    def get_crossing(self, left_loop: Loop, right_loop: Loop) -> Crossing_Direction:
        """Get the crossing direction between two loops, creating a no-cross edge if none exists.

        If no edge exists between the loops, this method automatically adds a no-crossing edge to maintain consistency in the graph structure.

        Args:
            left_loop (Loop): The loop on the left side of the crossing.
            right_loop (Loop): The loop on the right side of the crossing.

        Returns:
            Crossing_Direction: The crossing direction between the left and right loop. Defaults to No_Cross if no explicit crossing was previously defined.
        """
        if not self.loop_crossing_graph.has_edge(left_loop, right_loop):
            self.add_crossing(left_loop, right_loop, Crossing_Direction.No_Cross)
        return cast(Crossing_Direction, self.loop_crossing_graph[left_loop][right_loop]['crossing'])
