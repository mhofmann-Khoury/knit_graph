"""Enumerator used to define the two pull-directions of a loop through other loops.

This module defines the Pull_Direction enumeration which represents the two ways a loop can be pulled through other loops in knitting: from back to front (knit) or from front to back (purl).
"""
from __future__ import annotations

from enum import Enum


class Pull_Direction(Enum):
    """An enumerator of the two pull-directions of a loop in knitting operations.

    This enumeration represents the two directions that yarn can be pulled through loops to create different stitch types.
    BtF (Back to Front) creates knit stitches, while FtB (Front to Back) creates purl stitches.
    """
    BtF = "Knit"
    FtB = "Purl"

    def opposite(self) -> Pull_Direction:
        """Get the opposite pull direction of this direction.

        Returns:
            Pull_Direction: The opposite pull direction. If this is BtF, returns FtB. If this is FtB, returns BtF.
        """
        if self is Pull_Direction.BtF:
            return Pull_Direction.FtB
        else:
            return Pull_Direction.BtF

    def __neg__(self) -> Pull_Direction:
        """Get the opposite pull direction using the negation operator.

        Returns:
            Pull_Direction: The opposite pull direction, same as calling opposite().
        """
        return self.opposite()

    def __invert__(self) -> Pull_Direction:
        """Get the opposite pull direction using the bitwise inversion operator.

        Returns:
            Pull_Direction: The opposite pull direction, same as calling opposite().
        """
        return self.opposite()

    def __str__(self) -> str:
        """Get the string representation of the pull direction.

        Returns:
            str: The value of the pull direction ("Knit" for BtF, "Purl" for FtB).
        """
        return str(self.value)

    def __repr__(self) -> str:
        """Get the representation string of the pull direction for debugging.

        Returns:
            str: The name of the pull direction ("BtF" or "FtB").
        """
        return self.name

    def __hash__(self) -> int:
        """Get the hash value of the pull direction for use in sets and dictionaries.

        Returns:
            int: Hash value based on the pull direction name.
        """
        return hash(self.name)
