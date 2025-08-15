"""Module containing the Wale_Group class and its methods.

This module provides the Wale_Group class which represents a collection of interconnected wales that are joined through decrease operations, forming a tree-like structure of vertical stitch columns.
"""
from __future__ import annotations

from typing import cast

from networkx import DiGraph, dfs_preorder_nodes

from knit_graphs._base_classes import _Base_Knit_Graph
from knit_graphs.artin_wale_braids.Wale import Wale
from knit_graphs.Loop import Loop


class Wale_Group:
    """A graph structure maintaining relationships between connected wales through decrease operations.

    This class represents a collection of wales that are connected through decrease stitches, where multiple wales merge into fewer wales as the knitting progresses upward.
    It maintains both the wale-to-wale relationships and the individual stitch connections within the group.

    Attributes:
        wale_graph (DiGraph): A directed graph representing the relationships between wales in this group.
        stitch_graph (DiGraph): A directed graph of all individual stitch connections within this wale group.
        terminal_wale (Wale | None): The topmost wale in this group, typically where multiple wales converge.
        top_loops (dict[Loop, Wale]): Mapping from the last (top) loop of each wale to the wale itself.
        bottom_loops (dict[Loop, Wale]): Mapping from the first (bottom) loop of each wale to the wale itself.
    """

    def __init__(self, terminal_wale: Wale, knit_graph: _Base_Knit_Graph):
        """Initialize a wale group starting from a terminal wale and building downward.

        Args:
            terminal_wale (Wale): The topmost wale in the group, used as the starting point for building the complete group structure.
            knit_graph (Knit_Graph): The parent knit graph that contains this wale group.
        """
        self.wale_graph: DiGraph = DiGraph()
        self.stitch_graph: DiGraph = DiGraph()
        self._knit_graph: _Base_Knit_Graph = knit_graph
        self.terminal_wale: Wale | None = terminal_wale
        self.top_loops: dict[Loop, Wale] = {}
        self.bottom_loops: dict[Loop, Wale] = {}
        self.build_group_from_top_wale(terminal_wale)

    def add_wale(self, wale: Wale) -> None:
        """Add a wale to the group and connect it to existing wales through shared loops.

        This method adds the wale to the group's graphs and establishes connections with other wales based on shared loops at their endpoints.

        Args:
            wale (Wale): The wale to add to this group. Empty wales are ignored and not added.
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
        """Find and add all parent wales that created the given wale through decrease operations.

        This method identifies wales that end at the loops that are parents of this wale's first loop, representing the wales that were decreased together to form the given wale.

        Args:
            wale (Wale): The wale to find and add parent wales for.

        Returns:
            list[Wale]: The list of parent wales that were found and added to the group.
        """
        added_wales = []
        for parent_loop in cast(Loop, wale.first_loop).parent_loops:
            parent_wales = cast(list[Wale], self._knit_graph.get_wales_ending_with_loop(parent_loop))
            for parent_wale in parent_wales:
                self.add_wale(parent_wale)
            added_wales.extend(parent_wales)
        return added_wales

    def build_group_from_top_wale(self, top_wale: Wale) -> None:
        """Build the complete wale group by recursively finding all parent wales from the terminal wale.

        This method starts with the terminal wale and recursively adds all parent wales, building the complete tree structure of wales that contribute to the terminal wale through decrease operations.

        Args:
            top_wale (Wale): The terminal wale at the top of the group structure.
        """
        self.add_wale(top_wale)
        added_wales = self.add_parent_wales(top_wale)
        while len(added_wales) > 0:
            next_wale = added_wales.pop()
            more_wales = self.add_parent_wales(next_wale)
            added_wales.extend(more_wales)

    def get_loops_over_courses(self) -> list[list[Loop]]:
        """Get loops organized by their course (horizontal row) within this wale group.

        This method traces through the stitch connections starting from the terminal wale's top loop and groups loops by their vertical position (course) in the knitted structure.

        Returns:
            list[list[Loop]]: A list where each inner list contains all loops that belong to the same course, ordered from top to bottom courses. Returns empty list if there is no terminal wale.
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
        """Get the height of the wale group measured as the maximum number of loops from base to terminal.

        This method calculates the total length by summing all loops in all wales that can be reached from each bottom wale, returning the maximum total length found.

        Returns:
            int: The height of the wale group from the base loops to the tallest terminal, measured in total number of loops.
        """
        max_len = 0
        for bot_loop, wale in self.bottom_loops.items():
            path_len = sum(len(successor) for successor in dfs_preorder_nodes(self.wale_graph, wale))
            max_len = max(max_len, path_len)
        return max_len
