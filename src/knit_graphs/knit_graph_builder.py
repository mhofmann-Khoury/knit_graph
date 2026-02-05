"""Module containing the Knit_Graph_Builder class."""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar, cast

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn, Yarn_Properties

LoopT = TypeVar("LoopT", bound=Loop)


class Knit_Graph_Builder(Generic[LoopT]):
    """A general framework for building Knit_Graphs from standard knitting operations."""

    def __init__(
        self,
        loop_class: type[LoopT] | None = None,
        yarn_class: type[Yarn[LoopT]] | None = None,
    ):
        self._loop_class: type[LoopT] = loop_class if loop_class is not None else cast(type[LoopT], Loop)
        self._yarn_class: type[Yarn[LoopT]] = yarn_class if yarn_class is not None else cast(type[Yarn[LoopT]], Yarn)
        self.knit_graph: Knit_Graph[LoopT] = Knit_Graph[LoopT]()
        self._first_yarn: Yarn[LoopT] | None = None

    def add_yarn(self, yarn_properties: Yarn_Properties | None = None, **yarn_kwargs: Any) -> Yarn[LoopT]:
        """
        Create and add a new yarn to the Knit_Graph with the given properties.
        Args:
            yarn_properties (Yarn_Properties, optional): The properties of the yarn. Defaults to standard yarn-properties.

        Returns:
            Yarn[LoopT]: The new yarn in the Knit_Graph.
        """
        yarn = self._new_yarn(yarn_properties, **yarn_kwargs)
        self.knit_graph.add_yarn(yarn)
        return yarn

    def cut_yarn(self, yarn: Yarn[LoopT]) -> Yarn[LoopT]:
        """Cut yarn to make it no longer active and create a new yarn instance of the same type.

        Returns:
            Yarn[LoopT]: New yarn of the same type after cutting this yarn.
        """
        cut_yarn = yarn.cut_yarn()
        self.knit_graph.add_yarn(cut_yarn)
        return cut_yarn

    @staticmethod
    def position_float(
        first_loop: LoopT,
        loops_behind_float: Sequence[LoopT] | None = None,
        loops_in_front_of_float: Sequence[LoopT] | None = None,
    ) -> None:
        """
        Position the float exiting the given loop relative to the given sets of loops.
        Args:
            first_loop (LoopT): First loop in the float to position.
            loops_behind_float (Sequence[LoopT]): The loops in front of the float to position.
            loops_in_front_of_float (Sequence[LoopT]): The loops behind the float to position.
        """
        if loops_behind_float is not None:
            for loop in loops_behind_float:
                first_loop.yarn.add_loop_behind_float(loop, first_loop)
        if loops_in_front_of_float is not None:
            for loop in loops_in_front_of_float:
                first_loop.yarn.add_loop_in_front_of_float(loop, first_loop)

    def tuck(self, yarn: Yarn[LoopT]) -> LoopT:
        """
        Forms a new loop at the end of the yarn with no parent loops.
        Args:
            yarn (Yarn[LoopT]): The yarn to form the loop from in the knitgraph.

        Returns:
            LoopT: The new loop formed by the tuck.
        """
        return self._add_loop(yarn)

    def knit(
        self, yarn: Yarn[LoopT], parent_loops: Sequence[LoopT], pull_direction: Pull_Direction | None = None
    ) -> LoopT:
        """
        Args:
            yarn (Yarn[LoopT]): The yarn to form the loop from in the knitgraph.
            parent_loops (Sequence[LoopT]): The parent loops of stitch in their stacking order.
            pull_direction (Pull_Direction, optional): Pull direction of the stitch. Defaults to the dominant pull direction of a loop or Back-to-front (i.e., knit-stitch) if the loop has no parents.
        Returns:
            LoopT: The new loop formed by the knit.
        """
        if pull_direction is None:
            pull_direction = Loop.majority_pull_direction(parent_loops)
        loop = self._add_loop(yarn)
        for parent in parent_loops:
            self.knit_graph.connect_loops(parent, loop, pull_direction)
        return loop

    def xfer(
        self,
        loop: LoopT,
        over_loops_to_right: Sequence[LoopT] | None = None,
        over_loops_to_left: Sequence[LoopT] | None = None,
        under_loops_to_right: Sequence[LoopT] | None = None,
        under_loops_to_left: Sequence[LoopT] | None = None,
    ) -> None:
        """
        Cross the given loop over neighboring loops in the braid graph.
        Args:
            loop (LoopT): The loop to cross over neighbors
            over_loops_to_right (Sequence[LoopT], optional): The loops to cross over to the right. Defaults to no loops.
            over_loops_to_left (Sequence[LoopT], optional): The loops to cross over to the left. Defaults to no loops.
            under_loops_to_right (Sequence[LoopT], optional): The loops to cross under to the right. Defaults to no loops.
            under_loops_to_left (Sequence[LoopT], optional): The loops to cross under to the left. Defaults to no loops.
        """
        if over_loops_to_right is not None:
            for right_loop in over_loops_to_right:
                self.knit_graph.braid_graph.add_crossing(loop, right_loop, Crossing_Direction.Over_Right)
        if under_loops_to_right is not None:
            for right_loop in under_loops_to_right:
                self.knit_graph.braid_graph.add_crossing(loop, right_loop, Crossing_Direction.Under_Right)
        if over_loops_to_left is not None:
            for left_loop in over_loops_to_left:
                self.knit_graph.braid_graph.add_crossing(left_loop, loop, Crossing_Direction.Under_Right)
        if under_loops_to_left is not None:
            for left_loop in under_loops_to_left:
                self.knit_graph.braid_graph.add_crossing(left_loop, loop, Crossing_Direction.Over_Right)

    def split(
        self,
        yarn: Yarn[LoopT],
        parent_loops: Sequence[LoopT],
        pull_direction: Pull_Direction | None = None,
        over_loops_to_right: Sequence[LoopT] | None = None,
        over_loops_to_left: Sequence[LoopT] | None = None,
        under_loops_to_right: Sequence[LoopT] | None = None,
        under_loops_to_left: Sequence[LoopT] | None = None,
    ) -> LoopT:
        """

        Args:
            yarn (Yarn[LoopT]): The yarn to form the loop from in the knitgraph.
            parent_loops (Sequence[LoopT]): The parent loops of stitch in their stacking order.
            pull_direction (Pull_Direction, optional): Pull direction of the stitch. Defaults to the dominant pull direction of a loop or Back-to-front (i.e., knit-stitch) if the loop has no parents.
            over_loops_to_right (Sequence[LoopT], optional): The loops to cross over to the right. Defaults to no loops.
            over_loops_to_left (Sequence[LoopT], optional): The loops to cross over to the left. Defaults to no loops.
            under_loops_to_right (Sequence[LoopT], optional): The loops to cross under to the right. Defaults to no loops.
            under_loops_to_left (Sequence[LoopT], optional): The loops to cross under to the left. Defaults to no loops.

        Returns:
            LoopT: The loop formed in the split.
        """
        if pull_direction is None:
            pull_direction = Loop.majority_pull_direction(parent_loops)
        for loop in parent_loops:
            self.xfer(loop, over_loops_to_right, over_loops_to_left, under_loops_to_right, under_loops_to_left)
        return self.knit(yarn, parent_loops, pull_direction)

    def _new_yarn(self, yarn_properties: Yarn_Properties | None = None, **yarn_kwargs: Any) -> Yarn[LoopT]:
        """
        Args:
            yarn_properties (Yarn_Properties, optional): The properties of the yarn. Defaults to standard yarn-properties.
            **yarn_kwargs (Any, optional): Additional keyword arguments for forming the yarn. Defaults to no keyword arguments.

        Returns:
            Yarn[LoopT]: The new yarn in the Knit_Graph.
        """
        if self._first_yarn is None:
            self._first_yarn = self._yarn_class(yarn_properties, self.knit_graph, loop_class=self._loop_class)
            return self._first_yarn
        else:
            return self._first_yarn.__class__(yarn_properties, self.knit_graph, loop_class=self._loop_class)

    def _add_loop(self, yarn: Yarn[LoopT]) -> LoopT:
        """
        Create a loop at the end of the given yarn and add it to the Knit_Graph.
        Args:
            yarn (Yarn[LoopT]): The yarn to form the loop from in the knitgraph.

        Returns:
            LoopT: The new loop in the Knit_Graph.
        """
        loop = yarn.make_loop_on_end()
        if yarn.knit_graph is not self.knit_graph:
            self.knit_graph.add_loop(loop)
        return loop
