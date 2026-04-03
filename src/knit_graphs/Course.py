"""Course representation of a section of knitting with no parent loops.

This module contains the Course class which represents a horizontal row of loops in a knitting pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from knit_graphs.course_face import Course_Face
from knit_graphs.Loop import Loop
from knit_graphs.loop_sequence import Loop_Sequence

if TYPE_CHECKING:
    from knit_graphs.Knit_Graph import Knit_Graph

LoopT = TypeVar("LoopT", bound=Loop)


class Course(Loop_Sequence[LoopT]):
    """Course object for organizing loops into knitting rows.

    A Course represents a horizontal row of loops in a knitting pattern.
    It maintains an ordered list of loops and provides methods for analyzing the structure and relationships between courses in the knitted fabric.
    """

    def __init__(self, course_number: int, knit_graph: Knit_Graph[LoopT]) -> None:
        """Initialize an empty course associated with a knit graph.

        Args:
            knit_graph (Knit_Graph): The knit graph that this course belongs to.
        """
        super().__init__()
        self._course_number: int = course_number
        self._knit_graph: Knit_Graph[LoopT] = knit_graph

    @property
    def course_number(self) -> int:
        """
        Returns:
            int: The course number of the course.
        """
        return self._course_number

    @property
    def knit_graph(self) -> Knit_Graph[LoopT]:
        """
        Returns:
            Knit_Graph: The knit graph that this course belongs to.
        """
        return self._knit_graph

    def add_loop(self, loop: LoopT, index: int | None = None) -> None:
        """Add a loop to the course at the specified index or at the end.

        Args:
            loop (Loop): The loop to add to this course.
            index (int | None, optional): The index position to insert the loop at. If None, appends to the end.

        Raises:
            ValueError: If the loop is a parent to any loops already in the course.
        """
        if not self.isdisjoint(loop.parent_loops):
            raise ValueError(f"{loop} has parent in course, cannot be added to same course")
        self._loop_set.add(loop)
        if index is None:
            self.loops_in_order.append(loop)
        else:
            self.loops_in_order.insert(index, loop)

    def in_round_with(self, next_course: Course[LoopT]) -> bool:
        """Check if the next course connects to this course in a circular pattern.

        This method determines if the courses are connected in the round (circular knitting) by checking if the next course starts at the beginning of this course.

        Args:
            next_course (Course): The course that should follow this course in circular knitting.

        Returns:
            bool: True if the next course starts at the beginning of this course, indicating circular knitting.
        """
        next_start = next_course[0]
        i = 1
        while not next_start.has_parent_loops:
            next_start = next_course[i]
            i += 1
        return self[0] in next_start.parent_loops

    def in_row_with(self, next_course: Course[LoopT]) -> bool:
        """Check if the next course connects to this course in a flat/row pattern.

        This method determines if the courses are connected in flat knitting (back and forth) by checking if the next course starts at the end of this course.

        Args:
            next_course (Course): The course that should follow this course in flat knitting.

        Returns:
            bool: True if the next course starts at the end of this course, indicating flat/row knitting.
        """
        next_start: LoopT = next_course[0]
        i = 1
        while not next_start.has_parent_loops:
            next_start = next_course[i]
            i += 1
        return self[-1] in next_start.parent_loops

    def get_faces(self) -> list[Course_Face[LoopT]]:
        """
        Returns:
            list[Course_Face[LoopT]]: A list of all faces that make up this course in the order that they occur in the course.
        """
        faces = []
        loop: LoopT | None = self[0]
        while loop is not None:
            face = Course_Face(loop, self)
            faces.append(face)
            loop = self.next_loop_in_sequence(face.last_index_in_course)
        return faces

    def __str__(self) -> str:
        """Get string representation of this course.

        Returns:
            str: String representation showing the ordered list of loops.
        """
        return f"Course {self.course_number}: {self.loops_in_order}"

    def __repr__(self) -> str:
        """Get string representation of this course for debugging.

        Returns:
            str: String representation showing the ordered list of loops.
        """
        return str(self)
