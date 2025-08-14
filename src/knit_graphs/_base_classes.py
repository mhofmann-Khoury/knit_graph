"""Private module containing base classes for Loops and Yarns. Used to resolve circular dependencies."""
from __future__ import annotations

from networkx import DiGraph


class _Base_Loop:
    def __init__(self, loop_id: int):
        assert loop_id >= 0, f"{loop_id}: Loop_id must be non-negative"
        self._loop_id: int = loop_id

    @property
    def loop_id(self) -> int:
        """
        :return: the id of the loop
        """
        return self._loop_id

    def __hash__(self) -> int:
        return self.loop_id

    def __int__(self) -> int:
        return self.loop_id

    def __eq__(self, other: _Base_Loop) -> bool:
        return isinstance(other, other.__class__) and self.loop_id == other.loop_id

    def __lt__(self, other: _Base_Loop | int) -> bool:
        return int(self.loop_id) < int(other)

    def __repr__(self) -> str:
        return f"Loop {self.loop_id}"


class _Base_Yarn:

    def __init__(self) -> None:
        self.loop_graph: DiGraph = DiGraph()

    def prior_loop(self, loop: _Base_Loop) -> _Base_Loop | None:
        """
        Args:
            loop (Loop): The loop to find the proceeding loop of.
        Returns:
            (None | Loop): The loop that proceeds the given loop on the yarn or None if there is no prior loop.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError("Implemented by base class")

    def next_loop(self, loop: _Base_Loop) -> _Base_Loop | None:
        """
        Args:
            loop (Loop): The loop to find the next loop of.
        Returns:
            (None | Loop): The loop that follows the given loop on the yarn or None if there is no prior loop.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.
        """
        raise NotImplementedError("Implemented by base class")


class _Base_Wale:
    def __init__(self) -> None:
        self.stitches: DiGraph = DiGraph()


class _Base_Knit_Graph:
    def __init__(self) -> None:
        self.stitch_graph: DiGraph = DiGraph()

    @property
    def last_loop(self) -> None | _Base_Loop:
        """

        Returns:
            (None | Loop): The last loop added to the graph or None if the graph contains no loops.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.

        """
        raise NotImplementedError("Implemented by base class")

    def add_loop(self, loop: _Base_Loop) -> None:
        """

        Returns:
            (None | Loop): The first loop added to the graph or None if the graph contains no loops.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.

        """
        raise NotImplementedError("Implemented by base class")

    def get_wales_ending_with_loop(self, last_loop: _Base_Loop) -> list[_Base_Wale]:
        """

        Args:
            last_loop (Loop): The loop terminating the list of wales to be returned.

        Returns:
            list[Wale]: The list of wales that end at the given loop. This will only be multiple wales if the loop is a child of a decrease stitch.

        Raises:
            NotImplementedError: This is an abstract base class which must be extended with the correct implementation.

        """
        raise NotImplementedError
