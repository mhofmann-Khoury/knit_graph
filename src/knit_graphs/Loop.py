"""Module containing the Loop Class"""


class Loop:
    """
    A class to represent a single loop structure for modeling a single loop in a knitting pattern.

    Attributes:
    -----------
    _loop_id : int
        a unique identifier for the loop
    yarn : Yarn
        the Yarn variable that creates and holds this loop
    parent_loops : list
        the list of parent loops
    front_floats : dict
        a dictionary of loops in front of the float
    back_floats : dict
        a dictionary of loops behind the float

    Methods:
    -----------
    add_loop_in_front_of_float(u, v)
        Set this loop to be in front of the float between u and v
    add_loop_behind_float(u, v)
        Set this loop to be behind the float between u and v
    is_in_front_of_float(u, v)
        Check if the float between u and v is in front of this loop
    is_behind_float(u, v)
        Check if the float between u and v is behind this loop
    prior_loop_on_yarn()
        Return the prior loop on yarn or None if first loop on yarn
    next_loop_on_yarn()
        Return the next loop on yarn or None if last loop on yarn
    has_parent_loops()
        Check if loop has stitch-edge parents
    add_parent_loop(parent, stack_position)
        Add the parent Loop onto the stack of parent_loops
    """

    def __init__(self, loop_id: int, yarn):
        """
        Constructs the Loop object.

        Parameters:
        -----------
        loop_id : int
            a unique identifier for the loop, must be non-negative
        yarn : Yarn
            the Yarn variable that creates and holds this loop
        """
        assert loop_id >= 0, f"{loop_id}: Loop_id must be non-negative"
        self._loop_id: int = loop_id
        self.yarn = yarn
        self.parent_loops: list[Loop] = []
        self.front_floats: dict[Loop, set[Loop]] = {}
        self.back_floats: dict[Loop, set[Loop]] = {}

    def add_loop_in_front_of_float(self, u, v):
        """
        Set this loop to be in front of the float between u and v
        :param u: First loop in float
        :param v: Second loop in float
        """
        if u not in self.back_floats:
            self.back_floats[u] = set()
        if v not in self.back_floats:
            self.back_floats[v] = set()
        self.back_floats[u].add(v)
        self.back_floats[v].add(u)

    def add_loop_behind_float(self, u, v):
        """
        Set this loop to be behind the float between u and v
        :param u: First loop in float
        :param v: Second loop in float
        """
        if u not in self.front_floats:
            self.front_floats[u] = set()
        if v not in self.front_floats:
            self.front_floats[v] = set()
        self.front_floats[u].add(v)
        self.front_floats[v].add(u)

    def is_in_front_of_float(self, u, v) -> bool:
        """
        :param u: First loop in float.
        :param v: Second loop in float.
        :return: True if the float between u and v is in front of this loop.
        """
        return u in self.back_floats and v in self.back_floats and v in self.back_floats[u]

    def is_behind_float(self, u, v) -> bool:
        """
        :param u: First loop in float.
        :param v: Second loop in float.
        :return: True if the float between u and v is behind this loop.
        """
        return u in self.front_floats and v in self.front_floats and v in self.front_floats[u]

    def prior_loop_on_yarn(self):
        """
        :return: Prior loop on yarn or None if first loop on yarn
        """
        return self.yarn.prior_loop(self)

    def next_loop_on_yarn(self):
        """
        :return: Next loop on yarn or Non if last loop on yarn
        """
        return self.yarn.next_loop(self)

    def has_parent_loops(self) -> bool:
        """
        :return: True if loop has stitch-edge parents
        """
        return len(self.parent_loops) > 0

    def add_parent_loop(self, parent, stack_position: int | None = None):
        """
        Adds the parent Loop onto the stack of parent_loops
        :param parent: the Loop to be added onto the stack
        :param stack_position: The position to insert the parent into, by default add on top of the stack
        """
        if stack_position is not None:
            self.parent_loops.insert(stack_position, parent)
        else:
            self.parent_loops.append(parent)

    @property
    def loop_id(self) -> int:
        """
        :return: the id of the loop
        """
        return self._loop_id

    def __hash__(self):
        return self.loop_id

    def __eq__(self, other):
        return isinstance(other, Loop) and self.loop_id == other.loop_id and self.yarn == other.yarn

    def __lt__(self, other):
        assert isinstance(other, Loop)
        return self.loop_id < other.loop_id

    def __gt__(self, other):
        assert isinstance(other, Loop)
        return self.loop_id > other.loop_id

    def __str__(self):
        return f"{self.loop_id} on yarn {self.yarn}"

    def __repr__(self):
        return str(self.loop_id)
