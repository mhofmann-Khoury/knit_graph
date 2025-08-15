"""Module containing the Loop Class.

This module defines the Loop class which represents individual loops in a knitting pattern.
Loops are the fundamental building blocks of knitted structures and maintain relationships with parent loops, yarn connections, and float positions.
"""
from __future__ import annotations

from typing import cast

from knit_graphs._base_classes import _Base_Loop, _Base_Yarn


class Loop(_Base_Loop):
    """A class to represent a single loop structure for modeling a single loop in a knitting pattern.

    The Loop class manages yarn relationships, parent-child connections for stitches, and float positioning for complex knitting structures.
    Each loop maintains its position in the yarn sequence and its relationships to other loops through stitch connections and floating elements.

    Attributes:
        yarn (Yarn): The yarn that creates and holds this loop.
        parent_loops (list[Loop]): The list of parent loops that this loop is connected to through stitch edges.
        front_floats (dict[Loop, set[Loop]]): A dictionary tracking loops that this loop floats in front of.
        back_floats (dict[Loop, set[Loop]]): A dictionary tracking loops that this loop floats behind.
    """

    def __init__(self, loop_id: int, yarn: _Base_Yarn) -> None:
        """Construct a Loop object with the specified identifier and yarn.

        Args:
            loop_id (int): A unique identifier for the loop, must be non-negative.
            yarn (_Base_Yarn): The yarn that creates and holds this loop.
        """
        super().__init__(loop_id)
        self.yarn: _Base_Yarn = yarn
        self.parent_loops: list[Loop] = []
        self.front_floats: dict[Loop, set[Loop]] = {}
        self.back_floats: dict[Loop, set[Loop]] = {}

    def add_loop_in_front_of_float(self, u: Loop, v: Loop) -> None:
        """Set this loop to be in front of the float between loops u and v.

        This method establishes that this loop passes in front of a floating yarn segment between two other loops.

        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.
        """
        if u not in self.back_floats:
            self.back_floats[u] = set()
        if v not in self.back_floats:
            self.back_floats[v] = set()
        self.back_floats[u].add(v)
        self.back_floats[v].add(u)

    def add_loop_behind_float(self, u: Loop, v: Loop) -> None:
        """Set this loop to be behind the float between loops u and v.

        This method establishes that this loop passes behind a floating yarn segment between two other loops.

        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.
        """
        if u not in self.front_floats:
            self.front_floats[u] = set()
        if v not in self.front_floats:
            self.front_floats[v] = set()
        self.front_floats[u].add(v)
        self.front_floats[v].add(u)

    def is_in_front_of_float(self, u: Loop, v: Loop) -> bool:
        """Check if this loop is positioned in front of the float between loops u and v.

        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.

        Returns:
            bool: True if the float between u and v passes behind this loop, False otherwise.
        """
        return u in self.back_floats and v in self.back_floats and v in self.back_floats[u]

    def is_behind_float(self, u: Loop, v: Loop) -> bool:
        """Check if this loop is positioned behind the float between loops u and v.

        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.

        Returns:
            bool: True if the float between u and v passes in front of this loop, False otherwise.
        """
        return u in self.front_floats and v in self.front_floats and v in self.front_floats[u]

    def prior_loop_on_yarn(self) -> Loop | None:
        """Get the loop that precedes this loop on the same yarn.

        Returns:
            Loop | None: The prior loop on the yarn, or None if this is the first loop on the yarn.
        """
        loop = self.yarn.prior_loop(self)
        if loop is None:
            return None
        else:
            return cast(Loop, loop)

    def next_loop_on_yarn(self) -> Loop:
        """Get the loop that follows this loop on the same yarn.

        Returns:
            Loop: The next loop on the yarn, or None if this is the last loop on the yarn.
        """
        return cast(Loop, self.yarn.next_loop(self))

    def has_parent_loops(self) -> bool:
        """Check if this loop has any parent loops connected through stitch edges.

        Returns:
            bool: True if the loop has stitch-edge parents, False otherwise.
        """
        return len(self.parent_loops) > 0

    def add_parent_loop(self, parent: Loop, stack_position: int | None = None) -> None:
        """Add a parent loop to this loop's parent stack.

        Args:
            parent (Loop): The loop to be added as a parent to this loop.
            stack_position (int | None, optional): The position to insert the parent into the parent stack. If None, adds the parent on top of the stack. Defaults to None.
        """
        if stack_position is not None:
            self.parent_loops.insert(stack_position, parent)
        else:
            self.parent_loops.append(parent)

    def __str__(self) -> str:
        """Get a string representation of this loop.

        Returns:
            str: String representation showing the loop ID and associated yarn.
        """
        return f"{self.loop_id} on yarn {self.yarn}"
