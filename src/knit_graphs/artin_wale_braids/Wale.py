"""Module containing the Wale Class.

This module defines the Wale class which represents a vertical column of stitches in a knitted structure, maintaining the sequence and relationships between loops in that column.
"""
from __future__ import annotations

from typing import Iterator, cast

from networkx import dfs_preorder_nodes

from knit_graphs._base_classes import _Base_Wale
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction


class Wale(_Base_Wale):
    """A data structure representing stitch relationships between loops in a vertical column of a knitted structure.

    A wale represents a vertical sequence of loops connected by stitch edges, forming a column in the knitted fabric.
    This class manages the sequential relationships between loops and tracks the pull directions of stitches within the wale.

    Attributes:
        first_loop (Loop | None): The first (bottom) loop in the wale sequence.
        last_loop (Loop | None): The last (top) loop in the wale sequence.
        stitches (DiGraph): Stores the directed graph of stitch connections within this wale.
    """

    def __init__(self, first_loop: Loop | None = None) -> None:
        """Initialize a wale optionally starting with a specified loop.

        Args:
            first_loop (Loop | None, optional): The initial loop to start the wale with. If provided, it will be added as both the first and last loop. Defaults to None.
        """
        super().__init__()
        self.first_loop: None | Loop = first_loop
        self.last_loop: None | Loop = None
        if isinstance(self.first_loop, Loop):
            self.add_loop_to_end(self.first_loop, pull_direction=None)

    def add_loop_to_end(self, loop: Loop, pull_direction: Pull_Direction | None = Pull_Direction.BtF) -> None:
        """Add a loop to the end (top) of the wale with the specified pull direction.

        Args:
            loop (Loop): The loop to add to the end of the wale.
            pull_direction (Pull_Direction | None, optional): The direction to pull the loop through its parent loop. Defaults to Pull_Direction.BtF. Can be None only for the first loop in the wale.
        """
        if self.last_loop is None:
            self.stitches.add_node(loop)
            self.first_loop = loop
            self.last_loop = loop
        else:
            assert isinstance(pull_direction, Pull_Direction)
            self.stitches.add_edge(self.last_loop, loop, pull_direction=pull_direction)
            self.last_loop = loop

    def add_loop_to_beginning(self, loop: Loop, pull_direction: Pull_Direction = Pull_Direction.BtF) -> None:
        """Add a loop to the beginning (bottom) of the wale with the specified pull direction.

        Args:
            loop (Loop): The loop to add to the beginning of the wale.
            pull_direction (Pull_Direction, optional): The direction to pull the existing first loop through this new loop. Defaults to Pull_Direction.BtF.
        """
        if self.first_loop is None:
            self.stitches.add_node(loop)
            self.first_loop = loop
            self.last_loop = loop
        else:
            self.stitches.add_edge(loop, self.first_loop, pull_direction=pull_direction)
            self.first_loop = loop

    def get_stitch_pull_direction(self, u: Loop, v: Loop) -> Pull_Direction:
        """Get the pull direction of the stitch edge between two loops in this wale.

        Args:
            u (Loop): The parent loop in the stitch connection.
            v (Loop): The child loop in the stitch connection.

        Returns:
            Pull_Direction: The pull direction of the stitch between loops u and v.
        """
        return cast(Pull_Direction, self.stitches.edges[u, v]["pull_direction"])

    def split_wale(self, split_loop: Loop) -> tuple[Wale, Wale | None]:
        """Split this wale at the specified loop into two separate wales.

        The split loop becomes the last loop of the first wale and the first loop of the second wale.

        Args:
            split_loop (Loop): The loop at which to split the wale. This loop will appear in both resulting wales.

        Returns:
            tuple[Wale, Wale | None]:
                A tuple containing:
                * The first wale (from start to split_loop). This will be the whole wale if the split_loop is not found.
                * The second wale (from split_loop to end). This will be None if the split_loop is not found.
        """
        first_wale = Wale(self.first_loop)
        growing_wale = first_wale
        found_loop = False
        for l in cast(list[Loop], self[1:]):
            if l is split_loop:
                growing_wale.add_loop_to_end(l, self.get_stitch_pull_direction(cast(Loop, growing_wale.last_loop), l))
                growing_wale = Wale(split_loop)
                found_loop = True
            else:
                growing_wale.add_loop_to_end(l, self.get_stitch_pull_direction(cast(Loop, growing_wale.last_loop), l))
        if not found_loop:
            return self, None
        return first_wale, growing_wale

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
        """Get the hash value of this wale based on its first loop.

        Returns:
            int: Hash value based on the first loop in this wale.
        """
        return hash(self.first_loop)

    def overlaps(self, other: Wale) -> bool:
        """Check if this wale has any loops in common with another wale.

        Args:
            other (Wale): The other wale to compare against for overlapping loops.

        Returns:
            bool: True if the other wale has any overlapping loop(s) with this wale, False otherwise.
        """
        return any(loop in other for loop in self)
