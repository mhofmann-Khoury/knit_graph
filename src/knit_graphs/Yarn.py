"""The Yarn Data Structure.

This module contains the Yarn class and Yarn_Properties dataclass which together represent the physical yarn used in knitting patterns.
The Yarn class manages the sequence of loops along a yarn and their floating relationships.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, cast

from networkx import dfs_edges, dfs_preorder_nodes

from knit_graphs._base_classes import _Base_Knit_Graph, _Base_Yarn
from knit_graphs.Loop import Loop


@dataclass(frozen=True)
class Yarn_Properties:
    """Dataclass structure for maintaining relevant physical properties of a yarn.

    This frozen dataclass contains all the physical and visual properties that characterize a yarn, including its structure, weight, and appearance.
    """
    name: str = "yarn"  # name (str): The name or identifier for this yarn type.
    plies: int = 2  # plies (int): The number of individual strands twisted together to form the yarn.
    weight: float = 28  # weight (float): The weight category or thickness of the yarn.
    color: str = "green"  # color (str): The color of the yarn for visualization purposes.

    def __str__(self) -> str:
        """Get a formatted string representation of the yarn properties.

        Returns:
            str: String representation in format "name(plies-weight,color)".
        """
        return f"{self.name}({self.plies}-{self.weight},{self.color})"

    def __repr__(self) -> str:
        """Get the name of the yarn for debugging purposes.

        Returns:
            str: The name of the yarn.
        """
        return self.name

    @staticmethod
    def default_yarn() -> Yarn_Properties:
        """Create a default yarn properties instance.

        Returns:
            Yarn_Properties: A default yarn instance with standard properties.
        """
        return Yarn_Properties()

    def __eq__(self, other: Yarn_Properties) -> bool:
        """Check equality with another Yarn_Properties instance.

        Args:
            other (Yarn_Properties): The other yarn properties to compare with.

        Returns:
            bool: True if all properties (name, plies, weight, color) are equal, False otherwise.
        """
        return self.name == other.name and self.plies == other.plies and self.weight == other.weight and self.color == other.color

    def __hash__(self) -> int:
        """Get hash value for use in sets and dictionaries.

        Returns:
            int: Hash value based on all yarn properties.
        """
        return hash((self.name, self.plies, self.weight, self.color))


class Yarn(_Base_Yarn):
    """A class to represent a yarn structure as a sequence of connected loops.

    The Yarn class manages a directed graph of loops representing the physical yarn path through a knitted structure.
    It maintains the sequential order of loops and their floating relationships, providing methods for navigation and manipulation of the yarn structure.

    Attributes:
        properties (Yarn_Properties): The physical and visual properties of this yarn.
    """

    def __init__(self, yarn_properties: None | Yarn_Properties = None, knit_graph: None | _Base_Knit_Graph = None):
        """Initialize a yarn with the specified properties and optional knit graph association.

        Args:
            yarn_properties (None | Yarn_Properties, optional): The properties defining this yarn. If None, uses default properties. Defaults to standard properties.
            knit_graph (None | Knit_Graph, optional): The knit graph that will own this yarn. Can be None for standalone yarns. Defaults to None.
        """
        super().__init__()
        if yarn_properties is None:
            yarn_properties = Yarn_Properties.default_yarn()
        self.properties: Yarn_Properties = yarn_properties
        self._first_loop: Loop | None = None
        self._last_loop: Loop | None = None
        self._knit_graph: None | _Base_Knit_Graph = knit_graph

    @property
    def knit_graph(self) -> None | _Base_Knit_Graph:
        """Get the knit graph that owns this yarn.

        Returns:
            None | Knit_Graph: The knit graph that owns this yarn, or None if not associated with a graph.
        """
        return self._knit_graph

    @knit_graph.setter
    def knit_graph(self, knit_graph: _Base_Knit_Graph) -> None:
        """Set the knit graph that owns this yarn.

        Args:
            knit_graph (Knit_Graph): The knit graph to associate with this yarn.
        """
        self._knit_graph = knit_graph

    def has_float(self, u: Loop, v: Loop) -> bool:
        """Check if there is a float edge between two loops on this yarn.

        Args:
            u (Loop): The first loop to check for float connection.
            v (Loop): The second loop to check for float connection.

        Returns:
            bool: True if there is a float edge between the loops, False otherwise.
        """
        return bool(self.loop_graph.has_edge(u, v))

    def add_loop_in_front_of_float(self, front_loop: Loop, u: Loop, v: Loop) -> None:
        """Record that a loop falls in front of the float between two other loops.

        Args:
            front_loop (Loop): The loop that is positioned in front of the float.
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                self.add_loop_in_front_of_float(front_loop, v, u)
            else:
                return
        self.loop_graph.edges[u, v]["Front_Loops"].add(front_loop)
        front_loop.add_loop_in_front_of_float(u, v)

    def add_loop_behind_float(self, back_loop: Loop, u: Loop, v: Loop) -> None:
        """Record that a loop falls behind the float between two other loops.

        Args:
            back_loop (Loop): The loop that is positioned behind the float.
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                self.add_loop_behind_float(back_loop, v, u)
            else:
                return
        self.loop_graph.edges[u, v]["Back_Loops"].add(back_loop)
        back_loop.add_loop_behind_float(u, v)

    def get_loops_in_front_of_float(self, u: Loop, v: Loop) -> set[Loop]:
        """Get all loops positioned in front of the float between two loops.

        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.

        Returns:
            set[Loop]: Set of loops positioned in front of the float between u and v, or empty set if no float exists.
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                return self.get_loops_in_front_of_float(v, u)
            else:
                return set()
        else:
            return cast(set[Loop], self.loop_graph.edges[u, v]['Front_Loops'])

    def get_loops_behind_float(self, u: Loop, v: Loop) -> set[Loop]:
        """Get all loops positioned behind the float between two loops.

        Args:
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.

        Returns:
            set[Loop]: Set of loops positioned behind the float between u and v, or empty set if no float exists.
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                return self.get_loops_behind_float(v, u)
            else:
                return set()
        else:
            return cast(set[Loop], self.loop_graph.edges[u, v]['Back_Loops'])

    @property
    def last_loop(self) -> Loop | None:
        """Get the most recently added loop at the end of the yarn.

        Returns:
            Loop | None: The last loop on this yarn, or None if no loops have been added.
        """
        return self._last_loop

    @property
    def first_loop(self) -> Loop | None:
        """Get the first loop at the beginning of the yarn.

        Returns:
            Loop | None: The first loop on this yarn, or None if no loops have been added.
        """
        return self._first_loop

    @property
    def has_loops(self) -> bool:
        """Check if the yarn has any loops on it.

        Returns:
            bool: True if the yarn has at least one loop, False otherwise.
        """
        return self.last_loop is not None

    @property
    def yarn_id(self) -> str:
        """Get the string identifier for this yarn.

        Returns:
            str: The string representation of the yarn properties.
        """
        return str(self.properties)

    def __str__(self) -> str:
        """Get the string representation of this yarn.

        Returns:
            str: The yarn identifier string.
        """
        return self.yarn_id

    def __repr__(self) -> str:
        """Get the representation string of this yarn for debugging.

        Returns:
            str: The representation of the yarn properties.
        """
        return repr(self.properties)

    def __hash__(self) -> int:
        """Get the hash value of this yarn for use in sets and dictionaries.

        Returns:
            int: Hash value based on the yarn properties.
        """
        return hash(self.properties)

    def __len__(self) -> int:
        """Get the number of loops on this yarn.

        Returns:
            int: The total number of loops on this yarn.
        """
        return len(self.loop_graph.nodes)

    def make_loop_on_end(self) -> Loop:
        """Create and add a new loop at the end of the yarn.

        Returns:
            Loop: The newly created loop that was added to the end of this yarn.
        """
        loop_id = self._next_loop_id()
        loop = Loop(loop_id, self)
        return self.add_loop_to_end(loop)

    def _next_loop_id(self) -> int:
        """Get the ID for the next loop to be added to this yarn.

        Returns:
            int: The ID of the next loop to be added to this yarn based on the knit graph or, if no knit graph is associated with this yarn, based on the last loop on this yarn.
        """
        if self.knit_graph is not None:
            if self.knit_graph.last_loop is None:
                return 0
            else:
                return self.knit_graph.last_loop.loop_id + 1
        elif self.last_loop is None:
            return 0
        else:
            return self.last_loop.loop_id + 1

    def add_loop_to_end(self, loop: Loop) -> Loop:
        """Add an existing loop to the end of this yarn and associated knit graph.

        Args:
            loop (Loop): The loop to be added at the end of this yarn.

        Returns:
            Loop: The loop that was added to the end of the yarn.
        """
        self.insert_loop(loop, self._last_loop)
        if self.knit_graph is not None:
            self.knit_graph.add_loop(loop)
        return loop

    def insert_loop(self, loop: Loop, prior_loop: Loop | None = None) -> None:
        """Insert a loop into the yarn sequence after the specified prior loop.

        Args:
            loop (Loop): The loop to be added to this yarn.
            prior_loop (Loop | None): The loop that should come before this loop on the yarn. If None, defaults to the last loop (adding to end of yarn).
        """
        self.loop_graph.add_node(loop)
        if not self.has_loops:
            self._last_loop = loop
            self._first_loop = loop
            return
        elif prior_loop is None:
            prior_loop = self.last_loop
        self.loop_graph.add_edge(prior_loop, loop, Front_Loops=set(), Back_Loops=set())
        if prior_loop == self.last_loop:
            self._last_loop = loop

    def next_loop(self, loop: Loop) -> Loop | None:
        """Get the loop that follows the specified loop on this yarn.

        Args:
            loop (Loop): The loop to find the next loop from.

        Returns:
            Loop | None: The next loop on yarn after the specified loop, or None if it's the last loop.

        Raises:
            KeyError: If the specified loop is not on this yarn.
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} is not on Yarn")
        successors = [*self.loop_graph.successors(loop)]
        if len(successors) > 0:
            return cast(Loop, successors[0])
        else:
            return None

    def prior_loop(self, loop: Loop) -> Loop | None:
        """Get the loop that precedes the specified loop on this yarn.

        Args:
            loop (Loop): The loop to find the prior loop from.

        Returns:
            Loop | None: The prior loop on yarn before the specified loop, or None if it's the first loop.

        Raises:
            KeyError: If the specified loop is not on this yarn.
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} is not on Yarn")
        predecessors = [*self.loop_graph.predecessors(loop)]
        if len(predecessors) > 0:
            return cast(Loop, predecessors[0])
        else:
            return None

    def __contains__(self, item: Loop | int) -> bool:
        """Check if a loop is contained on this yarn.

        Args:
            item (Loop | int): The loop or loop ID being checked for in the yarn.

        Returns:
            bool: True if the loop is on the yarn, False otherwise.
        """
        return bool(self.loop_graph.has_node(item))

    def __iter__(self) -> Iterator[Loop]:
        """Iterate over loops on this yarn in sequence from first to last.

        Returns:
            Iterator[Loop]: An iterator over the loops on this yarn in their natural sequence order.
        """
        return cast(Iterator[Loop], dfs_preorder_nodes(self.loop_graph, self.first_loop))

    def edge_iter(self) -> Iterator[tuple[Loop, Loop]]:
        """Iterate over the edges between loops on this yarn.

        Returns:
            Iterator[tuple[Loop, Loop]]: An iterator over tuples of connected loops representing the yarn path.
        """
        return cast(Iterator[tuple[Loop, Loop]], dfs_edges(self.loop_graph, self.first_loop))

    def loops_in_front_of_floats(self) -> list[tuple[Loop, Loop, set[Loop]]]:
        """Get all float segments with loops positioned in front of them.

        Returns:
            list[tuple[Loop, Loop, set[Loop]]]: List of tuples containing the two loops defining each float and the set of loops positioned in front of that float.
            Only includes floats that have loops in front of them.
        """
        return [(u, v, self.get_loops_in_front_of_float(u, v)) for u, v in self.edge_iter()
                if len(self.get_loops_in_front_of_float(u, v)) > 0]

    def loops_behind_floats(self) -> list[tuple[Loop, Loop, set[Loop]]]:
        """Get all float segments with loops positioned behind them.

        Returns:
            list[tuple[Loop, Loop, set[Loop]]]: List of tuples containing the two loops defining each float and the set of loops positioned behind that float.
            Only includes floats that have loops behind them.
        """
        return [(u, v, self.get_loops_behind_float(u, v)) for u, v in self.edge_iter()
                if len(self.get_loops_behind_float(u, v)) > 0]

    def __getitem__(self, item: int) -> Loop:
        """Get a loop by its ID from this yarn.

        Args:
            item (int): The loop ID to retrieve from this yarn.

        Returns:
            Loop: The loop on the yarn with the matching ID.

        Raises:
            KeyError: If the loop ID is not found on this yarn.
        """
        if item not in self:
            raise KeyError(f"{item} is not a loop on yarn {self}")
        else:
            return cast(Loop, self.loop_graph.nodes[item])
