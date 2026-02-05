"""Module of functions that generate basic knit graph swatches.

This module provides utility functions for creating common knitting patterns and structures as knit graphs.
These functions serve as building blocks for testing and demonstration purposes.
"""

from __future__ import annotations

from collections.abc import Sequence

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.knit_graph_builder import Knit_Graph_Builder
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction
from knit_graphs.Yarn import Yarn


def co_loops(width: int) -> tuple[Knit_Graph_Builder[Loop], Knit_Graph[Loop], Yarn[Loop]]:
    """Create a cast-on row of loops forming the foundation for knitting patterns.

    Args:
        width (int): The number of loops to create in the cast-on row.

    Returns:
        tuple[Knit_Graph_Builder[Loop], Knit_Graph[Loop], Yarn[Loop]: A tuple containing the knit graph builder and its knitgraph with one course of the specified width and the yarn used to create it.
    """
    builder = Knit_Graph_Builder[Loop]()
    yarn = builder.add_yarn()
    for _ in range(0, width):
        _loop = builder.tuck(yarn)
    return builder, builder.knit_graph, yarn


def jersey_swatch(width: int, height: int) -> Knit_Graph[Loop]:
    """Generate a rectangular knit swatch with all knit stitches in a flat sheet structure.

    This creates a basic stockinette/jersey pattern where all stitches are worked as knit stitches from back to front.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a flat rectangular swatch with all knit stitches.
    """
    builder, knit_graph, yarn = co_loops(width)
    last_course: Sequence[Loop] = knit_graph.get_courses()[0]
    for _ in range(0, height):
        last_course = [builder.knit(yarn, [parent_loop]) for parent_loop in reversed(last_course)]
    return knit_graph


def jersey_tube(tube_width: int, height: int) -> Knit_Graph[Loop]:
    """Generate a tubular knit structure with all knit stitches worked in the round.

    This creates a seamless tube by knitting in the round, where the front and back sections are connected by floats to maintain the circular structure.

    Args:
        tube_width (int): The number of stitches per course on the front side of the tube.
        height (int): The number of courses (vertical rows) in the tube.

    Returns:
        Knit_Graph: A knit graph representing a seamless tube with all knit stitches.
    """
    builder = Knit_Graph_Builder[Loop]()
    yarn = builder.add_yarn()
    front_of_tube = [builder.tuck(yarn) for _ in range(0, tube_width)]
    back_of_tube = [builder.tuck(yarn) for _ in reversed(front_of_tube)]
    for _ in range(0, height):
        for fl, bl in zip(front_of_tube[:-1], reversed(back_of_tube[1:]), strict=False):
            builder.position_float(fl, loops_behind_float=[bl])
        for fl, bl in zip(reversed(front_of_tube[1:]), back_of_tube[:-1], strict=False):
            builder.position_float(bl, loops_in_front_of_float=[fl])
        front_of_tube = [builder.knit(yarn, [fl], Pull_Direction.BtF) for fl in front_of_tube]
        back_of_tube = [builder.knit(yarn, [bl], Pull_Direction.FtB) for bl in back_of_tube]

    return builder.knit_graph


def kp_rib_swatch(width: int, height: int) -> Knit_Graph[Loop]:
    """Generate a knit-purl ribbing swatch with alternating wales of knit and purl stitches.

    This creates a 1x1 ribbing pattern where knit and purl wales alternate, maintaining their stitch type throughout the height of the swatch for a stretchy, textured fabric.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a ribbed swatch with alternating knit and purl wales.
    """
    builder, knit_graph, yarn = co_loops(width)
    last_course: Sequence[Loop] = knit_graph.get_courses()[0]
    for _ in range(0, height):
        assert yarn.last_loop is not None
        pull_direction = yarn.last_loop.pull_directions[0] if yarn.last_loop.has_parent_loops else Pull_Direction.BtF
        last_course = [
            builder.knit(yarn, [parent_loop], pull_direction=pull_direction if i % 2 == 0 else pull_direction.opposite)
            for i, parent_loop in enumerate(reversed(last_course))
        ]
    return knit_graph


def seed_swatch(width: int, height: int) -> Knit_Graph[Loop]:
    """Generate a seed stitch swatch with a checkerboard pattern of knit and purl stitches.

    This creates a textured fabric where each stitch alternates between knit and purl both horizontally and vertically, creating a bumpy, non-curling fabric texture.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a seed stitch swatch with checkerboard knit-purl pattern.
    """
    builder, knit_graph, yarn = co_loops(width)
    last_course: Sequence[Loop] = knit_graph.get_courses()[0]
    for _ in range(0, height):
        assert yarn.last_loop is not None
        pull_direction = yarn.last_loop.pull_directions[0] if yarn.last_loop.has_parent_loops else Pull_Direction.BtF
        last_course = [
            builder.knit(yarn, [parent_loop], pull_direction=pull_direction.opposite if i % 2 == 0 else pull_direction)
            for i, parent_loop in enumerate(reversed(last_course))
        ]
    return knit_graph


def lace_mesh(width: int, height: int) -> Knit_Graph[Loop]:
    """Generate a mesh pattern with alternating left and right leaning decrease paired to yarn-overs.
    These pairings create a basic lace pattern with eyelets formed around the increases.

    Args:
        width (int): The number of stitches per course (horizontal row).
        height (int): The number of courses (vertical rows) in the swatch.

    Returns:
        Knit_Graph: A knit graph representing a mesh swatch.
    """
    builder, knit_graph, yarn = co_loops(width)
    last_course = [builder.knit(yarn, [p]) for p in reversed(knit_graph.get_courses()[0])]
    for _ in range(1, height):
        dec1 = last_course[1::3]
        dec2 = last_course[2::3]
        decs = [
            dec_parents if i % 2 == 0 else (dec_parents[1], dec_parents[0])
            for i, dec_parents in enumerate(zip(reversed(dec1), reversed(dec2), strict=False))
        ]
        knits = last_course[0::3]
        next_course = []
        for i, parent_loop in enumerate(reversed(knits)):
            next_course.append(builder.knit(yarn, [parent_loop]))
            if len(decs) > 0:
                if i % 2 == 0:
                    next_course.append(builder.tuck(yarn))
                    next_course.append(builder.knit(yarn, decs.pop(0)))
                else:
                    next_course.append(builder.knit(yarn, decs.pop(0)))
                    next_course.append(builder.tuck(yarn))
        last_course = [builder.knit(yarn, [p]) for p in reversed(next_course)]
    return knit_graph


def twist_cable(width: int, height: int) -> Knit_Graph[Loop]:
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
    builder, knit_graph, yarn = co_loops(width)
    pull_directions = [
        Pull_Direction.FtB,
        Pull_Direction.BtF,
        Pull_Direction.BtF,
        Pull_Direction.FtB,
    ]
    last_course = [
        builder.knit(yarn, [p], pull_directions[i % 4]) for i, p in enumerate(reversed(knit_graph.get_courses()[0]))
    ]
    for r in range(1, height, 2):
        crossed_course: list[Loop] = []
        for i, parent_loop in enumerate(last_course):
            if i % 4 == 2:
                crossed_course.insert(-1, parent_loop)
            else:
                crossed_course.append(parent_loop)
        last_course = [builder.knit(yarn, [p]) for p in reversed(crossed_course)]
        left_cable_loops = last_course[-2:0:-4]
        right_cable_loops = last_course[-3:0:-4]
        for left_loop, right_loop in zip(left_cable_loops, right_cable_loops, strict=False):
            if r % 4 == 1:
                builder.xfer(left_loop, over_loops_to_right=[right_loop])
            else:
                builder.xfer(left_loop, under_loops_to_right=[right_loop])
        last_course = [builder.knit(yarn, [p]) for p in reversed(last_course)]

    return knit_graph
