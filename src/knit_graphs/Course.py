"""Course representation of a section of knitting with no parent loops."""
from __future__ import annotations

from typing import Iterator, cast

from knit_graphs._base_classes import _Base_Knit_Graph
from knit_graphs.Loop import Loop


class Course:
    """
    Course object for organizing loops into knitting rows
    """

    def __init__(self, _knit_graph: _Base_Knit_Graph) -> None:
        self.loops_in_order: list[Loop] = []
        self._loop_set: set[Loop] = set()

    def add_loop(self, loop: Loop, index: int | None = None) -> None:
        """
        Add the loop at the given index or to the end of the course
        :param loop: loop to add
        :param index: index to insert at or None if adding to end
        """
        for parent_loop in loop.parent_loops:
            assert parent_loop not in self, f"{loop} has parent {parent_loop}, cannot be added to same course"
        self._loop_set.add(loop)
        if index is None:
            self.loops_in_order.append(loop)
        else:
            self.loops_in_order.insert(index, loop)

    def has_increase(self) -> bool:
        """
        :return: True if course has at least one yarn over to start new wales.
        """
        return any(not loop.has_parent_loops() for loop in self)

    def has_decrease(self) -> bool:
        """
        :return: True if course has at least one decrease, merging two wales
        """
        return any(len(loop.parent_loops) > 1 for loop in self)

    def __getitem__(self, index: int | slice) -> Loop | list[Loop]:
        return self.loops_in_order[index]

    def in_round_with(self, next_course: Course) -> bool:
        """
        :param next_course: another course who should follow this course
        :return: True if the next course starts at the beginning of this course
        """
        next_start: Loop = cast(Loop, next_course[0])
        i = 1
        while not next_start.has_parent_loops():
            next_start = cast(Loop, next_course[i])
            i += 1
        return self[0] in next_start.parent_loops

    def in_row_with(self, next_course: Course) -> bool:
        """
        :param next_course: another course that should follow this course.
        :return: True if the next course starts at the end of this course.
        """
        next_start: Loop = cast(Loop, next_course[0])
        i = 1
        while not next_start.has_parent_loops():
            next_start = cast(Loop, next_course[i])
            i += 1
        return self[-1] in next_start.parent_loops

    def __contains__(self, loop: Loop) -> bool:
        return loop in self._loop_set

    def __iter__(self) -> Iterator[Loop]:
        return iter(self.loops_in_order)

    def __reversed__(self) -> Iterator[Loop]:
        return reversed(self.loops_in_order)

    def __len__(self) -> int:
        return len(self.loops_in_order)

    def __str__(self) -> str:
        return str(self.loops_in_order)

    def __repr__(self) -> str:
        return str(self)
