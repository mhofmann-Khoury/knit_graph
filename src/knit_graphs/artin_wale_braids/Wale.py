"""Module containing the Wale Class.

This module defines the Wale class which represents a vertical column of stitches in a knitted structure, maintaining the sequence and relationships between loops in that column.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, cast

from networkx import DiGraph, dfs_preorder_nodes

from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction

if TYPE_CHECKING:
    from knit_graphs.Knit_Graph import Knit_Graph


class Wale:
    """A data structure representing stitch relationships between loops in a vertical column of a knitted structure.

    A wale represents a vertical sequence of loops connected by stitch edges, forming a column in the knitted fabric.
    This class manages the sequential relationships between loops and tracks the pull directions of stitches within the wale.

    Attributes:
        first_loop (Loop | None): The first (bottom) loop in the wale sequence.
        last_loop (Loop | None): The last (top) loop in the wale sequence.
        stitches (DiGraph): Stores the directed graph of stitch connections within this wale.
    """
    _PULL_DIRECTION: str = "pull_direction"

    def __init__(self, first_loop: Loop, knit_graph: Knit_Graph, end_loop: Loop | None = None) -> None:
        """Initialize a wale optionally starting with a specified loop.

        Args:
            first_loop (Loop): The initial loop to start the wale with.
            knit_graph (Knit_Graph): The knit graph that owns this wale.
            end_loop (Loop, optional):
                The loop to terminate the wale with.
                If no loop is provided or this loop is not found, the wale will terminate at the first loop with no child.
        """
        self.stitches: DiGraph = DiGraph()
        self.stitches.add_node(first_loop)
        self._knit_graph: Knit_Graph = knit_graph
        self.first_loop: Loop = first_loop
        self.last_loop: Loop = first_loop
        self._build_wale_from_first_loop(end_loop)

    def _build_wale_from_first_loop(self, end_loop: Loop | None) -> None:
        while self._knit_graph.has_child_loop(self.last_loop):
            child = self._knit_graph.get_child_loop(self.last_loop)
            assert isinstance(child, Loop)
            self.add_loop_to_end(child)
            if end_loop is not None and child is end_loop:
                return  # found the end loop, so wrap up the wale

    def add_loop_to_end(self, loop: Loop) -> None:
        """
        Add a loop to the end (top) of the wale with the specified pull direction.

        Args:
            loop (Loop): The loop to add to the end of the wale.
        """
        self.stitches.add_edge(self.last_loop, loop, pull_direction=self._knit_graph.get_pull_direction(self.last_loop, loop))
        self.last_loop = loop

    def get_stitch_pull_direction(self, u: Loop, v: Loop) -> Pull_Direction:
        """Get the pull direction of the stitch edge between two loops in this wale.

        Args:
            u (Loop): The parent loop in the stitch connection.
            v (Loop): The child loop in the stitch connection.

        Returns:
            Pull_Direction: The pull direction of the stitch between loops u and v.
        """
        return cast(Pull_Direction, self.stitches.edges[u, v][self._PULL_DIRECTION])

    def split_wale(self, split_loop: Loop) -> tuple[Wale, Wale | None]:
        """
        Split this wale at the specified loop into two separate wales.

        The split loop becomes the last loop of the first wale and the first loop of the second wale.

        Args:
            split_loop (Loop): The loop at which to split the wale. This loop will appear in both resulting wales.

        Returns:
            tuple[Wale, Wale | None]:
                A tuple containing:
                * The first wale (from start to split_loop). This will be the whole wale if the split_loop is not found.
                * The second wale (from split_loop to end). This will be None if the split_loop is not found.
        """
        if split_loop in self:
            return (Wale(self.first_loop, self._knit_graph, end_loop=split_loop),
                    Wale(split_loop, self._knit_graph, end_loop=self.last_loop))
        else:
            return self, None

    def __eq__(self, other: Wale) -> bool:
        """
        Args:
            other (Wale): The wale to compare.

        Returns:
            bool: True if all the loops in both wales are present and in the same order. False, otherwise.
        """
        if len(self) != len(other):
            return False
        return not any(l != o for l, o in zip(self, other))

    def __len__(self) -> int:
        """Get the number of loops in this wale.

        Returns:
            int: The total number of loops in this wale.
        """
        return len(self.stitches.nodes)

    def __iter__(self) -> Iterator[Loop]:
        """Iterate over loops in this wale from first to last.

        Returns:
            Iterator[Loop]: An iterator over the loops in this wale in their sequential order from bottom to top.
        """
        return cast(Iterator[Loop], dfs_preorder_nodes(self.stitches, source=self.first_loop))

    def __getitem__(self, item: int | slice) -> Loop | list[Loop]:
        """Get loop(s) at the specified index or slice within this wale.

        Args:
            item (int | slice): The index of a single loop or a slice for multiple loops.

        Returns:
            Loop | list[Loop]: The loop at the specified index, or a list of loops for a slice.
        """
        if isinstance(item, int):
            return cast(Loop, self.stitches.nodes[item])
        elif isinstance(item, slice):
            return list(self)[item]

    def __contains__(self, item: Loop) -> bool:
        """Check if a loop is contained in this wale.

        Args:
            item (Loop): The loop to check for membership in this wale.

        Returns:
            bool: True if the loop is in this wale, False otherwise.
        """
        return bool(self.stitches.has_node(item))

    def __hash__(self) -> int:
        """
        Get the hash value of this wale based on its first loop.

        Returns:
            int: Hash value based on the first loop in this wale.
        """
        return hash(self.first_loop)

    def __str__(self) -> str:
        """
        Returns:
            str: The string representation of this wale.
        """
        return f"Wale({self.first_loop}->{self.last_loop})"

    def __repr__(self) -> str:
        """
        Returns:
            str: The string representation of this wale.
        """
        return str(self)

    def overlaps(self, other: Wale) -> bool:
        """Check if this wale has any loops in common with another wale.

        Args:
            other (Wale): The other wale to compare against for overlapping loops.

        Returns:
            bool: True if the other wale has any overlapping loop(s) with this wale, False otherwise.
        """
        return any(loop in other for loop in self)
