"""Module containing the Wale_Group class and its methods.

This module provides the Wale_Group class which represents a collection of interconnected wales that are joined through decrease operations, forming a tree-like structure of vertical stitch columns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from networkx import DiGraph, dfs_preorder_nodes

from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.directed_loop_graph import Directed_Loop_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction

if TYPE_CHECKING:
    from knit_graphs.Knit_Graph import Knit_Graph

LoopT = TypeVar("LoopT", bound=Loop)


class Wale_Group(Directed_Loop_Graph[LoopT, Pull_Direction]):
    """A graph structure maintaining relationships between connected wales through decrease operations.

    This class represents a collection of wales that are connected through decrease stitches, where multiple wales merge into fewer wales as the knitting progresses upward.
    It maintains both the wale-to-wale relationships and the individual stitch connections within the group.

    Attributes:
        wale_graph (DiGraph): A directed graph representing the relationships between wales in this group.
        top_loops (dict[Loop, Wale]): Mapping from the last (top) loop of each wale to the wale itself.
        bottom_loops (dict[Loop, Wale]): Mapping from the first (bottom) loop of each wale to the wale itself.
    """

    def __init__(self, terminal_loop: LoopT, knit_graph: Knit_Graph[LoopT]):
        """Initialize a wale group starting from a terminal wale and building downward.

        Args:
            terminal_loop (Loop): The terminal loop of this wale-group. All the wales in the group connect up to this loop.
            knit_graph (Knit_Graph): The parent knit graph that contains this wale group.
        """
        super().__init__()
        self.wale_graph: DiGraph = DiGraph()
        self._knit_graph: Knit_Graph[LoopT] = knit_graph
        self._terminal_loop: LoopT = terminal_loop
        self.top_loops: dict[LoopT, Wale] = {}
        self.bottom_loops: dict[LoopT, Wale] = {}
        self._build_wale_group()

    @property
    def terminal_loop(self) -> LoopT:
        """
        Returns:
            LoopT: The loop that terminates all wales in this group.
        """
        return self._terminal_loop

    def get_loops_over_courses(self) -> list[list[LoopT]]:
        """Get loops organized by their course (horizontal row) within this wale group.

        This method traces through the stitch connections starting from the terminal wale's top loop and groups loops by their vertical position (course) in the knitted structure.

        Returns:
            list[list[LoopT]]: A list where each inner list contains all loops that belong to the same course, ordered from top to bottom courses. Returns empty list if there is no terminal wale.
        """
        courses: list[list[LoopT]] = []
        cur_course: list[LoopT] = [self._terminal_loop]
        while len(cur_course) > 0:
            courses.append(cur_course)
            next_course: list[LoopT] = []
            for loop in cur_course:
                next_course.extend(self.predecessors(loop))
            cur_course = next_course
        return courses

    def _build_wale_group(self) -> None:
        full_wales = self._knit_graph.get_wales_ending_with_loop(self._terminal_loop)
        # Build up the stitch graph.
        for wale in full_wales:
            u_loops = wale[:-1]
            v_loops = wale[1:]
            for u, v in zip(u_loops, v_loops, strict=False):
                if u not in self:
                    self.add_loop(u)
                if v not in self:
                    self.add_loop(v)
                self.add_edge(u, v, self._knit_graph.get_pull_direction(u, v))
        wales_to_split = full_wales
        while len(wales_to_split) > 0:
            wale_to_split = wales_to_split.pop()
            split = False
            upper_loops = wale_to_split[1:]
            for (
                loop
            ) in upper_loops:  # skip first loop in each wale as it may be already connected to a discovered decrease.
                if len(loop.parent_loops) > 1:  # Focal of a decrease.
                    clean_wale, remaining_wale = wale_to_split.split_wale(loop)
                    if not self.wale_graph.has_node(clean_wale):
                        self._add_wale(clean_wale)
                    if isinstance(remaining_wale, Wale):
                        wales_to_split.add(remaining_wale)
                    split = True
                    break
            if not split:
                self._add_wale(wale_to_split)
        for _bot_loop, lower_wale in self.bottom_loops.items():
            if lower_wale.last_loop in self.bottom_loops:
                self.wale_graph.add_edge(lower_wale, self.bottom_loops[lower_wale.last_loop])

    def _add_wale(self, wale: Wale) -> None:
        self.wale_graph.add_node(wale)
        self.top_loops[wale.last_loop] = wale
        self.bottom_loops[wale.first_loop] = wale

    def __len__(self) -> int:
        """Get the height of the wale group measured as the maximum number of loops from base to terminal.

        This method calculates the total length by summing all loops in all wales that can be reached from each bottom wale, returning the maximum total length found.

        Returns:
            int: The height of the wale group from the base loops to the tallest terminal, measured in total number of loops.
        """
        max_len = 0
        for _bot_loop, wale in self.bottom_loops.items():
            path_len = sum(len(successor) for successor in dfs_preorder_nodes(self.wale_graph, wale))
            max_len = max(max_len, path_len)
        return max_len

    def __hash__(self) -> int:
        """
        Returns:
            int: Hash value of the terminal loop of this group.
        """
        return hash(self._terminal_loop)

    def __contains__(self, item: LoopT | int | tuple[LoopT | int, LoopT | int] | Wale) -> bool:
        """
        Args:
            item (LoopT | int | tuple[LoopT | int, LoopT | int] | Wale): The item to check for in the wale group.

        Returns:
            bool: True if the given loop, loop_id (int), pair of loops, or wale is in this group.
        """
        if isinstance(item, Wale):
            return item in self.wale_graph
        else:
            return super().__contains__(item)

    def __str__(self) -> str:
        """
        Returns:
            str: The string representation of this wale group.
        """
        return f"WG({self.terminal_loop})"

    def __repr__(self) -> str:
        """
        Returns:
            str: The string representation of this wale group.
        """
        return str(self)
