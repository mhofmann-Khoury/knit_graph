"""Module containing the Wale Class.

This module defines the Wale class which represents a vertical column of stitches in a knitted structure, maintaining the sequence and relationships between loops in that column.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, overload

from knit_graphs.directed_loop_graph import Directed_Loop_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction

if TYPE_CHECKING:
    from knit_graphs.Knit_Graph import Knit_Graph

LoopT = TypeVar("LoopT", bound=Loop)


class Wale(Directed_Loop_Graph[LoopT, Pull_Direction]):
    """A data structure representing stitch relationships between loops in a vertical column of a knitted structure.

    A wale represents a vertical sequence of loops connected by stitch edges, forming a column in the knitted fabric.
    This class manages the sequential relationships between loops and tracks the pull directions of stitches within the wale.

    Attributes:
        first_loop (Loop | None): The first (bottom) loop in the wale sequence.
        last_loop (Loop | None): The last (top) loop in the wale sequence.
    """

    def __init__(self, first_loop: LoopT, knit_graph: Knit_Graph[LoopT], end_loop: LoopT | None = None) -> None:
        """Initialize a wale optionally starting with a specified loop.

        Args:
            first_loop (Loop): The initial loop to start the wale with.
            knit_graph (Knit_Graph): The knit graph that owns this wale.
            end_loop (Loop, optional):
                The loop to terminate the wale with.
                If no loop is provided or this loop is not found, the wale will terminate at the first loop with no child.
        """
        super().__init__()
        self.add_loop(first_loop)
        self._knit_graph: Knit_Graph[LoopT] = knit_graph
        self.first_loop: LoopT = first_loop
        self.last_loop: LoopT = first_loop
        self._build_wale_from_first_loop(end_loop)

    def overlaps(self, other: Wale) -> bool:
        """
        Args:
            other (Wale): The other wale to compare against for overlapping loops.

        Returns:
            bool: True if the other wale has any overlapping loop(s) with this wale, False otherwise.
        """
        return any(loop in other for loop in self)

    def get_pull_direction(self, u: LoopT, v: LoopT) -> Pull_Direction:
        """Get the pull direction of the stitch edge between two loops in this wale.

        Args:
            u (LoopT): The parent loop in the stitch connection.
            v (LoopT): The child loop in the stitch connection.

        Returns:
            Pull_Direction: The pull direction of the stitch between loops u and v.
        """
        return self.get_edge(u, v)

    def split_wale(self, split_loop: LoopT) -> tuple[Wale[LoopT], Wale[LoopT] | None]:
        """
        Split this wale at the specified loop into two separate wales.

        The split loop becomes the last loop of the first wale and the first loop of the second wale.

        Args:
            split_loop (Loop): The loop at which to split the wale. This loop will appear in both resulting wales.

        Returns:
            tuple[Wale[LoopT], Wale[LoopT] | None]:
                A tuple containing:
                * The first wale (from start to split_loop). This will be the whole wale if the split_loop is not found.
                * The second wale (from split_loop to end). This will be None if the split_loop is not found.
        """
        if split_loop in self:
            return (
                Wale[LoopT](self.first_loop, self._knit_graph, end_loop=split_loop),
                Wale[LoopT](split_loop, self._knit_graph, end_loop=self.last_loop),
            )
        else:
            return self, None

    def _build_wale_from_first_loop(self, end_loop: LoopT | None) -> None:
        for child in [*self._knit_graph.dfs_preorder_loops(self.first_loop)][1:]:
            self.add_loop_to_end(child)
            if end_loop is not None and child is end_loop:
                return  # found the end loop, so wrap up the wale

    def add_loop_to_end(self, loop: LoopT) -> None:
        """
        Add a loop to the end (top) of the wale.
        Args:
            loop (T): The loop to add to the end of the wale.
        """
        self.add_loop(loop)
        self.add_edge(self.last_loop, loop, self._knit_graph.get_edge(self.last_loop, loop))
        self.last_loop = loop

    def __eq__(self, other: object) -> bool:
        """
        Args:
            other (Wale): The wale to compare.

        Returns:
            bool: True if all the loops in both wales are present and in the same order. False, otherwise.
        """
        if not isinstance(other, Wale) or len(self) != len(other):
            return False
        return not any(l != o for l, o in zip(self, other, strict=False))

    @overload
    def __getitem__(self, item: int) -> LoopT: ...

    @overload
    def __getitem__(self, item: tuple[LoopT | int, LoopT | int]) -> Pull_Direction: ...

    @overload
    def __getitem__(self, item: slice) -> list[LoopT]: ...

    def __getitem__(self, item: int | tuple[LoopT | int, LoopT | int] | slice) -> LoopT | Pull_Direction | list[LoopT]:
        """Get a loop by its ID from this yarn.

        Args:
            item (int | tuple[LoopT | int, LoopT | int] | slice):
                The loop ,loop ID, or float between two loops to retrieve from this yarn.
                If given a slice, it will retrieve the elements between the specified indices in the standard ordering of loops along the wale.

        Returns:
            LoopT: The loop on the yarn with the matching ID.
            Stitch_Edge: The edge data for the given pair of loops forming a stitch in the wale.
            list[LoopT]: The loops in the slice of the wale based on their ordering along the wale.

        Raises:
            KeyError: If the item is not found on this yarn.
        """
        if isinstance(item, slice):
            return list(self)[item]
        else:
            return super().__getitem__(item)

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
