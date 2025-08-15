"""Module containing the Wale Braid Word Class.

This module provides the Wale_Braid_Word class which represents a single step in a braid operation, describing how loops cross over each other within a course of knitting.
"""
from __future__ import annotations

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Loop import Loop


class Wale_Braid_Word:
    """A representation of loop crossings over a set of loops in a common course.

    This class represents a single braid word in the mathematical sense, describing how a set of loops cross over or under each other within a horizontal course.
    Each braid word can be inverted and applied to determine the new ordering of loops after the crossing operations.

    Attributes:
        loops (list[Loop]): The ordered list of loops that participate in this braid word.
        crossings (dict[int, Crossing_Direction]): A mapping from loop indices to their crossing directions, where each key represents the index of a loop that crosses with the loop at index+1.
    """

    def __init__(self, loops: list[Loop], crossings: dict[int, Crossing_Direction]) -> None:
        """Initialize a wale braid word with the specified loops and crossing operations.

        Args:
            loops (list[Loop]): The ordered list of loops that participate in this braid word.
            crossings (dict[int, Crossing_Direction]): A dictionary mapping loop indices to crossing directions.
            Each index-key indicates that the loop at  that index crosses with the loop at index+1 in the specified direction.
        """
        self.loops: list[Loop] = loops
        self.crossings: dict[int, Crossing_Direction] = crossings

    def new_loop_order(self) -> list[Loop]:
        """Calculate the new ordering of loops after applying all crossing operations.

        This method applies all the crossing operations defined in this braid word to determine the final ordering of loops.
        Crossings are applied from right to left (highest index to lowest) to maintain proper braid semantics.

        Returns:
            list[Loop]: The list of loops in their new order after all crossing operations have been applied.
        """
        new_loops: list[Loop] = [*self.loops]
        for i in sorted(self.crossings.keys(), reverse=True):
            moves_left = new_loops[i + 1]
            new_loops[i + 1] = new_loops[i]
            new_loops[i] = moves_left

        return new_loops

    def __invert__(self) -> Wale_Braid_Word:
        """Create the inverse braid word that undoes the operations of this braid word.

        The inverse braid word uses the new loop order as its starting configuration and inverts all crossing directions to reverse the effect of the original braid word.

        Returns:
            Wale_Braid_Word: A new braid word that represents the inverse operation of this braid word.
        """
        new_loops = self.new_loop_order()
        new_crossings = {i: ~c for i, c in self.crossings.items()}
        return Wale_Braid_Word(new_loops, new_crossings)

    def __eq__(self, other: Wale_Braid_Word) -> bool:
        """Check equality with another wale braid word.

        Two braid words are equal if they have the same loops in the same order and the same crossing operations at the same indices.

        Args:
            other (Wale_Braid_Word): The other braid word to compare with.

        Returns:
            bool: True if both braid words have identical loops, loop ordering, and crossing operations, False otherwise.
        """
        if (len(self) != len(other)
                or any(l != o for l, o in zip(self.loops, other.loops))
                or any(i not in other.crossings for i in self.crossings)
                or any(other.crossings[i] != cd for i, cd in self.crossings.items())):
            return False
        else:
            return True

    def is_inversion(self, other: Wale_Braid_Word) -> bool:
        """Check if another braid word is the inverse of this braid word.

        Args:
            other (Wale_Braid_Word): The other braid word to compare against for inversion relationship.

        Returns:
            bool: True if the other braid word is equal to the inverse of this braid word, False otherwise.
        """
        invert = ~self
        return other == invert

    def __len__(self) -> int:
        """Get the number of loops in this braid word.

        Returns:
            int: The total number of loops participating in this braid word.
        """
        return len(self.loops)
