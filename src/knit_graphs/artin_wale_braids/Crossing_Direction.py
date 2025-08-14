"""Module containing the Crossing_Direction Enum"""
from __future__ import annotations

from enum import Enum


class Crossing_Direction(Enum):
    """Enumeration of crossing values between loops"""
    Over_Right = "+"
    Under_Right = "-"
    No_Cross = "|"

    @property
    def opposite(self) -> Crossing_Direction:
        """
        Returns:
            Crossing_Direction: The opposite of this crossing direction.
            * The Over_Right and Under_Right crossing directions are opposed.
            * The No_Cross crossing direction is its own opposite.

        """
        if self is Crossing_Direction.Over_Right:
            return Crossing_Direction.Under_Right
        elif self is Crossing_Direction.Under_Right:
            return Crossing_Direction.Over_Right
        else:
            return Crossing_Direction.No_Cross

    def __invert__(self) -> Crossing_Direction:
        return self.opposite

    def __neg__(self) -> Crossing_Direction:
        return self.opposite

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.name)

    def __hash__(self) -> int:
        return hash(self.value)
