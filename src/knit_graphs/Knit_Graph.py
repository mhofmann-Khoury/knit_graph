"""The graph structure used to represent knitted objects"""
from __future__ import annotations

from typing import Any, cast

from knit_graphs._base_classes import _Base_Knit_Graph
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.artin_wale_braids.Loop_Braid_Graph import Loop_Braid_Graph
from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.artin_wale_braids.Wale_Group import Wale_Group
from knit_graphs.Course import Course
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn


class Knit_Graph(_Base_Knit_Graph):
    """
    A representation of knitted structures as connections between loops on yarns
    """

    def __init__(self) -> None:
        super().__init__()
        self.braid_graph: Loop_Braid_Graph = Loop_Braid_Graph()
        self._last_loop: None | Loop = None
        self.yarns: set[Yarn] = set()

    @property
    def last_loop(self) -> None | Loop:
        """
        :return: Last loop added to graph
        """
        return self._last_loop

    @property
    def has_loop(self) -> bool:
        """
        :return: True if graph has loops
        """
        return self.last_loop is not None

    def add_crossing(self, left_loop: Loop, right_loop: Loop, crossing_direction: Crossing_Direction) -> None:
        """
        Adds edge between loops with attribute of the crossing direction.
        :param left_loop: Loop on the left side of the crossing.
        :param right_loop: Loop on the right side of the crossing.
        :param crossing_direction: The crossing direction is (over, under, none) between loops.
        """
        self.braid_graph.add_crossing(left_loop, right_loop, crossing_direction)

    def add_loop(self, loop: Loop) -> None:
        """
        Adds a loop to the graph
        :param loop: the loop to be added in as a node in the graph
        """
        self.stitch_graph.add_node(loop)
        if loop.yarn not in self.yarns:
            self.add_yarn(cast(Yarn, loop.yarn))
        if self._last_loop is None or loop > self._last_loop:
            self._last_loop = loop

    def add_yarn(self, yarn: Yarn) -> None:
        """
        Adds a yarn to the graph. Assumes that loops do not need to be added
        :param yarn: the yarn to be added to the graph structure
        """
        self.yarns.add(yarn)

    def connect_loops(self, parent_loop: Loop, child_loop: Loop,
                      pull_direction: Pull_Direction = Pull_Direction.BtF,
                      stack_position: int | None = None) -> None:
        """
        Creates a stitch-edge by connecting a parent and child loop
        :param parent_loop: the id of the parent loop to connect to this child
        :param child_loop:  the id of the child loop to connect to the parent
        :param pull_direction: the direction the child is pulled through the parent
        :param stack_position: The position to insert the parent into, by default add on top of the stack
        """
        if parent_loop not in self:
            raise KeyError(f"parent loop {parent_loop} not in Knit Graph")
        if child_loop not in self:
            raise KeyError(f"child loop {parent_loop} not in Knit Graph")
        self.stitch_graph.add_edge(parent_loop, child_loop, pull_direction=pull_direction)
        child_loop.add_parent_loop(parent_loop, stack_position)

    def get_wale_starting_with_loop(self, first_loop: Loop) -> Wale:
        """
        :param first_loop:
        :return: A wale starting from given loop in knit graph.
        """
        wale = Wale(first_loop)
        cur_loop = first_loop
        while len(self.stitch_graph.successors(cur_loop)) == 1:
            cur_loop = [*self.stitch_graph.successors(cur_loop)][0]
            wale.add_loop_to_end(cur_loop, self.stitch_graph.edges[wale.last_loop, cur_loop]['pull_direction'])
        return wale

    def get_wales_ending_with_loop(self, last_loop: Loop) -> list[Wale]:
        """
        :param last_loop: last loop of joined set of wales
        :return: the set of wales that end at this loop, only multiple wales if this is a child of a decrease.
        """
        wales = []
        for top_stitch_parent in self.stitch_graph.predecessors(last_loop):
            wale = Wale(last_loop)
            wale.add_loop_to_beginning(top_stitch_parent, cast(Pull_Direction, self.get_pull_direction(top_stitch_parent, last_loop)))
            cur_loop = top_stitch_parent
            while len(cur_loop.parent_loops) == 1:  # stop at split for decrease or start of wale
                cur_loop = [*self.stitch_graph.predecessors(cur_loop)][0]
                wale.add_loop_to_beginning(cur_loop, cast(Pull_Direction, self.get_pull_direction(cur_loop, cast(Loop, wale.first_loop))))
            wales.append(wale)
        return wales

    def get_courses(self) -> list[Course]:
        """
        :return: A dictionary of loop_ids to the course they are on,
        a dictionary or course ids to the loops on that course in the order of creation.
        The first set of loops in the graph is on course 0.
        A course change occurs when a loop has a parent loop in the last course.
        """
        courses = []
        course = Course(self)
        for loop in sorted([*self.stitch_graph.nodes]):
            for parent in self.stitch_graph.predecessors(loop):
                if parent in course:  # start a new course
                    courses.append(course)
                    course = Course(self)
                    break
            course.add_loop(loop)
        courses.append(course)
        return courses

    def get_wale_groups(self) -> dict[Loop, Wale_Group]:
        """
        :return: Dictionary of terminal loops to the wale group they terminate
        """
        wale_groups = {}
        for loop in self.stitch_graph.nodes:
            if self.is_terminal_loop(loop):
                wale_groups.update({loop: Wale_Group(wale, self) for wale in self.get_wales_ending_with_loop(loop)})
        return wale_groups

    def __contains__(self, item: Loop) -> bool:
        """
        Returns true if the item is in the graph
        :param item: the loop being checked for in the graph
        :return: true if the loop_id of item or the loop is in the graph
        """
        return bool(self.stitch_graph.has_node(item))

    def get_pull_direction(self, parent: Loop, child: Loop) -> Pull_Direction | None:
        """
        Args:
            parent (Loop): The parent loop of the stitch edge.
            child (Loop): The child loop of the stitch edge.

        Returns:
            Pull_Direction | None: The pull direction of the stitch-edge between the parent and child or None if there is no edge between these loops.

        """
        edge = self.get_stitch_edge(parent, child)
        if edge is None:
            return None
        else:
            return cast(Pull_Direction, edge['pull_direction'])

    def get_stitch_edge(self, parent: Loop, child: Loop) -> dict[str, Any] | None:
        """
        Shortcut to get stitch-edge data from loops or ids
        :param parent: parent loop or id of parent loop
        :param child: child loop or id of child loop
        :return: the edge data for this stitch edge
        """
        if self.stitch_graph.has_edge(parent, child):
            return cast(dict[str, Any], self.stitch_graph.get_edge_data(parent, child))
        else:
            return None

    def get_child_loop(self, loop: Loop) -> Loop | None:
        """
        :param loop: loop_id to look for child from.
        :return: child loop_id or None if no child loop
        """
        successors = [*self.stitch_graph.successors(loop)]
        if len(successors) == 0:
            return None
        return cast(Loop, successors[0])

    def has_child_loop(self, loop: Loop) -> bool:
        """
        :param loop:
        :return: True if loop has a child loop
        """
        return self.get_child_loop(loop) is not None

    def is_terminal_loop(self, loop: Loop) -> bool:
        """
        :param loop:
        :return: True if loop has no child and terminates a wale.
        """
        return not self.has_child_loop(loop)
