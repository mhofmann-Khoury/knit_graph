"""Module of functions that generate basic knit graph swatches.

This module provides utility functions for creating common knitting patterns and structures as knit graphs.
These functions serve as building blocks for testing and demonstration purposes.
"""
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn


def co_loops(width: int) -> tuple[Knit_Graph, Yarn]:
    """Create a cast-on row of loops forming the foundation for knitting patterns.

    Args:
        width (int): The number of loops to create in the cast-on row.

    Returns:
        tuple[Knit_Graph, Yarn]: A tuple containing the knit graph with one course of the specified width and the yarn used to create it.
    """
    knit_graph = Knit_Graph()
    yarn = Yarn(knit_graph=knit_graph)
    for _ in range(0, width):
        _loop = yarn.make_loop_on_end()
    return knit_graph, yarn


def jersey_swatch(width: int, height: int) -> Knit_Graph:
    """Generate a rectangular knit swatch with all knit stitches in a flat sheet structure.

    This creates a basic stockinette/jersey pattern where all stitches are worked as knit stitches from back to front.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a flat rectangular swatch with all knit stitches.
    """
    knit_graph, yarn = co_loops(width)
    last_course = list(knit_graph.get_courses()[0])
    for _ in range(0, height):
        next_course = []
        for parent_loop in reversed(last_course):
            child_loop = yarn.make_loop_on_end()
            knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.BtF)
            next_course.append(child_loop)
        last_course = next_course
    return knit_graph


def jersey_tube(tube_width: int, height: int) -> Knit_Graph:
    """Generate a tubular knit structure with all knit stitches worked in the round.

    This creates a seamless tube by knitting in the round, where the front and back sections are connected by floats to maintain the circular structure.

    Args:
        tube_width (int): The number of stitches per course on the front side of the tube.
        height (int): The number of courses (vertical rows) in the tube.

    Returns:
        Knit_Graph: A knit graph representing a seamless tube with all knit stitches.
    """
    knit_graph, yarn = co_loops(tube_width * 2)
    last_course = [*knit_graph.get_courses()[0]]

    def _set_tube_floats() -> None:
        """Internal helper function to set up float connections between front and back of tube."""
        front_loops = last_course[0:tube_width]
        back_loops = last_course[tube_width:]
        for first_front, second_front, back in zip(front_loops[0:-1], front_loops[1:], reversed(back_loops)):
            yarn.add_loop_behind_float(back, first_front, second_front)
        for (first_back, second_back, front) in zip(back_loops[0:-1], back_loops[1:], reversed(front_loops)):
            yarn.add_loop_in_front_of_float(front, first_back, second_back)

    _set_tube_floats()
    for _ in range(0, height):
        next_course = [yarn.make_loop_on_end() for _p in last_course]
        for parent_loop, child_loop in zip(last_course, next_course):
            knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.BtF)
        last_course = next_course
        _set_tube_floats()
    return knit_graph


def kp_rib_swatch(width: int, height: int) -> Knit_Graph:
    """Generate a knit-purl ribbing swatch with alternating wales of knit and purl stitches.

    This creates a 1x1 ribbing pattern where knit and purl wales alternate, maintaining their stitch type throughout the height of the swatch for a stretchy, textured fabric.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a ribbed swatch with alternating knit and purl wales.
    """
    knit_graph, yarn = co_loops(width)
    last_course = knit_graph.get_courses()[0]
    next_course = []
    next_pull = Pull_Direction.BtF
    for parent_loop in reversed(last_course):
        child_loop = yarn.make_loop_on_end()
        knit_graph.connect_loops(parent_loop, child_loop, pull_direction=next_pull)
        next_pull = next_pull.opposite()
        next_course.append(child_loop)
    last_course = next_course
    for _ in range(1, height):
        next_course = []
        for parent_loop in reversed(last_course):
            grand_parent = parent_loop.parent_loops[0]
            parent_pull = knit_graph.get_pull_direction(grand_parent, parent_loop)
            assert isinstance(parent_pull, Pull_Direction)
            child_loop = yarn.make_loop_on_end()
            knit_graph.connect_loops(parent_loop, child_loop, pull_direction=parent_pull)
            next_course.append(child_loop)
        last_course = next_course
    return knit_graph


def seed_swatch(width: int, height: int) -> Knit_Graph:
    """Generate a seed stitch swatch with a checkerboard pattern of knit and purl stitches.

    This creates a textured fabric where each stitch alternates between knit and purl both horizontally and vertically, creating a bumpy, non-curling fabric texture.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a seed stitch swatch with checkerboard knit-purl pattern.
    """
    knit_graph, yarn = co_loops(width)
    last_course = knit_graph.get_courses()[0]
    next_course = []
    next_pull = Pull_Direction.BtF
    for parent_loop in reversed(last_course):
        child_loop = yarn.make_loop_on_end()
        knit_graph.connect_loops(parent_loop, child_loop, pull_direction=next_pull)
        next_pull = next_pull.opposite()
        next_course.append(child_loop)
    last_course = next_course
    for _ in range(1, height):
        next_course = []
        for parent_loop in reversed(last_course):
            grand_parent = parent_loop.parent_loops[0]
            parent_pull = knit_graph.get_pull_direction(grand_parent, parent_loop)
            assert isinstance(parent_pull, Pull_Direction)
            child_loop = yarn.make_loop_on_end()
            knit_graph.connect_loops(parent_loop, child_loop, pull_direction=parent_pull.opposite())
            next_course.append(child_loop)
        last_course = next_course
    return knit_graph


def kp_mesh_decrease_left_swatch(width: int, height: int) -> Knit_Graph:
    """Generate a mesh pattern with left-leaning decreases and yarn overs in knit-purl ribbing.

    This creates an openwork mesh pattern where purl stitches are decreased leftward on even courses and replaced with yarn overs,
    creating decorative holes in the fabric while maintaining the overall stitch count.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a mesh swatch with left-leaning decreases and yarn overs.
    """
    # k<o k<o k <-: 1->2
    # |\  |\
    # k p k p k ->: 0->1
    # 0 1 2 3 4
    knit_graph, yarn = co_loops(width)
    last_course = knit_graph.get_courses()[0]
    next_course = []
    next_pull = Pull_Direction.BtF
    for parent_loop in reversed(last_course):
        child_loop = yarn.make_loop_on_end()
        knit_graph.connect_loops(parent_loop, child_loop, pull_direction=next_pull)
        next_pull = next_pull.opposite()
        next_course.append(child_loop)
    last_course = next_course
    for _ in range(1, height):
        next_course = []
        for parent_loop in reversed(last_course):
            child_loop = yarn.make_loop_on_end()
            grand_parent = parent_loop.parent_loops[0]
            parent_pull = knit_graph.get_pull_direction(grand_parent, parent_loop)
            if parent_pull is Pull_Direction.BtF:  # knits stay in decrease at bottom of stack
                knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.BtF, stack_position=0)
                prior_parent = yarn.prior_loop(parent_loop)
                if prior_parent is not None and prior_parent in last_course:
                    knit_graph.connect_loops(prior_parent, child_loop, pull_direction=Pull_Direction.FtB, stack_position=1)
            next_course.append(child_loop)
        last_course = next_course
        next_course = []
        for parent_loop in reversed(last_course):
            child_loop = yarn.make_loop_on_end()
            if len(parent_loop.parent_loops) == 0:
                knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.FtB)
            else:
                knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.BtF)
            next_course.append(child_loop)
        last_course = next_course
    return knit_graph


def kp_mesh_decrease_right_swatch(width: int, height: int) -> Knit_Graph:
    """Generate a mesh pattern with right-leaning decreases and yarn overs in knit-purl ribbing.

    This creates an openwork mesh pattern where purl stitches are decreased rightward on even courses and replaced with yarn overs,
    creating decorative holes in the fabric while maintaining the overall stitch count.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a mesh swatch with right-leaning decreases and yarn overs.
    """
    # k o>k o>k <-: 1->2
    #    /|  /|
    # k p k p k ->: 0->1
    # 0 1 2 3 4
    knit_graph, yarn = co_loops(width)
    last_course = knit_graph.get_courses()[0]
    next_course = []
    next_pull = Pull_Direction.BtF
    for parent_loop in reversed(last_course):
        child_loop = yarn.make_loop_on_end()
        knit_graph.connect_loops(parent_loop, child_loop, pull_direction=next_pull)
        next_pull = next_pull.opposite()
        next_course.append(child_loop)
    last_course = next_course
    for _ in range(1, height):
        next_course = []
        for parent_loop in reversed(last_course):
            child_loop = yarn.make_loop_on_end()
            grand_parent = parent_loop.parent_loops[0]
            parent_pull = knit_graph.get_pull_direction(grand_parent, parent_loop)
            if parent_pull is Pull_Direction.BtF:  # knits stay in decrease at bottom of stack
                knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.BtF, stack_position=0)
                next_parent = yarn.next_loop(parent_loop)
                if next_parent is not None:
                    knit_graph.connect_loops(next_parent, child_loop, pull_direction=Pull_Direction.FtB, stack_position=1)
            next_course.append(child_loop)
        last_course = next_course
        next_course = []
        for parent_loop in reversed(last_course):
            child_loop = yarn.make_loop_on_end()
            if len(parent_loop.parent_loops) == 0:
                knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.FtB)
            else:
                knit_graph.connect_loops(parent_loop, child_loop, pull_direction=Pull_Direction.BtF)
            next_course.append(child_loop)
        last_course = next_course
    return knit_graph


def twist_cable(width: int, height: int) -> Knit_Graph:
    """Generate a twisted cable pattern with alternating crossing directions and purl separators.

    This creates a cable pattern with 1x1 twists that alternate direction every two rows, separated by purl wales to make the cable structure more prominent.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a twisted cable pattern with alternating crossing directions.
    """
    # p k\k p ->: 3-4
    # p k k p <-: 2-3
    # p k/k p ->: 1-2
    # p k k p <-: 0-1
    # 0 1 2 3
    knit_graph, yarn = co_loops(width)
    last_course = knit_graph.get_courses()[0]
    next_course = []
    pull_directions = [Pull_Direction.FtB, Pull_Direction.BtF, Pull_Direction.BtF, Pull_Direction.FtB]
    for i, parent_loop in enumerate(reversed(last_course)):
        child_loop = yarn.make_loop_on_end()
        knit_graph.connect_loops(parent_loop, child_loop, pull_direction=pull_directions[i % 4])
        next_course.append(child_loop)
    last_course = next_course
    crossing = Crossing_Direction.Over_Right
    for r in range(1, height):
        next_course = [yarn.make_loop_on_end() for _ in last_course]
        for i, parent_loop in enumerate(reversed(last_course)):
            if r % 2 == 0 or i % 4 == 0 or i % 4 == 3:  # not cable row (even) or in purl wale
                child_loop = next_course[i]
            elif i % 4 == 1:
                child_loop = next_course[i + 1]
            else:
                child_loop = next_course[i - 1]
            knit_graph.connect_loops(parent_loop, child_loop, pull_direction=pull_directions[i % 4])
        if r % 2 == 1:  # cable row
            for left_loop, right_loop in zip(next_course[1::4], next_course[2::4]):
                knit_graph.add_crossing(left_loop, right_loop, crossing)
            crossing = ~crossing
        last_course = next_course
    return knit_graph
