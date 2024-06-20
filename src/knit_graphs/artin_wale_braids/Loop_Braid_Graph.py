"""Module containing the Loop Braid Graph class."""
import networkx

from knit_graphs.Loop import Loop
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction


class Loop_Braid_Graph:
    """
        Tracks crossing braid edges between loops
    """

    def __init__(self):
        self.loop_crossing_graph: networkx.DiGraph = networkx.DiGraph()

    def add_crossing(self, left_loop: Loop, right_loop: Loop, crossing_direction: Crossing_Direction):
        """
        Adds edge between loops with attribute of the crossing direction.
        :param left_loop: Loop on the left side of the crossing.
        :param right_loop: Loop on the right side of the crossing.
        :param crossing_direction: The crossing direction is (over, under, none) between loops.
        """
        self.loop_crossing_graph.add_edge(left_loop, right_loop, crossing=crossing_direction)

    def __contains__(self, item: Loop | tuple[Loop, Loop]):
        if isinstance(item, Loop):
            return item in self.loop_crossing_graph.nodes
        else:
            return self.loop_crossing_graph.has_edge(item[0], item[1])

    def left_crossing_loops(self, left_loop: Loop) -> list[Loop]:
        """
        :param left_loop: loop to left side of crossing
        :return: list of loops this crosses over on right side
        """
        if left_loop not in self:
            return []
        else:
            return [rl for rl in self.loop_crossing_graph.successors(left_loop)
                    if self.get_crossing(left_loop, rl) is not Crossing_Direction.No_Cross]

    def right_crossing_loops(self, right_loop: Loop) -> list[Loop]:
        """
        :param right_loop: The loop to find crossings with.
        :return: The list of loops that leftward cross the right loop.
        """
        if right_loop not in self:
            return []
        else:
            return [l for l in self.loop_crossing_graph.predecessors(right_loop)
                    if self.get_crossing(l, right_loop) is not Crossing_Direction.No_Cross]

    def get_crossing(self, left_loop: Loop, right_loop: Loop) -> Crossing_Direction:
        """
        Adds no-cross edge if no edge exists between loops
        :param left_loop: Loop on the left side of the crossing.
        :param right_loop: Loop on the right side of the crossing.
        :return: The crossing direction between left and right loop. Defaults to no crossing.
        """
        if not self.loop_crossing_graph.has_edge(left_loop, right_loop):
            self.add_crossing(left_loop, right_loop, Crossing_Direction.No_Cross)
        return self.loop_crossing_graph[left_loop][right_loop]['crossing']
