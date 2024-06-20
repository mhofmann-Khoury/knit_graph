"""
The Yarn Data Structure
"""
import networkx

from knit_graphs.Loop import Loop


class Yarn_Properties:
    """
        Class Structure for maintaining relevant data about a yarn
    """

    def __init__(self, name: str = "yarn", plies: int = 2, weight: float = 28, color=None):
        self.plies = plies
        self.name = name
        self.weight = weight
        if color is None:
            color = "green"
            # color = random.choice(matplotlib.colors.BASE_COLORS.items())
        self.color = color

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return f"{self.name}({self.plies}-{self.weight},{self.color})"

    def __repr__(self):
        return self.name

    @staticmethod
    def default_yarn():
        """
        :return: A default yarn to be used for development
        """
        return Yarn_Properties()


class Yarn:
    """
    A class to represent a yarn structure.
    Yarns are structured as a list of loops with a pointer to the last loop id
    """

    def __init__(self, yarn_properties: None | Yarn_Properties = None):
        """
        A Graph structure to show the yarn-wise relationship between loops
        :param yarn_properties:
        """
        if yarn_properties is None:
            yarn_properties = Yarn_Properties.default_yarn()
        self.properties: Yarn_Properties = yarn_properties
        self.loop_graph: networkx.DiGraph = networkx.DiGraph()
        self._first_loop: Loop | None = None
        self._last_loop: Loop | None = None

    def has_float(self, u: Loop, v: Loop) -> bool:
        """
        :param u: first loop
        :param v: second loop
        :return: True if there is a float edge between loops
        """
        return self.loop_graph.has_edge(u, v)

    def add_loop_in_front_of_float(self, front_loop: Loop, u: Loop, v: Loop):
        """
        Records front_loop falls in front of float between u and v.
        :param front_loop: loop in front of float.
        :param u: First loop in float.
        :param v: Second loop in float.
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                self.add_loop_in_front_of_float(front_loop, v, u)
            else:
                return
        self.loop_graph.edges[u, v]["Front_Loops"].add(front_loop)
        front_loop.add_loop_in_front_of_float(u, v)

    def add_loop_behind_float(self, back_loop: Loop, u: Loop, v: Loop):
        """
        Records back_loop falls behind the float between u and v
        :param back_loop: loop behind the float.
        :param u: First loop in float.
        :param v: Second loop in float.
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                self.add_loop_behind_float(back_loop, v, u)
            else:
                return
        self.loop_graph.edges[u, v]["Back_Loops"].add(back_loop)
        back_loop.add_loop_behind_float(u, v)

    def get_loops_in_front_of_float(self, u: Loop, v: Loop) -> set[Loop]:
        """
        :param u:
        :param v:
        :return: list of loops in front of float between u and v or empty if no float exists
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                return self.get_loops_in_front_of_float(v, u)
            else:
                return set()
        else:
            return self.loop_graph.edges[u, v]['Front_Loops']

    def get_loops_behind_float(self, u: Loop, v: Loop) -> set[Loop]:
        """
        :param u:
        :param v:
        :return: list of loops behind float between u and v or empty if no float exists
        """
        if not self.has_float(u, v):
            if self.has_float(v, u):
                return self.get_loops_behind_float(v, u)
            else:
                return set()
        else:
            return self.loop_graph.edges[u, v]['Back_Loops']

    @property
    def last_loop(self) -> Loop | None:
        """
        :return: Last loop id at the end of the yarn
        """
        return self._last_loop

    @property
    def first_loop(self) -> Loop | None:
        """
        :return: Last loop id at the end of the yarn
        """
        return self._first_loop

    @property
    def has_loops(self) -> bool:
        """
        :return: True if the yarn has loops on it
        """
        return self.last_loop is not None

    @property
    def yarn_id(self) -> str:
        """
        :return: the id of this yarn
        """
        return str(self.properties)

    def __str__(self):
        return self.yarn_id

    def __repr__(self):
        return repr(self.properties)

    def __hash__(self):
        return hash(self.properties)

    def __len__(self):
        return len(self.loop_graph.nodes)

    def make_loop_on_end(self, knit_graph=None) -> Loop:
        """
        Adds the loop at the end of the yarn.
        :param knit_graph: An optional Knit_Graph used to calculate last loop id in knitgraph.
        """
        loop_id = self._next_loop_id(knit_graph)
        loop = Loop(loop_id, self)
        return self.add_loop_to_end(knit_graph, loop)

    def _next_loop_id(self, knit_graph) -> int:
        if knit_graph is not None:
            if knit_graph.last_loop is None:
                loop_id = 0
            else:
                loop_id = knit_graph.last_loop.loop_id + 1
        else:
            loop_id = self.last_loop.loop_id + 1
        return loop_id

    def add_loop_to_end(self, knit_graph, loop: Loop):
        """
        :param knit_graph: knit graph that holds loop
        :param loop: Loop to be at end of yarn
        :return: Add loop to end of yarn and knit graph
        """
        self.insert_loop(loop, self._last_loop)
        if knit_graph is not None:
            knit_graph.add_loop(loop)
        return loop

    def insert_loop(self, loop: Loop, prior_loop: Loop | None = None):
        """
            Adds the loop at the end of the yarn.
            :param prior_loop: The loop that came before this on the yarn. Default to last loop added to end of yarn.
            :param loop: The loop to be added to this index. If none, a non-twisted loop will be created.
            """
        self.loop_graph.add_node(loop)
        if not self.has_loops:
            self._last_loop = loop
            self._first_loop = loop
            return
        elif prior_loop is None:
            prior_loop = self.last_loop
        self.loop_graph.add_edge(prior_loop, loop, Front_Loops=set(), Back_Loops=set())
        if prior_loop == self.last_loop:
            self._last_loop = loop

    def next_loop(self, loop: Loop) -> Loop | None:
        """
        :param loop: loop to index from. Will raise attribute error if not in yarn
        :return: Next loop on yarn after loop or None if last loop
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} is not on Yarn")
        successors = [*self.loop_graph.successors(loop)]
        if len(successors) > 0:
            return successors[0]
        else:
            return None

    def prior_loop(self, loop: Loop) -> Loop | None:
        """
        :param loop: loop to index from. Will raise attribute error if not in yarn
        :return: Prior loop on yarn before loop or None if first loop
        """
        if loop not in self:
            raise KeyError(f"Loop {loop} is not on Yarn")
        predecessors = [*self.loop_graph.predecessors(loop)]
        if len(predecessors) > 0:
            return predecessors[0]
        else:
            return None

    def __contains__(self, item: Loop):
        """
        Return true if the loop is on the yarn
        :param item: the loop being checked for in the yarn
        :return: true if the loop_id of item or the loop is in the yarn
        """
        return self.loop_graph.has_node(item)

    def __iter__(self):
        return networkx.dfs_preorder_nodes(self.loop_graph, self.first_loop)

    def edge_iter(self):
        """
        :return: Iterator over edges between loops on yarn.
        """
        return networkx.dfs_edges(self.loop_graph, self.first_loop)

    def loops_in_front_of_floats(self) -> list[tuple[Loop, Loop, set[Loop]]]:
        """
        :return: List of loops connecting floats and loops that are positioned in front of the float.
         Ignores floats with no loops in front of them.
        """
        return [(u, v, self.get_loops_in_front_of_float(u, v)) for u, v in self.edge_iter()
                if len(self.get_loops_in_front_of_float(u, v)) > 0]

    def loops_behind_floats(self) -> list[tuple[Loop, Loop, set[Loop]]]:
        """
        :return: List of loops connecting floats and loops that are positioned behind the float.
         Ignores floats with no loops behind them.
        """
        return [(u, v, self.get_loops_behind_float(u, v)) for u, v in self.edge_iter()
                if len(self.get_loops_behind_float(u, v)) > 0]

    def __getitem__(self, item: int) -> Loop:
        """
        Collect the loop of a given id
        :param item: the loop_id being checked for in the yarn
        :return: the Loop on the yarn with the matching id
        """
        if item not in self:
            raise AttributeError
        else:
            return self.loop_graph.nodes[item]
