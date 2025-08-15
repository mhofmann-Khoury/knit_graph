"""Private module containing base classes for Loops and Yarns. Used to resolve circular dependencies."""
from __future__ import annotations

from networkx import DiGraph


class _Base_Loop:
    """Base class for Loop objects providing common functionality and interface.

    This class serves as a foundation for Loop implementations and helps resolve circular dependencies between modules. It provides basic loop identification and comparison functionality.
    """

    def __init__(self, loop_id: int):
        """Initialize a base loop with the given identifier.

        Args:
            loop_id (int): The unique identifier for this loop. Must be non-negative.
        """
        assert loop_id >= 0, f"{loop_id}: Loop_id must be non-negative"
        self._loop_id: int = loop_id

    @property
    def loop_id(self) -> int:
        """Get the unique identifier of this loop.

        Returns:
            int: The id of the loop.
        """
        return self._loop_id

    def __hash__(self) -> int:
        """Return hash value based on loop_id for use in sets and dictionaries.

        Returns:
            int: Hash value of the loop_id.
        """
        return self.loop_id

    def __int__(self) -> int:
        """Convert loop to integer representation using loop_id.

        Returns:
            int: The loop_id as an integer.
        """
        return self.loop_id

    def __eq__(self, other: _Base_Loop) -> bool:
        """Check equality with another base loop based on loop_id and type.

        Args:
            other (_Base_Loop): The other loop to compare with.

        Returns:
            bool: True if both loops have the same class and loop_id, False otherwise.
        """
        return isinstance(other, other.__class__) and self.loop_id == other.loop_id

    def __lt__(self, other: _Base_Loop | int) -> bool:
        """Compare loop_id with another loop or integer for ordering.

        Args:
            other (_Base_Loop | int): The other loop or integer to compare with.

        Returns:
            bool: True if this loop's id is less than the other's id.
        """
        return int(self.loop_id) < int(other)

    def __repr__(self) -> str:
        """Return string representation of the loop.

        Returns:
            str: String representation showing "Loop {loop_id}".
        """
        return f"Loop {self.loop_id}"


class _Base_Yarn:
    """Base class for Yarn objects providing common functionality and interface.

    This class serves as a foundation for Yarn implementations and helps resolve circular dependencies between modules. It maintains a directed graph structure for managing loop relationships.
    """

    def __init__(self) -> None:
        """Initialize a base yarn with an empty directed graph for loop relationships."""
        self.loop_graph: DiGraph = DiGraph()

    def prior_loop(self, loop: _Base_Loop) -> _Base_Loop | None:
        """Find the loop that precedes the given loop on this yarn.

        Args:
            loop (_Base_Loop): The loop to find the preceding loop of.

        Returns:
            _Base_Loop | None: The loop that precedes the given loop on the yarn, or None if there is no prior loop.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError("Implemented by base class")

    def next_loop(self, loop: _Base_Loop) -> _Base_Loop | None:
        """Find the loop that follows the given loop on this yarn.

        Args:
            loop (_Base_Loop): The loop to find the next loop of.

        Returns:
            _Base_Loop | None: The loop that follows the given loop on the yarn, or None if there is no next loop.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError("Implemented by base class")


class _Base_Wale:
    """Base class for Wale objects providing common functionality and interface.

    This class serves as a foundation for Wale implementations and maintains a directed graph structure for managing stitch relationships within a wale (vertical column of stitches).
    """

    def __init__(self) -> None:
        """Initialize a base wale with an empty directed graph for stitch relationships."""
        self.stitches: DiGraph = DiGraph()


class _Base_Knit_Graph:
    """Base class for Knit Graph objects providing common functionality and interface.

    This class serves as a foundation for Knit Graph implementations and maintains a directed graph structure for managing stitch relationships throughout the entire knitted structure.
    """

    def __init__(self) -> None:
        """Initialize a base knit graph with an empty directed graph for stitch relationships."""
        self.stitch_graph: DiGraph = DiGraph()

    @property
    def last_loop(self) -> None | _Base_Loop:
        """Get the most recently added loop in the graph.

        Returns:
            None | _Base_Loop: The last loop added to the graph, or None if the graph contains no loops.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError("Implemented by base class")

    def add_loop(self, loop: _Base_Loop) -> None:
        """Add a loop to the knit graph structure.

        Args:
            loop (_Base_Loop): The loop to add to the graph.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError("Implemented by base class")

    def get_wales_ending_with_loop(self, last_loop: _Base_Loop) -> list[_Base_Wale]:
        """Get all wales (vertical columns) that terminate at the specified loop.

        Args:
            last_loop (_Base_Loop): The loop terminating the list of wales to be returned.

        Returns:
            list[_Base_Wale]: The list of wales that end at the given loop. This will only be multiple wales if the loop is a child of a decrease stitch.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError
