"""Course representation of a section of knitting with no parent loops.

This module contains the Course class which represents a horizontal row of loops in a knitting pattern.
"""
from __future__ import annotations

from typing import Iterator, cast

from knit_graphs._base_classes import _Base_Knit_Graph
from knit_graphs.Loop import Loop


class Course:
    """Course object for organizing loops into knitting rows.

    A Course represents a horizontal row of loops in a knitting pattern.
    It maintains an ordered list of loops and provides methods for analyzing the structure and relationships between courses in the knitted fabric.
    """

    def __init__(self, _knit_graph: _Base_Knit_Graph) -> None:
        """Initialize an empty course associated with a knit graph.

        Args:
            _knit_graph (Knit_Graph): The knit graph that this course belongs to.
        """
        self.loops_in_order: list[Loop] = []
        self._loop_set: set[Loop] = set()

    def add_loop(self, loop: Loop, index: int | None = None) -> None:
        """Add a loop to the course at the specified index or at the end.

        Args:
            loop (Loop): The loop to add to this course.
            index (int | None, optional): The index position to insert the loop at. If None, appends to the end.
        """
        for parent_loop in loop.parent_loops:
            assert parent_loop not in self, f"{loop} has parent {parent_loop}, cannot be added to same course"
        self._loop_set.add(loop)
        if index is None:
            self.loops_in_order.append(loop)
        else:
            self.loops_in_order.insert(index, loop)

    def has_increase(self) -> bool:
        """Check if this course contains any yarn overs that start new wales.

        Returns:
            bool: True if the course has at least one yarn over (loop with no parent loops) to start new wales.
        """
        return any(not loop.has_parent_loops() for loop in self)

    def has_decrease(self) -> bool:
        """Check if this course contains any decrease stitches that merge wales.

        Returns:
            bool: True if the course has at least one decrease stitch (loop with multiple parent loops) merging two or more wales.
        """
        return any(len(loop.parent_loops) > 1 for loop in self)

    def __getitem__(self, index: int | slice) -> Loop | list[Loop]:
        """Get loop(s) at the specified index or slice.

        Args:
            index (int | slice): The index or slice to retrieve from the course.

        Returns:
            Loop | list[Loop]: The loop at the specified index, or list of loops for a slice.
        """
        return self.loops_in_order[index]

    def in_round_with(self, next_course: Course) -> bool:
        """Check if the next course connects to this course in a circular pattern.

        This method determines if the courses are connected in the round (circular knitting) by checking if the next course starts at the beginning of this course.

        Args:
            next_course (Course): The course that should follow this course in circular knitting.

        Returns:
            bool: True if the next course starts at the beginning of this course, indicating circular knitting.
        """
        next_start: Loop = cast(Loop, next_course[0])
        i = 1
        while not next_start.has_parent_loops():
            next_start = cast(Loop, next_course[i])
            i += 1
        return self[0] in next_start.parent_loops

    def in_row_with(self, next_course: Course) -> bool:
        """Check if the next course connects to this course in a flat/row pattern.

        This method determines if the courses are connected in flat knitting (back and forth) by checking if the next course starts at the end of this course.

        Args:
            next_course (Course): The course that should follow this course in flat knitting.

        Returns:
            bool: True if the next course starts at the end of this course, indicating flat/row knitting.
        """
        next_start: Loop = cast(Loop, next_course[0])
        i = 1
        while not next_start.has_parent_loops():
            next_start = cast(Loop, next_course[i])
            i += 1
        return self[-1] in next_start.parent_loops

    def __contains__(self, loop: Loop) -> bool:
        """Check if a loop is contained in this course.

        Args:
            loop (Loop): The loop to check for membership in this course.

        Returns:
            bool: True if the loop is in this course, False otherwise.
        """
        return loop in self._loop_set

    def __iter__(self) -> Iterator[Loop]:
        """Iterate over loops in this course in order.

        Returns:
            Iterator[Loop]: An iterator over the loops in this course in their natural order.
        """
        return iter(self.loops_in_order)

    def __reversed__(self) -> Iterator[Loop]:
        """Iterate over loops in this course in reverse order.

        Returns:
            Iterator[Loop]: An iterator over the loops in this course in reverse order.
        """
        return reversed(self.loops_in_order)

    def __len__(self) -> int:
        """Get the number of loops in this course.

        Returns:
            int: The total number of loops in this course.
        """
        return len(self.loops_in_order)

    def __str__(self) -> str:
        """Get string representation of this course.

        Returns:
            str: String representation showing the ordered list of loops.
        """
        return str(self.loops_in_order)

    def __repr__(self) -> str:
        """Get string representation of this course for debugging.

        Returns:
            str: String representation showing the ordered list of loops.
        """
        return str(self)
