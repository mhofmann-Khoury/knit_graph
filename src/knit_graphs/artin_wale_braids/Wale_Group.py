"""Module containing the Wale_Group class and its methods."""
import networkx

from knit_graphs.Loop import Loop
from knit_graphs.artin_wale_braids.Wale import Wale


class Wale_Group:
    """
        A graphs structure maintaining the relationship between connected wales through decreases
    """

    def __init__(self, terminal_wale: Wale, knit_graph):
        self.wale_graph: networkx.DiGraph = networkx.DiGraph()
        self.stitch_graph: networkx.DiGraph = networkx.DiGraph()
        self.terminal_wale: Wale | None = terminal_wale
        self.top_loops: dict[Loop, Wale] = {}
        self.bottom_loops: dict[Loop, Wale] = {}
        self.build_group_from_top_wale(terminal_wale, knit_graph)

    def add_wale(self, wale: Wale):
        """
        :param wale: Adds wale to group and connects by di-graph by position of shared loops.
        """
        self.wale_graph.add_node(wale)
        for u, v in wale.stitches.edges:
            self.stitch_graph.add_edge(u, v, pull_direction=wale.stitches.get_edge_data(u, v, "pull_direction"))
        for top_loop, other_wale in self.top_loops.items():
            if top_loop == wale.first_loop:
                self.wale_graph.add_edge(other_wale, wale)
        for bot_loop, other_wale in self.bottom_loops.items():
            if bot_loop == wale.last_loop:
                self.wale_graph.add_edge(wale, other_wale)
        self.top_loops[wale.last_loop] = wale
        self.bottom_loops[wale.first_loop] = wale

    def add_parent_wales(self, wale: Wale, knit_graph) -> list[Wale]:
        """
        Add parent wales that created the given wale to a wale group.
        :param wale: Wale to find parents from.
        :param knit_graph: Knit graph used to derive stitch relationships.
        :return: List of wales that were added.
        """
        added_wales = []
        for parent_loop in wale.first_loop.parent_loops:
            parent_wales = knit_graph.get_wales_ending_with_loop(parent_loop)
            for parent_wale in parent_wales:
                self.add_wale(parent_wale)
            added_wales.extend(parent_wales)
        return added_wales

    def build_group_from_top_wale(self, top_wale: Wale, knit_graph):
        """
        Builds out a wale group by finding parent wales from top wale provided
        :param top_wale: top of a wale tree.
        :param knit_graph: Knit graph used to derive stitch relationships.
        """
        self.add_wale(top_wale)
        added_wales = self.add_parent_wales(top_wale, knit_graph)
        while len(added_wales) > 0:
            next_wale = added_wales.pop()
            more_wales = self.add_parent_wales(next_wale, knit_graph)
            added_wales.extend(more_wales)

    def get_loops_over_courses(self) -> list[list[Loop]]:
        """
        :return: List of lists of loops that are in the same course by wales
        """
        top_loop = self.terminal_wale.last_loop
        courses = []
        cur_course = [top_loop]
        while len(cur_course) > 0:
            courses.append(cur_course)
            next_course = []
            for loop in cur_course:
                next_course.extend(self.stitch_graph.predecessors(loop))
            cur_course = next_course
        return courses

    def __len__(self):
        """
        :return: height of the wale group from base loop to the tallest terminal
        """
        max_len = 0
        for bot_loop, wale in self.bottom_loops.items():
            path_len = sum(len(successor) for successor in networkx.dfs_preorder_nodes(self.wale_graph, wale))
            max_len = max(max_len, path_len)
        return max_len
