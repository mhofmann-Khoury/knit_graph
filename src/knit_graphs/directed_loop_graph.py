"""Module containing directed loop graph class"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Generic, TypeVar, cast, overload

from networkx import DiGraph, ancestors, dfs_edges, dfs_preorder_nodes, has_path

from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction

EdgeT = TypeVar("EdgeT")

LoopT = TypeVar("LoopT", bound=Loop)


class Directed_Loop_Graph(Generic[LoopT, EdgeT]):
    """
    Wrapper for networkx.DiGraphs with directed edges between loops (i.e., floats in yarns, stitches in knitgraph).
    """

    _DATA_ATTRIBUTE_NAME = "data"

    def __init__(self) -> None:
        self._loop_graph: DiGraph = DiGraph()
        self._loops_by_loop_id: dict[int, LoopT] = {}

    @property
    def loop_count(self) -> int:
        """
        Returns:
            int: The number of loops in the graph.
        """
        return len(self._loops_by_loop_id)

    @property
    def edge_count(self) -> int:
        """
        Returns:
            int: The number of edges in the graph.
        """
        return len(self._loop_graph.edges)

    @property
    def contains_loops(self) -> bool:
        """
        Returns:
            bool: True if the graph has at least one loop, False otherwise.
        """
        return len(self) > 0

    @property
    def sorted_loops(self) -> list[LoopT]:
        """
        Returns:
            list[Loop]: The list of loops in the graph sorted from the earliest formed loop to the latest formed loop.
        """
        return sorted(self)

    @property
    def edge_iter(self) -> Iterator[tuple[LoopT, LoopT, EdgeT]]:
        """
        Returns:
            Iterator[tuple[LoopT, LoopT, EdgeT]]: Iterator over the edges and edge-data in the graph.

        Notes:
            No guarantees about the order of the edges.
        """
        return iter((cast(LoopT, u), cast(LoopT, v), self.get_edge(u, v)) for u, v in self._loop_graph.edges)

    @property
    def terminal_loops(self) -> Iterator[LoopT]:
        """
        Returns:
            Iterator[Loop]: An iterator over all terminal loops in the graph.
        """
        return iter(loop for loop in self if self.is_terminal_loop(loop))

    def has_loop(self, loop: int | LoopT) -> bool:
        """
        Args:
            loop (int | LoopT): The loop or loop id to check for in the graph.

        Returns:
            bool: True if the loop id is in the graph. False, otherwise.
        """
        if isinstance(loop, int):
            return loop in self._loops_by_loop_id
        else:
            return bool(self._loop_graph.has_node(loop))

    def get_loop(self, loop_id: int) -> LoopT:
        """
        Args:
            loop_id (int): The loop id of the loop to get from the graph.

        Returns:
            LoopT: The loop node in the graph.
        """
        return self._loops_by_loop_id[loop_id]

    def successors(self, loop: int | LoopT) -> set[LoopT]:
        """
        Args:
            loop (int | LoopT): The loop to get the successors of from the graph.

        Returns:
            set[LoopT]: The successors of the loop.
        """
        if isinstance(loop, int):
            loop = self.get_loop(loop)
        return cast(set[LoopT], set(self._loop_graph.successors(loop)))

    def has_child_loop(self, loop: LoopT) -> bool:
        """
        Args:
            loop (Loop): The loop to check for child connections.

        Returns:
            bool: True if the loop has a child loop, False otherwise.
        """
        return len(self.successors(loop)) > 0

    def is_terminal_loop(self, loop: LoopT) -> bool:
        """
        Args:
            loop (LoopT): The loop to check for terminal status.

        Returns:
            bool: True if the loop has no child loops, False otherwise.
        """
        return not self.has_child_loop(loop)

    def get_child_loop(self, loop: LoopT) -> LoopT | None:
        """
        Args:
            loop (LoopT): The loop to look for a child loop from.

        Returns:
            LoopT | None: The child loop if one exists, or None if no child loop is found.
        """
        successors = self.successors(loop)
        if len(successors) == 0:
            return None
        return successors.pop()

    def predecessors(self, loop: int | LoopT) -> set[LoopT]:
        """
        Args:
            loop (int | LoopT): The loop to get the predecessors of from the graph.

        Returns:
            set[LoopT]: The successors of the loop.
        """
        if isinstance(loop, int):
            loop = self.get_loop(loop)
        return cast(set[LoopT], set(self._loop_graph.predecessors(loop)))

    def ancestors(self, loop: LoopT) -> set[LoopT]:
        """
        Args:
            loop (LoopT): The loop to get the ancestors of from the graph.

        Returns:
            set[LoopT]: The ancestors of the given loop.
        """
        return cast(set[LoopT], ancestors(self._loop_graph, loop))

    def is_descendant(self, ancestor: LoopT, descendant: LoopT) -> bool:
        """

        Args:
            ancestor (LoopT): The loop to check if it is an ancestor of the other loop.
            descendant (LoopT): The loop to check if it is a descendant of the other loop.

        Returns:
            bool: True if there is a directed path from the ancestor to the descendant, False otherwise.
        """
        return bool(has_path(self._loop_graph, ancestor, descendant))

    def source_loops(self, loop: LoopT) -> set[LoopT]:
        """
        Args:
            loop (LoopT): The loop to get the sources of.

        Returns:
            set[LoopT]: The source loops of the given loop. These are the loops that are the source of all ancestors to the given loop.
        """
        ancestor_loops = self.ancestors(loop)
        if len(ancestor_loops) == 0:
            return set()
        sources = set()
        while len(ancestor_loops) > 0:
            ancestor = ancestor_loops.pop()
            if len(ancestor_loops) == 0:
                sources.add(ancestor)
            elif not any(self.is_descendant(other, ancestor) for other in ancestor_loops):
                sources.add(ancestor)
                non_sources = {descendant for descendant in ancestor_loops if self.is_descendant(ancestor, descendant)}
                ancestor_loops.difference_update(non_sources)  # remove all ancestors that descend from the source.
        return sources

    def dfs_edges(self, loop: LoopT) -> Iterator[tuple[LoopT, LoopT]]:
        """
        Args:
            loop (LoopT): The loop to start iteration over edges from.

        Returns:
            The depth-first-search ordering of edges starting from the given loop.
        """
        return cast(Iterator[tuple[LoopT, LoopT]], dfs_edges(self._loop_graph, loop))

    def dfs_preorder_loops(self, loop: LoopT) -> Iterator[LoopT]:
        """
        Args:
            loop (LoopT): The loop to start iteration from.

        Returns:
            Iterator[LoopT]: The depth-first-search ordering of loops in the graph starting from the given loop.
        """
        return cast(Iterator[LoopT], dfs_preorder_nodes(self._loop_graph, loop))

    def has_edge(self, u: LoopT | int, v: LoopT | int) -> bool:
        """
        Args:
            u (LoopT | int): The loop or id of the first loop in the edge.
            v (LoopT | int): The loop or id of the second loop in the edge.

        Returns:
            bool: True if the graph has an edge from loop u to v. False, otherwise.
        """
        if not self.has_loop(u) or not self.has_loop(v):
            return False
        if isinstance(u, int):
            u = self.get_loop(u)
        if isinstance(v, int):
            v = self.get_loop(v)
        return bool(self._loop_graph.has_edge(u, v))

    def get_edge(self, u: LoopT | int, v: LoopT | int) -> EdgeT:
        """

        Args:
            u (LoopT | int): The loop or id of the first loop in the edge.
            v (LoopT | int): The loop or id of the second loop in the edge.

        Returns:
            EdgeT: The data about the edge from loop u to v.
        """
        return cast(EdgeT, self._loop_graph.edges[u, v][self._DATA_ATTRIBUTE_NAME])

    def add_loop(self, loop: LoopT) -> None:
        """Add the given loop to the loop graph.
        Args:
            loop (LoopT): The loop to add to the graph.
        """
        self._loop_graph.add_node(loop)
        self._loops_by_loop_id[loop.loop_id] = loop

    def remove_loop(self, loop: LoopT | int) -> None:
        """
        Remove the given loop from the graph.
        Args:
            loop (LoopT | int): The loop or id of the loop to remove.

        Raises:
            KeyError: The given loop does not exist in the graph.
        """
        if isinstance(loop, int):
            if loop not in self._loops_by_loop_id:
                raise KeyError(f"No loop with id {loop} in graph")
            loop = self._loops_by_loop_id[loop]
        if not self._loop_graph.has_node(loop):
            raise KeyError(f"No loop {loop} in graph")
        self._loop_graph.remove_node(loop)
        del self._loops_by_loop_id[loop.loop_id]

    def add_edge(self, u: LoopT | int, v: LoopT | int, edge_data: EdgeT) -> None:
        """
        Connect the given loop u to the loop v with the given edge data.
        Args:
            u (LoopT | int): The loop to connect to.
            v (LoopT | int): The loop to connect to.
            edge_data (EdgeT): The edge data to associate with the connection.

        Raises:
            KeyError: Either of the given loops does not exist in the graph.
        """
        if u not in self:
            raise KeyError(f"parent loop {u} is not in graph")
        if v not in self:
            raise KeyError(f"child loop {v} i not in graph")
        if isinstance(u, int):
            u = self.get_loop(u)
        if isinstance(v, int):
            v = self.get_loop(v)
        self._loop_graph.add_edge(u, v, data=edge_data)

    def remove_edge(self, u: LoopT | int, v: LoopT | int) -> None:
        """
        Removes the edge from loop u to the loop v from the graph.
        Args:
            u (LoopT | int): The loop to connect to.
            v (LoopT | int): The loop to connect to.

        Raises:
            KeyError: The given edge does not exist in the graph.
        """
        if (u, v) not in self:
            raise KeyError(f"Edge from {u} to {v} is not in graph")
        if isinstance(u, int):
            u = self.get_loop(u)
        if isinstance(v, int):
            v = self.get_loop(v)
        self._loop_graph.remove_edge(u, v)

    def __contains__(self, item: LoopT | int | tuple[LoopT | int, LoopT | int]) -> bool:
        """
        Args:
            item (LoopT | int | tuple[LoopT | int, LoopT | int]): The loop, loop-id, or a pair of loops in a directed edge to search for.

        Returns:
            bool: True if the graph contains the given loop or edge.
        """
        if isinstance(item, tuple):
            return self.has_edge(item[0], item[1])
        else:
            return self.has_loop(item)

    @overload
    def __getitem__(self, item: int) -> LoopT: ...

    @overload
    def __getitem__(self, item: tuple[LoopT | int, LoopT | int]) -> EdgeT: ...

    def __getitem__(self, item: int | tuple[LoopT | int, LoopT | int]) -> LoopT | EdgeT:
        """
        Args:
            item (int | tuple[LoopT | int, LoopT | int]): The id of the loop or the pair of loops that form an edge in the graph.

        Returns:
            LoopT: The loop associated with the given id.
            EdgeT: The edge data associated with the given pair of loops/ loop_ids.

        Raises:
            KeyError: The given loop or edge does not exist in the graph.
        """
        if item not in self:
            raise KeyError(f"{item} is not in graph")
        elif isinstance(item, int):
            return self.get_loop(item)
        else:
            return self.get_edge(item[0], item[1])

    def __iter__(self) -> Iterator[LoopT]:
        """
        Returns:
            Iterator[LoopT]: Iterator over all the loops in the graph.

        Notes:
            No guarantees about order of loops. Expected to be insertion order.
        """
        return iter(self._loops_by_loop_id.values())

    def __len__(self) -> int:
        """
        Returns:
            int: The number of loops in the graph.
        """
        return len(self._loops_by_loop_id)


@dataclass
class Stitch_Edge:
    """Common data about stitch edges."""

    pull_direction: Pull_Direction  # The direction of the stitch edge.


@dataclass
class Float_Edge(Generic[LoopT]):
    """The edge data for float edges between loops on a yarn."""

    front_loops: set[LoopT] = field(default_factory=set)  # The set of loops that sit in front of this float. Defaults to empty set.
    back_loops: set[LoopT] = field(default_factory=set)  # THe set of loops that sit behind this float. Defaults to the empty set.

    def loop_in_front_of_float(self, loop: LoopT) -> bool:
        """
        Args:
            loop (LoopT): The loop to find relative to this float.

        Returns:
            bool: True if the loop is in the front of the float.
        """
        return loop in self.front_loops

    def loop_behind_float(self, loop: LoopT) -> bool:
        """
        Args:
            loop (LoopT): The loop to find relative to this float.

        Returns:
            bool: True if the loop is behind the float.
        """
        return loop in self.front_loops

    def add_loop_in_front_of_float(self, loop: LoopT) -> None:
        """
        Adds the given loop to the set of loops in front of this float.
        If the loop was behind the float, it is swapped to be in front.
        Args:
            loop (LoopT): The loop to put in front of this float.
        """
        if loop in self.back_loops:
            self.back_loops.remove(loop)
        self.front_loops.add(loop)

    def add_loop_behind_float(self, back_loop: LoopT) -> None:
        """
        Adds the given loop to the set of loops behind this float.
        If the loop was in front of this float, it is swapped to be behind.
        Args:
            back_loop (LoopT): The loop to put behind this float.
        """
        if back_loop in self.front_loops:
            self.front_loops.remove(back_loop)
        self.back_loops.add(back_loop)

    def remove_loop_relative_to_floats(self, loop: LoopT) -> None:
        """
        Removes the given loop from the edge data (if present), noting that it is neither in front of nor behind the float.
        Args:
            loop (LoopT): The loop to remove.
        """
        if self.loop_in_front_of_float(loop):
            self.front_loops.remove(loop)
        elif self.loop_behind_float(loop):
            self.back_loops.remove(loop)

    def __contains__(self, item: LoopT) -> bool:
        """
        Args:
            item (LoopT): The loop to find relative to this float.

        Returns:
            bool: True if the loop is in front or behind this float.
        """
        return item in self.front_loops or item in self.back_loops
