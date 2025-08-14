"""Module containing the Wale_Group class and its methods."""
from __future__ import annotations

from typing import cast

from networkx import DiGraph, dfs_preorder_nodes

from knit_graphs._base_classes import _Base_Knit_Graph
from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.Loop import Loop


class Wale_Group:
    """
        A graphs structure maintaining the relationship between connected wales through decreases
    """

    def __init__(self, terminal_wale: Wale, knit_graph: _Base_Knit_Graph):
        self.wale_graph: DiGraph = DiGraph()
        self.stitch_graph: DiGraph = DiGraph()
        self._knit_graph: _Base_Knit_Graph = knit_graph
        self.terminal_wale: Wale | None = terminal_wale
        self.top_loops: dict[Loop, Wale] = {}
        self.bottom_loops: dict[Loop, Wale] = {}
        self.build_group_from_top_wale(terminal_wale)

    def add_wale(self, wale: Wale) -> None:
        """
        :param wale: Adds wale to group and connects by di-graph by position of shared loops.
        """
        if len(wale) == 0:
            return  # This wale is empty and therefore there is nothing to add to the wale group
        self.wale_graph.add_node(wale)
        for u, v in wale.stitches.edges:
            self.stitch_graph.add_edge(u, v, pull_direction=wale.get_stitch_pull_direction(u, v))
        for top_loop, other_wale in self.top_loops.items():
            if top_loop == wale.first_loop:
                self.wale_graph.add_edge(other_wale, wale)
        for bot_loop, other_wale in self.bottom_loops.items():
            if bot_loop == wale.last_loop:
                self.wale_graph.add_edge(wale, other_wale)
        assert isinstance(wale.last_loop, Loop)
        self.top_loops[wale.last_loop] = wale
        assert isinstance(wale.first_loop, Loop)
        self.bottom_loops[wale.first_loop] = wale

    def add_parent_wales(self, wale: Wale) -> list[Wale]:
        """
        Add parent wales that created the given wale to a wale group.
        :param wale: Wale to find parents from.
        :return: List of wales that were added.
        """
        added_wales = []
        for parent_loop in cast(Loop, wale.first_loop).parent_loops:
            parent_wales = cast(list[Wale], self._knit_graph.get_wales_ending_with_loop(parent_loop))
            for parent_wale in parent_wales:
                self.add_wale(parent_wale)
            added_wales.extend(parent_wales)
        return added_wales

    def build_group_from_top_wale(self, top_wale: Wale) -> None:
        """
        Builds out a wale group by finding parent wales from top wale provided
        :param top_wale: top of a wale tree.
        """
        self.add_wale(top_wale)
        added_wales = self.add_parent_wales(top_wale)
        while len(added_wales) > 0:
            next_wale = added_wales.pop()
            more_wales = self.add_parent_wales(next_wale)
            added_wales.extend(more_wales)

    def get_loops_over_courses(self) -> list[list[Loop]]:
        """
        :return: List of lists of loops that are in the same course by wales
        """
        if self.terminal_wale is None:
            return []
        top_loop: Loop = cast(Loop, self.terminal_wale.last_loop)
        courses: list[list[Loop]] = []
        cur_course: list[Loop] = [top_loop]
        while len(cur_course) > 0:
            courses.append(cur_course)
            next_course = []
            for loop in cur_course:
                next_course.extend(self.stitch_graph.predecessors(loop))
            cur_course = next_course
        return courses

    def __len__(self) -> int:
        """
        :return: height of the wale group from base loop to the tallest terminal
        """
        max_len = 0
        for bot_loop, wale in self.bottom_loops.items():
            path_len = sum(len(successor) for successor in dfs_preorder_nodes(self.wale_graph, wale))
            max_len = max(max_len, path_len)
        return max_len
