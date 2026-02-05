"""Module containing the Loop Braid Graph class.

This module provides the Loop_Braid_Graph class which tracks crossing relationships between loops in cable knitting patterns using a directed graph structure.
"""

from __future__ import annotations

from typing import TypeVar

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.directed_loop_graph import Directed_Loop_Graph
from knit_graphs.Loop import Loop

LoopT = TypeVar("LoopT", bound=Loop)


class Loop_Braid_Graph(Directed_Loop_Graph[LoopT, Crossing_Direction]):
    """A graph structure that tracks crossing braid edges between loops in cable patterns.

    This class maintains a directed graph where nodes are loops and edges represent cable crossings between those loops.
    It provides methods to add crossings, query crossing relationships, and determine which loops cross with a given loop.
    """

    def __init__(self) -> None:
        """Initialize an empty loop braid graph with no crossings."""
        super().__init__()

    def get_crossing(self, left_loop: LoopT, right_loop: LoopT) -> Crossing_Direction:
        """
        Args:
            left_loop (Loop): The loop on the left side of the crossing.
            right_loop (Loop): The loop on the right side of the crossing.

        Returns:
            Crossing_Direction: The crossing direction between the left and right loop. Defaults to No_Cross if no explicit crossing was previously defined.
        """
        if self.has_edge(left_loop, right_loop):
            return self.get_edge(left_loop, right_loop)
        elif self.has_edge(right_loop, left_loop):
            return self.get_edge(right_loop, left_loop).opposite
        else:
            return Crossing_Direction.No_Cross

    def add_crossing(self, left_loop: LoopT, right_loop: LoopT, crossing_direction: Crossing_Direction) -> None:
        """Add a crossing edge between two loops with the specified crossing direction.

        If the opposite crossing edge has already been defined, it will be removed from the graph so that only one crossing relationship is ever defined for each pair of the loops.

        Args:
            left_loop (Loop): The loop on the left side of the crossing.
            right_loop (Loop): The loop on the right side of the crossing.
            crossing_direction (Crossing_Direction): The direction of the crossing (over, under, or none) between the loops.
        """
        if self.has_edge(right_loop, left_loop):  # Remove the edge that will be implied by the new crossing formation.
            self.remove_edge(right_loop, left_loop)
        if left_loop not in self:
            self.add_loop(left_loop)
        if right_loop not in self:
            self.add_loop(right_loop)
        self.add_edge(left_loop, right_loop, crossing_direction)

    def left_crossing_loops(self, left_loop: LoopT) -> set[LoopT]:
        """Get all loops that cross with the given loop when it is on the left side.

        Args:
            left_loop (Loop): The loop on the left side of potential crossings.

        Returns:
            set[Loop]: Set of loops that this loop crosses over on the right side. Empty set if the loop is not in the graph or has no crossings.
        """
        if left_loop not in self:
            return set()
        else:
            return {
                rl
                for rl in self.successors(left_loop)
                if self.get_crossing(left_loop, rl) is not Crossing_Direction.No_Cross
            }

    def right_crossing_loops(self, right_loop: LoopT) -> set[LoopT]:
        """Get all loops that cross with the given loop when it is on the right side.

        Args:
            right_loop (Loop): The loop on the right side of potential crossings.

        Returns:
            list[Loop]: List of loops that cross this loop from the left side. Empty list if the loop is not in the graph or has no crossings.
        """
        if right_loop not in self:
            return set()
        else:
            return {
                l
                for l in self.predecessors(right_loop)
                if self.get_crossing(l, right_loop) is not Crossing_Direction.No_Cross
            }
