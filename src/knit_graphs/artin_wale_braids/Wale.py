"""Module containing the Wale Class"""
import networkx

from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction


class Wale:
    """
        Data structure representing stitch relationships between loops in a knitted structure
    """

    def __init__(self, first_loop: None | Loop = None):
        self.stitches: networkx.DiGraph = networkx.DiGraph()
        self.first_loop: None | Loop = first_loop
        self.last_loop: None | Loop = first_loop

    def add_loop_to_end(self, loop: Loop, pull_direction: Pull_Direction = Pull_Direction.BtF):
        """
        Adds loop onto stitch graph with edge value of given pull_direction. Assumes loop comes after last loop.
        :param loop: Loop to add to the end of wale.
        :param pull_direction: Direction to pull loop through parent loop.
        """
        if self.last_loop is None:
            self.stitches.add_node(loop)
            self.first_loop = loop
            self.last_loop = loop
        else:
            self.stitches.add_edge(self.last_loop, loop, pull_direction=pull_direction)
            self.last_loop = loop

    def add_loop_to_beginning(self, loop: Loop, pull_direction: Pull_Direction = Pull_Direction.BtF):
        """
        Adds loop onto stitch graph with edge value of given pull_direction. Assumes loop comes before first loop.
        :param loop: Loop to add to the beginning of wale.
        :param pull_direction: Direction to pull loop through child loop.
        """
        if self.first_loop is None:
            self.stitches.add_node(loop)
            self.first_loop = loop
            self.last_loop = loop
        else:
            self.stitches.add_edge(loop, self.first_loop, pull_direction=pull_direction)
            self.first_loop = loop

    def get_stitch_pull_direction(self, u: Loop, v: Loop) -> Pull_Direction:
        """
        :param u:
        :param v:
        :return: The Pull direction of stitch between loops u and v
        """
        return self.stitches.edges[u, v]["pull_direction"]

    def split_wale(self, split_loop: Loop) -> tuple:
        """
        :param split_loop: loop to split at. Will be the first loop in the second wale and last loop in the first wale
        :return: tuple of wales or current wale and none if loop not found
        """
        first_wale = Wale(self.first_loop)
        growing_wale = first_wale
        found_loop = False
        for l in self[1:]:
            if l is split_loop:
                growing_wale.add_loop_to_end(l, self.get_stitch_pull_direction(growing_wale.last_loop, l))
                growing_wale = Wale(split_loop)
                found_loop = True
            else:
                growing_wale.add_loop_to_end(l, self.get_stitch_pull_direction(growing_wale.last_loop, l))
        if not found_loop:
            return self, None
        return first_wale, growing_wale

    def __len__(self):
        return len(self.stitches.nodes)

    def __iter__(self):
        return networkx.dfs_preorder_nodes(self.stitches, source=self.first_loop)

    def __contains__(self, item: Loop):
        return self.stitches.has_node(item)

    def __hash__(self):
        return hash(self.first_loop)

    def overlaps(self, other):
        """
        :param other: Wale to compare against.
        :return: True if the other wale has overlapping loop(s) with this wale.
        """
        for loop in self:
            if loop in other:
                return True
        return False
