"""Course representation of a section of knitting with no parent loops."""
from knit_graphs.Loop import Loop


class Course:
    """
    Course object for organizing loops into knitting rows
    """

    def __init__(self):
        self.loops_in_order: list[Loop] = []
        self._loop_set: dict[Loop, Loop] = {}

    def add_loop(self, loop: Loop, index: int | None = None):
        """
        Add the loop at the given index or to the end of the course
        :param loop: loop to add
        :param index: index to insert at or None if adding to end
        """
        for parent_loop in loop.parent_loops:
            assert parent_loop not in self, f"{loop} has parent {parent_loop}, cannot be added to same course"
        self._loop_set[loop] = loop
        if index is None:
            self.loops_in_order.append(loop)
        else:
            self.loops_in_order.insert(index, loop)

    def has_increase(self) -> bool:
        """
        :return: True if course has at least one yarn over to start new wales.
        """
        for loop in self:
            if not loop.has_parent_loops():  # Yarn over
                return True
        return False

    def has_decrease(self) -> bool:
        """
        :return: True if course has at least one decrease, merging two wales
        """
        for loop in self:
            if len(loop.parent_loops) > 1:
                return True
        return False

    def has_terminal_loop(self, knit_graph) -> bool:
        """\
        :param knit_graph: Knit graph to get child loop data from
        :return: True if this course contains a terminal loop with no child
        """
        for loop in self:
            if knit_graph.get_child_loop(loop) is None:
                return True
        return False

    def __getitem__(self, index: int | slice) -> Loop | list[Loop]:
        return self.loops_in_order[index]

    def index(self, loop: Loop) -> int:
        """
        Searches for index of given loop_id
        :param loop: loop_id or loop to find
        :return: index of the loop_id
        """
        return self.loops_in_order.index(loop)

    def in_round_with(self, next_course) -> bool:
        """
        :param next_course: another course who should follow this course
        :return: True if the next course starts at the beginning of this course
        """
        next_start = next_course[0]
        i = 1
        while not next_start.has_parent_loops():
            next_start = next_course[i]
            i += 1
        return self[0] in next_start.parent_loops

    def in_row_with(self, next_course) -> bool:
        """
        :param next_course: another course that should follow this course.
        :return: True if the next course starts at the end of this course.
        """
        next_start = next_course[0]
        i = 1
        while not next_start.has_parent_loops():
            next_start = next_course[i]
            i += 1
        return self[-1] in next_start.parent_loops

    def __contains__(self, loop: Loop) -> bool:
        return loop in self._loop_set

    def __iter__(self):
        return self.loops_in_order.__iter__()

    def __len__(self):
        return len(self.loops_in_order)

    def __str__(self):
        return str(self.loops_in_order)

    def __repr__(self):
        return str(self)
