"""Enumerator used to define the two pull-direction of a loop through other loops"""
from __future__ import annotations

from enum import Enum


class Pull_Direction(Enum):
    """An enumerator of the two pull-directions of a loop."""
    BtF = "Knit"
    FtB = "Purl"

    def opposite(self) -> Pull_Direction:
        """
        :return: returns the opposite pull direction of self
        """
        if self is Pull_Direction.BtF:
            return Pull_Direction.FtB
        else:
            return Pull_Direction.BtF

    def __neg__(self) -> Pull_Direction:
        return self.opposite()

    def __invert__(self) -> Pull_Direction:
        return self.opposite()

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)
