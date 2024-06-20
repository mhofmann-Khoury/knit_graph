"""Module contianing the Wale Braid Word Class"""

from knit_graphs.Loop import Loop
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction


class Wale_Braid_Word:
    """
       Representation of loop crossings over a set of loops in a common course
    """
    def __init__(self, loops: list[Loop], crossings: dict[int, Crossing_Direction]):
        self.loops: list[Loop] = loops
        self.crossings: dict[int, Crossing_Direction] = crossings

    def new_loop_order(self) -> list[Loop]:
        """
        :return: list of loops in order that results from applying the crossing operations
        """
        new_loops: list[Loop] = [*self.loops]
        for i in sorted(self.crossings.keys(), reverse=True):
            moves_left = new_loops[i + 1]
            new_loops[i + 1] = new_loops[i]
            new_loops[i] = moves_left

        return new_loops

    def __invert__(self):
        new_loops = self.new_loop_order()
        new_crossings = {i: ~c for i, c in self.crossings.items()}
        return Wale_Braid_Word(new_loops, new_crossings)

    def __eq__(self, other):
        if not isinstance(other, Wale_Braid_Word):
            return False
        for l, o in zip(self.loops, other.loops):
            if l != o:
                return False
        for i, cd in self.crossings.items():
            if i not in other.crossings:
                return False
            if other.crossings[i] != cd:
                return False
        return True

    def is_inversion(self, other) -> bool:
        """
        :param other: other braid word to compare to
        :return: True if other is equal to inversion of self
        """
        invert = ~self
        return other == invert

    def __len__(self):
        return len(self.loops)
