"""Module containing the Crossing_Direction Enum.

This module defines the Crossing_Direction enumeration which represents the different ways loops can cross over or under each other in cable knitting patterns.
"""
from __future__ import annotations

from enum import Enum


class Crossing_Direction(Enum):
    """Enumeration of crossing directions between loops in cable knitting patterns.

    This enumeration represents the three possible crossing relationships between loops: crossing over to the right, crossing under to the right, or no crossing at all.
    These directions are fundamental to representing cable structures in knitted fabrics.
    """
    Over_Right = "+"
    Under_Right = "-"
    No_Cross = "|"

    @property
    def opposite(self) -> Crossing_Direction:
        """Get the opposite crossing direction of this direction.

        The Over_Right and Under_Right crossing directions are opposites of each other, while No_Cross is its own opposite since there is no crossing to invert.

        Returns:
            Crossing_Direction: The opposite of this crossing direction. Over_Right returns Under_Right, Under_Right returns Over_Right, and No_Cross returns No_Cross.
        """
        if self is Crossing_Direction.Over_Right:
            return Crossing_Direction.Under_Right
        elif self is Crossing_Direction.Under_Right:
            return Crossing_Direction.Over_Right
        else:
            return Crossing_Direction.No_Cross

    def __invert__(self) -> Crossing_Direction:
        """Get the opposite crossing direction using the bitwise inversion operator.

        Returns:
            Crossing_Direction: The opposite crossing direction, same as calling the opposite property.
        """
        return self.opposite

    def __neg__(self) -> Crossing_Direction:
        """Get the opposite crossing direction using the negation operator.

        Returns:
            Crossing_Direction: The opposite crossing direction, same as calling the opposite property.
        """
        return self.opposite

    def __str__(self) -> str:
        """Get the string representation of the crossing direction.

        Returns:
            str: The symbol representing the crossing direction ("+", "-", or "|").
        """
        return str(self.value)

    def __repr__(self) -> str:
        """Get the representation string of the crossing direction for debugging.

        Returns:
            str: The name of the crossing direction ("Over_Right", "Under_Right", or "No_Cross").
        """
        return str(self.name)

    def __hash__(self) -> int:
        """Get the hash value of the crossing direction for use in sets and dictionaries.

        Returns:
            int: Hash value based on the crossing direction value.
        """
        return hash(self.value)
