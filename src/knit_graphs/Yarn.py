"""The Yarn Data Structure.

This module contains the Yarn class and Yarn_Properties dataclass which together represent the physical yarn used in knitting patterns.
The Yarn class manages the sequence of loops along a yarn and their floating relationships.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar, overload

from knit_graphs.directed_loop_graph import Directed_Loop_Graph, Float_Edge
from knit_graphs.Loop import Loop

if TYPE_CHECKING:
    from knit_graphs.Knit_Graph import Knit_Graph

LoopT = TypeVar("LoopT", bound=Loop)


@dataclass(frozen=True)
class Yarn_Properties:
    """Dataclass structure for maintaining relevant physical properties of a yarn.

    This frozen dataclass contains all the physical and visual properties that characterize a yarn, including its structure, weight, and appearance.
    """

    name: str = "yarn"  # name (str): The name or identifier for this yarn type.
    color: str = "green"  # color (str): The color of the yarn for visualization purposes.

    def __str__(self) -> str:
        """Get a formatted string representation of the yarn properties.

        Returns:
            str: String representation in format "name(plies-weight,color)".
        """
        return f"{self.name}({self.color})"

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

    def __eq__(self, other: object) -> bool:
        """Check equality with another Yarn_Properties instance.

        Args:
            other (Yarn_Properties): The other yarn properties to compare with.

        Returns:
            bool: True if all properties (name, plies, weight, color) are equal, False otherwise.
        """
        return isinstance(other, Yarn_Properties) and self.name == other.name and self.color == other.color

    def __hash__(self) -> int:
        """Get hash value for use in sets and dictionaries.

        Returns:
            int: Hash value based on all yarn properties.
        """
        return hash((self.name, self.color))


class Yarn(Directed_Loop_Graph[LoopT, Float_Edge[LoopT]]):
    """A class to represent a yarn structure as a sequence of connected loops.

    The Yarn class manages a directed graph of loops representing the physical yarn path through a knitted structure.
    It maintains the sequential order of loops and their floating relationships, providing methods for navigation and manipulation of the yarn structure.

    Attributes:
        properties (Yarn_Properties): The physical and visual properties of this yarn.
    """

    def __init__(
        self,
        loop_class: type[LoopT],
        yarn_properties: Yarn_Properties | None = None,
        knit_graph: Knit_Graph[LoopT] | None = None,
    ):
        """Initialize a yarn with the specified properties and optional knit graph association.

        Args:
            yarn_properties (None | Yarn_Properties, optional): The properties defining this yarn. If None, uses default properties. Defaults to standard properties.
            knit_graph (None | Knit_Graph, optional): The knit graph that will own this yarn. Can be None for standalone yarns. Defaults to None.
        """
        super().__init__()
        self._loop_class: type[LoopT] = loop_class
        if yarn_properties is None:
            yarn_properties = Yarn_Properties.default_yarn()
        self.properties: Yarn_Properties = yarn_properties
        self._first_loop: LoopT | None = None
        self._last_loop: LoopT | None = None
        self._knit_graph: Knit_Graph[LoopT] = knit_graph if knit_graph is not None else Knit_Graph[LoopT]()
        if self not in self.knit_graph.yarns:
            self.knit_graph.add_yarn(self)

    @property
    def knit_graph(self) -> Knit_Graph[LoopT]:
        """
        Returns:
            Knit_Graph | Knit_Graph: The knit graph that owns this yarn, or None if not associated with a graph.
        """
        return self._knit_graph

    @knit_graph.setter
    def knit_graph(self, knit_graph: Knit_Graph[LoopT]) -> None:
        """Set the knit graph that owns this yarn.

        Args:
            knit_graph (Knit_Graph): The knit graph to associate with this yarn.
        """
        self._knit_graph = knit_graph

    @property
    def last_loop(self) -> LoopT | None:
        """Get the most recently added loop at the end of the yarn.

        Returns:
            Loop | None: The last loop on this yarn, or None if no loops have been added.
        """
        return self._last_loop

    @property
    def first_loop(self) -> LoopT | None:
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

    @property
    def float_iter(self) -> Iterator[tuple[LoopT, LoopT]]:
        """
        Returns:
            Iterator[tuple[Loop, Loop]]: An iterator over tuples of connected loops representing the yarn path.
        """
        if self.first_loop is None:
            return iter([])
        return self.dfs_edges(self.first_loop)

    def loops_in_front_of_floats(self) -> Iterator[tuple[LoopT, LoopT, set[LoopT]]]:
        """Get all float segments with loops positioned in front of them.

        Returns:
            list[tuple[Loop, Loop, set[Loop]]]: List of tuples containing the two loops defining each float and the set of loops positioned in front of that float.
            Only includes floats that have loops in front of them.
        """
        return ((u, v, d.front_loops) for u, v, d in self.edge_iter if len(d.front_loops) > 0)

    def loops_behind_floats(self) -> Iterator[tuple[LoopT, LoopT, set[LoopT]]]:
        """Get all float segments with loops positioned behind them.

        Returns:
            list[tuple[Loop, Loop, set[Loop]]]: List of tuples containing the two loops defining each float and the set of loops positioned behind that float.
            Only includes floats that have loops behind them.
        """
        return ((u, v, d.back_loops) for u, v, d in self.edge_iter if len(d.back_loops) > 0)

    def _next_loop_id(self) -> int:
        """
        Returns:
            int: The ID of the next loop to be added to this yarn based on the knit graph or, if no knit graph is associated with this yarn, based on the last loop on this yarn.
        """
        if self.knit_graph.last_loop is None:
            return 0
        else:
            return self.knit_graph.last_loop.loop_id + 1

    def next_loop(self, loop: LoopT) -> LoopT | None:
        """
        Args:
            loop (LoopT): The loop to find the next loop from.

        Returns:
            LoopT | None: The next loop on yarn after the specified loop, or None if it's the last loop.

        Raises:
            KeyError: If the specified loop is not on this yarn.
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} is not on Yarn")
        successors = self.successors(loop)
        return successors.pop() if len(successors) > 0 else None

    def prior_loop(self, loop: LoopT) -> LoopT | None:
        """
        Args:
            loop (Loop): The loop to find the prior loop from.

        Returns:
            Loop | None: The prior loop on yarn before the specified loop, or None if it's the first loop.

        Raises:
            KeyError: If the specified loop is not on this yarn.
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} is not on Yarn")
        predecessors = self.predecessors(loop)
        if len(predecessors) > 0:
            return predecessors.pop()
        else:
            return None

    def has_float(self, u: LoopT, v: LoopT) -> bool:
        """Check if there is a float edge between two loops on this yarn.

        Args:
            u (Loop): The first loop to check for float connection.
            v (Loop): The second loop to check for float connection.

        Returns:
            bool: True if there is a float edge between the loops, False otherwise.
        """
        return bool(self.has_edge(u, v))

    def get_loops_in_front_of_float(self, u: LoopT, v: LoopT) -> set[LoopT]:
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
            return self.get_edge(u, v).front_loops

    def get_loops_behind_float(self, u: LoopT, v: LoopT) -> set[LoopT]:
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
            return self.get_edge(u, v).back_loops

    def make_loop_on_end(self) -> LoopT:
        """Create and add a new loop at the end of the yarn.

        Returns:
            Loop: The newly created loop that was added to the end of this yarn.
        """
        loop_id = self._next_loop_id()
        return self.add_loop_to_end(self._new_loop(loop_id))

    def _new_loop(self, loop_id: int) -> LoopT:
        """
        Args:
            loop_id (int): The loop id to create a new loop.

        Returns:
            LoopT: A loop on this yarn with the given id.
        """
        if self.first_loop is not None:
            return self.first_loop.__class__(loop_id, self, self.knit_graph)
        else:
            return self._loop_class(loop_id, self, self.knit_graph)

    def remove_loop(self, loop: LoopT | int) -> None:
        """
        Remove the given loop from the yarn.
        Reconnects any neighboring loops to form a new float with the positioned in-front-of or behind the original floats positioned accordingly.
        Resets the first_loop and last_loop properties if the removed loop was the tail of the yarn.
        Args:
            loop (LoopT): The loop to remove from the yarn.

        Raises:
            KeyError: The given loop does not exist in the yarn.
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} does not exist on yarn {self}.")
        elif isinstance(loop, int):
            loop = self[loop]
        prior_loop = self.prior_loop(loop)
        next_loop = self.next_loop(loop)
        if prior_loop is not None and next_loop is not None:  # Loop is between two floats to be merged.
            front_of_float_loops = self.get_loops_in_front_of_float(prior_loop, loop)
            front_of_float_loops.update(self.get_loops_in_front_of_float(loop, next_loop))
            back_of_float_loops = self.get_loops_behind_float(prior_loop, loop)
            back_of_float_loops.update(self.get_loops_behind_float(loop, next_loop))
            super().remove_loop(loop)
            self.add_edge(
                prior_loop,
                next_loop,
                Float_Edge[LoopT](front_loops=front_of_float_loops, back_loops=back_of_float_loops),
            )
            for front_loop in front_of_float_loops:
                front_loop.add_loop_in_front_of_float(prior_loop, next_loop)
            for back_loop in back_of_float_loops:
                back_loop.add_loop_behind_float(prior_loop, next_loop)
        else:
            super().remove_loop(loop)
            if next_loop is None:  # This was the last loop, make the prior loop the last loop.
                self._last_loop = prior_loop
            if prior_loop is None:  # This was the first loop, make the next loop the first loop.
                self._first_loop = next_loop

    def add_loop_to_end(self, loop: LoopT) -> LoopT:
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

    def insert_loop(self, loop: LoopT, prior_loop: LoopT | None = None) -> None:
        """Insert a loop into the yarn sequence after the specified prior loop.

        Args:
            loop (Loop): The loop to be added to this yarn.
            prior_loop (Loop | None): The loop that should come before this loop on the yarn. If None, defaults to the last loop (adding to end of yarn).
        """
        super().add_loop(loop)
        if self.last_loop is None:
            self._last_loop = loop
            self._first_loop = loop
            return
        if prior_loop is None:
            prior_loop = self.last_loop
        super().add_edge(prior_loop, loop, Float_Edge[LoopT]())
        if prior_loop == self.last_loop:
            self._last_loop = loop

    def add_loop_in_front_of_float(self, front_loop: LoopT, u: LoopT, v: LoopT) -> None:
        """Record that a loop falls in front of the float between two other loops.

        Args:
            front_loop (Loop): The loop that is positioned in front of the float.
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.
        """
        if not self.has_float(u, v) and self.has_float(v, u):
            self.add_loop_in_front_of_float(front_loop, v, u)
        else:
            self.get_edge(u, v).front_loops.add(front_loop)
            front_loop.add_loop_in_front_of_float(u, v)

    def remove_loop_relative_to_floats(self, loop: LoopT) -> None:
        """
        Removes the given loop from positions relative to floats along this yarn.
        Args:
            loop (LoopT): The loop to remove from positions relative to floats on this yarn.
        """
        for _u, _v, float_data in self.edge_iter:
            float_data.remove_loop_relative_to_floats(loop)

    def add_loop_behind_float(self, back_loop: LoopT, u: LoopT, v: LoopT) -> None:
        """Record that a loop falls behind the float between two other loops.

        Args:
            back_loop (Loop): The loop that is positioned behind the float.
            u (Loop): The first loop in the float pair.
            v (Loop): The second loop in the float pair.
        """
        if not self.has_float(u, v) and self.has_float(v, u):
            self.add_loop_behind_float(back_loop, v, u)
        else:
            self.get_edge(u, v).back_loops.add(back_loop)
            back_loop.add_loop_behind_float(u, v)

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

    def __iter__(self) -> Iterator[LoopT]:
        """Iterate over loops on this yarn in sequence from first to last.

        Returns:
            Iterator[Loop]: An iterator over the loops on this yarn in their natural sequence order.
        """
        if self.first_loop is None:
            return iter([])
        return self.dfs_preorder_loops(self.first_loop)

    @overload
    def __getitem__(self, item: int) -> LoopT: ...

    @overload
    def __getitem__(self, item: tuple[LoopT | int, LoopT | int]) -> Float_Edge[LoopT]: ...

    @overload
    def __getitem__(self, item: slice) -> list[LoopT]: ...

    def __getitem__(
        self, item: int | tuple[LoopT | int, LoopT | int] | slice
    ) -> LoopT | Float_Edge[LoopT] | list[LoopT]:
        """Get a loop by its ID from this yarn.

        Args:
            item (int | tuple[LoopT | int, LoopT | int] | slice):
                The loop ,loop ID, or float between two loops to retrieve from this yarn.
                If given a slice, it will retrieve the elements between the specified indices in the standard ordering of loops along the yarn.

        Returns:
            LoopT: The loop on the yarn with the matching ID.
            Float_Edge[LoopT]: The float data for the given pair of loops forming a float.
            list[LoopT]: The loops in the slice of the yarn based on their ordering along the yarn.

        Raises:
            KeyError: If the item is not found on this yarn.
        """
        if isinstance(item, slice):
            return list(self)[item]
        else:
            return super().__getitem__(item)
