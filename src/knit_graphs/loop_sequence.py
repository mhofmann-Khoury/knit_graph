"""Module containing the Loop Sequence class."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from typing import Generic, TypeVar, overload

from knit_graphs.directed_loop_graph import Float_Edge
from knit_graphs.Loop import Loop

LoopT = TypeVar("LoopT", bound=Loop)


class Loop_Sequence(Sequence[LoopT], Generic[LoopT]):
    """Generic class for a series of loops as in a course or a course-face"""

    def __init__(self) -> None:
        self._loops_in_order: list[LoopT] = []
        self._loop_set: set[LoopT] = set()

    @property
    def loops_in_order(self) -> list[LoopT]:
        """
        Returns:
            list[Loop]: The list of loops in this course.
        """
        return self._loops_in_order

    @property
    def loop_ids(self) -> list[int]:
        """
        Returns:
            list[int]: The loop ids in the course in the order they occur.
        """
        return [l.loop_id for l in self.loops_in_order]

    @property
    def has_increase(self) -> bool:
        """Check if this course contains any yarn overs that start new wales.

        Returns:
            bool: True if the course has at least one yarn over (loop with no parent loops) to start new wales.
        """
        return any(not loop.has_parent_loops for loop in self)

    @property
    def has_decrease(self) -> bool:
        """Check if this course contains any decrease stitches that merge wales.

        Returns:
            bool: True if the course has at least one decrease stitch (loop with multiple parent loops) merging two or more wales.
        """
        return any(len(loop.parent_loops) > 1 for loop in self)

    @property
    def floats(self) -> Iterator[Float_Edge[LoopT]]:
        """
        Returns:
            set[Float_Edge[LoopT]]: The set of yarn-floats between loops in this sequence.
        """
        for loop in self:
            f = self.following_float_in_sequence(loop)
            if f is not None:
                yield f

    @property
    def loops_in_front_of_floats(self) -> set[LoopT]:
        """
        Returns:
            set[LoopT]: The set of loops in front of at least one float in this sequence.
        """
        loops = set()
        for f in self.floats:
            loops.update(f.front_loops)
        return loops

    @property
    def loops_behind_floats(self) -> set[LoopT]:
        """
        Returns:
            set[LoopT]: The set of loops behind of at least one float in this sequence.
        """
        loops = set()
        for f in self.floats:
            loops.update(f.back_loops)
        return loops

    def loop_is_in_front(self, loop: LoopT) -> bool:
        """
        Args:
            loop (LoopT): The loop to check for.

        Returns:
            bool: True if the loop is in front of any float in this sequence.
        """
        return any(loop in f.front_loops for f in self.floats)

    def in_front_of_loops(self, other: Sequence[LoopT]) -> bool:
        """

        Args:
            other (Sequence[LoopT]): The series of loop to compare to.

        Returns:
            bool: True if all loops in the other series cross in front of a float in this series.
        """
        return all(l in self.loops_in_front_of_floats for l in other)

    def loop_is_behind(self, loop: LoopT) -> bool:
        """
        Args:
            loop (LoopT): The loop to check for.

        Returns:
            bool: True if the loop is behind any float in this sequence.
        """
        return any(loop in f.back_loops for f in self.floats)

    def behind_loops(self, other: Sequence[LoopT]) -> bool:
        """

        Args:
            other (Sequence[LoopT]): The series of loop to compare to.

        Returns:
            bool: True if all loops in the other series cross behind a float in this series.
        """
        return all(l in self.loops_behind_floats for l in other)

    def loop_crosses_floats(self, loop: LoopT) -> bool:
        """
        Args:
            loop [LoopT]: The loop to check for crossing floats.

        Returns:
            bool: True if the given loop crosses at least one float in this sequence.
        """
        return not loop.cross_floats.isdisjoint(self._loop_set)

    def tangled_with_loops(self, other: Sequence[LoopT]) -> bool:
        """
        Args:
            other (Sequence[LoopT]): The series of loop to compare to.

        Returns:
            bool: True if some loops in the given sequence fall in-front and others behind this sequence.
        """
        return any(self.loop_is_in_front(l) for l in other) and any(self.loop_is_behind(l) for l in other)

    def next_loop_in_sequence(self, loop: int | LoopT) -> LoopT | None:
        """
        Args:
            loop (int | LoopT): The index of the loop to find the following loop in the series or the loop to find the next loop in the series.

        Returns:
            LoopT | None: The loop that follows the given loop in this series or None if the given loop is the last loop in the series.

        Raises:
            ValueError: If the given loop is not a loop in the series.
        """
        if isinstance(loop, int):
            index = loop
        elif loop not in self:
            raise ValueError(f"Loop {loop} does not exist in {self}")
        else:
            index = self._loops_in_order.index(loop)
        if index + 1 < len(self):
            return self.loops_in_order[index + 1]
        else:
            return None

    def following_float_in_sequence(self, loop: int | LoopT) -> Float_Edge[LoopT] | None:
        """
        Args:
            loop (int | LoopT): The index of the loop to find the following float of or the loop to find the next loop in the series.

        Returns:
            Float_Edge[LoopT] | None:
                The float-edge initiated at the given loop and going to a loop in the sequence
                or None if there is no following loop along the yarn in this sequence.
        """
        if isinstance(loop, int):
            loop = self[loop]
        if loop.next_loop_on_yarn is None or loop.next_loop_on_yarn not in self:
            return None
        return loop.started_float

    def _add_loop_to_sequence(self, loop: LoopT, index: int | None = None) -> None:
        self._loop_set.add(loop)
        if index is None:
            self.loops_in_order.append(loop)
        else:
            self.loops_in_order.insert(index, loop)

    def __contains__(self, loop: object) -> bool:
        """O(1) membership test backed by the internal loop set.

        Args:
            loop (object): The object to test for membership.

        Returns:
            bool: True if loop is in this sequence, False otherwise.
        """
        return loop in self._loop_set

    @overload
    def __getitem__(self, index: int) -> LoopT: ...

    @overload
    def __getitem__(self, index: slice) -> list[LoopT]: ...

    def __getitem__(self, index: int | slice) -> LoopT | list[LoopT]:
        """
        Args:
            index (int | slice): The index or slice to retrieve.

        Returns:
            Loop | list[Loop]: The loop at the specified index, or list of loops for a slice.
        """
        return self.loops_in_order[index]

    def __iter__(self) -> Iterator[LoopT]:
        """
        Returns:
            Iterator[Loop]: An iterator over the loops in the series in their natural order.
        """
        return iter(self.loops_in_order)

    def __len__(self) -> int:
        """O(1) length backed by the internal loop set.

        Returns:
            int: The total number of loops in the series.
        """
        return len(self._loop_set)

    def __reversed__(self) -> Iterator[LoopT]:
        """Iterate over loops in reverse sequence order.

        Enables ``reversed(seq)`` and communicates that the sequence has a
        meaningful direction — relevant for knitting since course direction
        (e.g. left-to-right vs. right-to-left passes) matters structurally.

        Returns:
            Iterator[LoopT]: An iterator over the loops in reverse order.
        """
        return reversed(self._loops_in_order)

    def count(self, loop: object) -> int:
        """
        Args:
            loop (object): The object whose occurrences to count.

        Returns:
            int: The number of times loop appears in this sequence. 1 if loop is in this sequence, 0 otherwise.
        """
        return int(loop in self._loop_set)

    def isdisjoint(self, other: Iterable[LoopT]) -> bool:
        """
        Args:
            other (Iterable[LoopT]): The sequence to test against.

        Returns:
            bool: True if the two sequences have no loops in common.
        """
        return self._loop_set.isdisjoint(other)
