"""Module containing the Crossing_Direction Enum"""
from enum import Enum


class Crossing_Direction(Enum):
    """Enumeration of crossing values between loops"""
    Over_Right = "+"
    Under_Right = "-"
    No_Cross = "|"

    def __invert__(self):
        if self is Crossing_Direction.Over_Right:
            return Crossing_Direction.Under_Right
        else:
            return Crossing_Direction.Over_Right
