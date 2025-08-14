"""Module of functions that generate basic knit graph swatches."""
from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn


def co_loops(width: int) -> tuple[Knit_Graph, Yarn]:
    """
    :param width:
    :return: Knit Graph with one course of length width
    """
    knit_graph = Knit_Graph()
    yarn = Yarn(knit_graph=knit_graph)
    for _ in range(0, width):
        _loop = yarn.make_loop_on_end()
    return knit_graph, yarn


def jersey_swatch(width: int, height: int) -> Knit_Graph:
    """
    :param width: number of stitches per course
    :param height: number of loops per course
    :return: Generate a Knitgraph of width and height with all knit stitches in a sheet structure
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
    """
    :param tube_width: number of stitches per course on front side of tube
    :param height: number of loops per course
    :return: Generate a Knitgraph of width and height with all knit stitches in a tube structure
    """
    knit_graph, yarn = co_loops(tube_width * 2)
    last_course = [*knit_graph.get_courses()[0]]

    def _set_tube_floats() -> None:
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
    """
    :param width: number of stitches per course
    :param height: number of loops per course
    :return: Generate a Knitgraph of width and height with alternating wales of knit purl stitches in a sheet structure
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
    """
    :param width: number of stitches per course
    :param height: number of loops per course
    :return: Generate a Knitgraph of width and height with checkered knit purl stitches in a sheet structure
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
    """
    :param width: number of stitches per course
    :param height: number of loops per course
    :return: Knit Graph with mesh of kp rib with even courses decreasing purls leftward and replacing them with yarn overs
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
                if prior_parent is not None:
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
    """
    :param width: number of stitches per course
    :param height: number of loops per course
    :return: Knit Graph with mesh of kp rib with even courses decreasing purls rightward and replacing them with yarn overs
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
    """
    :param width: number of stitches per course
    :param height: number of loops per course
    :return: Knit Graph of alternating 1 by 1 twists in different directions with purl wales between them
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
