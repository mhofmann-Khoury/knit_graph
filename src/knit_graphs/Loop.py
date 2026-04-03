"""Module containing the Loop Class.

This module defines the Loop class which represents individual loops in a knitting pattern.
Loops are the fundamental building blocks of knitted structures and maintain relationships with parent loops, yarn connections, and float positions.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Self, cast

from knit_graphs.Pull_Direction import Pull_Direction

if TYPE_CHECKING:
    from knit_graphs.directed_loop_graph import Float_Edge
    from knit_graphs.Knit_Graph import Knit_Graph
    from knit_graphs.Yarn import Yarn


class Loop:
    """A class to represent a single loop structure for modeling a single loop in a knitting pattern.

    The Loop class manages yarn relationships, parent-child connections for stitches, and float positioning for complex knitting structures.
    Each loop maintains its position in the yarn sequence and its relationships to other loops through stitch connections and floating elements.

    Attributes:
        yarn (Yarn[Self]): The yarn that creates and holds this loop.
        parent_loops (list[Loop]): The list of parent loops that this loop is connected to through stitch edges.
    """

    def __init__(self, yarn: Yarn[Self], loop_id: int | None = None, **_kwargs: Any) -> None:
        """Construct a Loop object with the specified identifier and yarn.

        Args:
            yarn (Yarn[Self]): The yarn that creates and holds this loop.
            loop_id (int, optional): A unique identifier for the loop, must be non-negative. Defaults to the next id of the knitgraph that owns the given yarn.
        """
        self.yarn: Yarn[Self] = yarn
        self._knit_graph: Knit_Graph[Self] = yarn.knit_graph
        if loop_id is None:
            loop_id = 0 if self._knit_graph.last_loop is None else self._knit_graph.last_loop.loop_id + 1
        if loop_id < 0:
            raise ValueError(f"Loop identifier must be non-negative but got {loop_id}")
        self._loop_id: int = loop_id
        self.parent_loops: list[Self] = []

    @property
    def loop_id(self) -> int:
        """Get the unique identifier of this loop.

        Returns:
            int: The id of the loop.
        """
        return self._loop_id

    @property
    def has_parent_loops(self) -> bool:
        """Check if this loop has any parent loops connected through stitch edges.

        Returns:
            bool: True if the loop has stitch-edge parents, False otherwise.
        """
        return len(self.parent_loops) > 0

    @property
    def parent_loop_ids(self) -> list[int]:
        """
        Returns:
            list[int]: The ids of the parent loops of this loop in their stacking order.
        """
        return [p.loop_id for p in self.parent_loops]

    @property
    def pull_directions(self) -> list[Pull_Direction]:
        """
        Returns:
            list[Pull_Direction]: The pull direction of the stitches formed by this loop and its parents in stacking order of its parents.
        """
        return [self._knit_graph.get_pull_direction(p, cast(Self, self)) for p in self.parent_loops]

    @property
    def pull_direction(self) -> Pull_Direction:
        """
        Returns:
            Pull_Direction: The majority pull-direction of the stitches formed with the parent loops or Back-To-Front (knit-stitch) if this loop has no parents.
        """
        if not self.has_parent_loops:
            return Pull_Direction.BtF
        elif len(self.parent_loops) == 1:
            return self._knit_graph.get_pull_direction(self.parent_loops[0], cast(Self, self))
        else:
            knits = len([pd for pd in self.pull_directions if pd is Pull_Direction.BtF])
            purls = len(self.parent_loops) - knits
            return Pull_Direction.BtF if knits > purls else Pull_Direction.FtB

    @property
    def prior_loop_on_yarn(self) -> Self | None:
        """
        Returns:
            Loop | None: The prior loop on the yarn, or None if this is the first loop on the yarn.
        """
        return self.yarn.prior_loop(self)

    @property
    def next_loop_on_yarn(self) -> Self | None:
        """
        Returns:
            Loop | None: The next loop on the yarn, or None if this is the last loop on the yarn.
        """
        return self.yarn.next_loop(self)

    @property
    def started_float(self) -> Float_Edge[Self] | None:
        """
        Returns:
            Float_Edge | None: The float-edge connecting this loop to the next loop on its yarn or None if it is at the end of the yarn.
        """
        return self.yarn.following_float(self)

    @property
    def ended_float(self) -> Float_Edge[Self] | None:
        """
        Returns:
            Float_Edge | None: The float-edge connecting the prior loop on the yarn to this loop or None if it is at the beginning of the yarn.
        """
        return self.yarn.proceeding_float(self)

    @property
    def loops_in_front_of_floats(self) -> set[Self]:
        """
        Returns:
            set[Self]: The set of all loops in front of a float that involves this loop.
        """
        fronts = set()
        if self.started_float is not None:
            fronts.update(self.started_float.front_loops)
        if self.ended_float is not None:
            fronts.update(self.ended_float.front_loops)
        return fronts

    @property
    def loops_behind_floats(self) -> set[Self]:
        """
        Returns:
            set[Self]: The set of all loops behind a float that involves this loop.
        """
        backs = set()
        if self.started_float is not None:
            backs.update(self.started_float.back_loops)
        if self.ended_float is not None:
            backs.update(self.ended_float.back_loops)
        return backs

    @property
    def cross_floats(self) -> set[Self]:
        """
        Returns:
            set[Self]: The set of all loops that cross a float that involves this loop.
        """
        return self.loops_in_front_of_floats.union(self.loops_behind_floats)

    def is_in_front_of_float(self, u: Self, v: Self) -> bool:
        """
        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.

        Returns:
            bool: True if the float between u and v passes behind this loop, False otherwise.
        """
        if not u.yarn.has_float(u, v):
            return False
        return u.yarn.get_edge(u, v).loop_in_front_of_float(self)

    def is_behind_float(self, u: Self, v: Self) -> bool:
        """
        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.

        Returns:
            bool: True if the float between u and v passes in front of this loop, False otherwise.
        """
        if not u.yarn.has_float(u, v):
            return False
        return u.yarn.get_edge(u, v).loop_behind_float(self)

    @staticmethod
    def majority_pull_direction(loops: Sequence[Loop]) -> Pull_Direction:
        """
        Args:
            loops (Sequence[Loop]): The loops to find the majority pull direction of.

        Returns:
            Pull_Direction: The majority pull direction of the given loops or Back-to-Front (i.e., knit-stitch) there are no loops.
        """
        if len(loops) == 0:
            return Pull_Direction.BtF
        elif len(loops) == 1:
            return loops[0].pull_direction
        else:
            knits = len([l.pull_direction for l in loops if l.pull_direction is Pull_Direction.BtF])
            purls = len(loops) - knits
            return Pull_Direction.BtF if knits > purls else Pull_Direction.FtB

    def add_loop_behind_started_float(self, back_loop: Self) -> None:
        """
        Places the given loop behind the float started by this loop. If this loop is at the end of the yarn, nothing happens.

        Args:
            back_loop (Loop): The loop to place the loop behind the float started by this loop.
        """

        started_float = self.started_float
        if started_float is not None:
            started_float.add_loop_behind_float(back_loop)

    def add_loop_in_front_of_started_float(self, front_loop: Self) -> None:
        """
        Places the given loop in front of the float started by this loop. If this loop is at the end of the yarn, nothing happens.
        Args:
            front_loop (Loop): The loop to place the loop in front of the float started by this loop.
        """
        started_float = self.started_float
        if started_float is not None:
            started_float.add_loop_in_front_of_float(front_loop)

    def add_parent_loop(self, parent: Self, stack_position: int | None = None) -> None:
        """Add a parent loop to this loop's parent stack.

        Args:
            parent (Loop): The loop to be added as a parent to this loop.
            stack_position (int | None, optional): The position to insert the parent into the parent stack. If None, adds the parent on top of the stack. Defaults to None.
        """
        if stack_position is not None:
            self.parent_loops.insert(stack_position, parent)
        else:
            self.parent_loops.append(parent)

    def remove_parent(self, parent: Self) -> None:
        """
        Removes the given parent loop from the set of parents of this loop.
        If the given loop is not a parent of this loop, nothing happens.
        Args:
            parent (Loop): The parent loop to remove.
        """
        if parent in self.parent_loops:
            self.parent_loops.remove(parent)

    def __hash__(self) -> int:
        """Return hash value based on loop_id for use in sets and dictionaries.

        Returns:
            int: Hash value of the loop_id.
        """
        return self.loop_id

    def __int__(self) -> int:
        """Convert loop to integer representation using loop_id.

        Returns:
            int: The loop_id as an integer.
        """
        return self.loop_id

    def __eq__(self, other: object) -> bool:
        """Check equality with another base loop based on loop_id and type.

        Args:
            other (Self): The other loop to compare with.

        Returns:
            bool: True if both loops have the same class and loop_id, False otherwise.
        """
        return isinstance(other, type(self)) and self.loop_id == other.loop_id

    def __lt__(self, other: Loop | int) -> bool:
        """Compare loop_id with another loop or integer for ordering.

        Args:
            other (Loop | int): The other loop or integer to compare with.

        Returns:
            bool: True if this loop's id is less than the other's id.
        """
        return int(self.loop_id) < int(other)

    def __repr__(self) -> str:
        """Return string representation of the loop.

        Returns:
            str: String representation showing "Loop {loop_id}".
        """
        return f"Loop {self.loop_id}"
