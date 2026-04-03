"""Module containing the Course_Face class"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from knit_graphs.Loop import Loop
from knit_graphs.loop_sequence import Loop_Sequence

if TYPE_CHECKING:
    from knit_graphs.Course import Course
    from knit_graphs.Knit_Graph import Knit_Graph

LoopT = TypeVar("LoopT", bound=Loop)


class Course_Face(Loop_Sequence[LoopT]):
    """A series of loops in a common course that are on the same face of a knit structure.

    A face is a continuous series of loops where no floats cross other loops already in the face.
    """

    def __init__(self, first_loop: LoopT, parent_course: Course[LoopT]) -> None:
        if first_loop not in parent_course:
            raise ValueError(f"Loop {first_loop} is not in the course {parent_course}")
        if len(parent_course) == 0:
            raise ValueError(f"Parent course {parent_course} is empty and has no faces.")
        super().__init__()
        self._first_index_in_course: int = parent_course.index(first_loop)
        self._parent_course: Course[LoopT] = parent_course
        self._add_loop_to_sequence(first_loop)
        self._extend_face()

    @property
    def last_index_in_course(self) -> int:
        """
        Returns:
            int: The last index in the parent course of the last loop.
        """
        return self._first_index_in_course + (len(self) - 1)

    @property
    def course_number(self) -> int:
        """
        Returns:
            int: The course number of the course.
        """
        return self.parent_course.course_number

    @property
    def parent_course(self) -> Course[LoopT]:
        """
        Returns:
            Course[LoopT]: The course that owns this face.
        """
        return self._parent_course

    @property
    def is_full_course(self) -> bool:
        """
        Returns:
            bool: True if the face is its full parent course. False otherwise.
        """
        return len(self) == len(self.parent_course)

    @property
    def knit_graph(self) -> Knit_Graph[LoopT]:
        """
        Returns:
            Knit_Graph[LoopT]: The knitgraph that owns this face.
        """
        return self._parent_course.knit_graph

    def index_in_course(self, loop: int | LoopT) -> int:
        """
        Args:
            loop (int | LoopT): The index of the loop or the loop in this face.

        Returns:
            int: The index of the loop in the parent course.

        Raises:
            ValueError: If the loop is not a loop in this face.
        """
        if isinstance(loop, int):
            return self._first_index_in_course + loop
        if loop not in self:
            raise ValueError(f"Loop {loop} is not in {self}")
        return self._first_index_in_course + self._loops_in_order.index(loop)

    def _extend_face(self) -> None:
        """
        Working from the last loop in the face,
        extend the face until reaching the end of the parent course or reaching a loop that cross the face.
        """
        next_loop = self.parent_course.next_loop_in_sequence(self.last_index_in_course)

        while next_loop is not None and not self.loop_crosses_floats(next_loop):
            self._add_loop_to_sequence(next_loop)
            next_loop = self.parent_course.next_loop_in_sequence(self.last_index_in_course)

    def __str__(self) -> str:
        """
        Returns:
            str: String representation showing the ordered list of loops.
        """
        return f"Face in Course {self.course_number}: {self.loops_in_order}"

    def __repr__(self) -> str:
        """
        Returns:
            str: String representation showing the ordered list of loops.
        """
        return str(self)
