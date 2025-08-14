"""This module supports visualization of knit-graphs using the plotly library."""
from typing import Any, Iterable, cast

import plotly.graph_objects as go
from networkx import DiGraph

from knit_graphs.artin_wale_braids.Crossing_Direction import Crossing_Direction
from knit_graphs.Course import Course
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Loop import Loop
from knit_graphs.Pull_Direction import Pull_Direction


def get_base_row_course_positions(course: Course, start_on_left: bool, loop_space: float = 1.0) -> tuple[dict[Loop, float], float, float]:
    """
    :param course: course assumed to be base of knit graph for visualization.
    :param start_on_left: If True, loops will start on left side of plot.
    :param loop_space: spacing between loops.
    :return: dictionary of loops in course keyed to x position. The minimum loop position. The maximum loop position.
    """
    loops: Iterable[Loop] = list(course)
    if not start_on_left:
        loops = reversed(course)
    positions = {l: x * loop_space for x, l in enumerate(loops)}
    return positions, min(positions.values()), max(positions.values())


def get_base_round_course_positions(course: Course, start_on_left: bool,
                                    loop_space: float = 1.0, back_shift: float = 0.5) -> tuple[dict[Loop, float], dict[Loop, float], float, float]:
    """
    :param back_shift: Shift in x position for back bed loop s that can't be placed by float inference.
    :param course: Course assumed to be base of knit graph for visualization.
    :param start_on_left: If True, loops will start on the left side of plot.
    :param loop_space: Spacing between loops.
    :return: Dictionary of loops in front of the course keyed to x position.
     Dictionary of loops in the back of the course keyed to x position.
      Min loop position. Max loop position
    """
    split_index = int(len(course) / 2)
    front_loops: list[Loop] = cast(list[Loop], course[:split_index])
    back_loops: list[Loop] = cast(list[Loop], course[split_index:])
    if start_on_left:
        back_loops = [*reversed(back_loops)]
    else:
        front_loops = [*reversed(back_loops)]
    front_positions = {l: x * loop_space for x, l in enumerate(front_loops)}
    back_positions = {l: x * loop_space + back_shift for x, l in enumerate(back_loops)}
    for back_loop in back_loops:
        float_positions = [front_positions[fl] for fl in back_loop.front_floats if fl in front_positions]
        if len(float_positions) > 0:
            back_positions[back_loop] = sum(float_positions) / len(float_positions)
    min_front = min(front_positions.values())
    max_front = max(front_positions.values())
    min_back = min(back_positions.values())
    max_back = max(back_positions.values())
    return front_positions, back_positions, min(min_front, min_back), max(max_front, max_back)


def get_loop_x_by_parent_average(data_graph: DiGraph, loop: Loop) -> float | None:
    """
    :param data_graph: Collection of loop nodes to assigned locations.
    :param loop: Loop to derive location for.
    :return: X position derived from parent_loop locations for loop.
    """

    def _parent_weight(stack_position: int) -> int:
        return len(loop.parent_loops) - stack_position

    parent_positions = {data_graph.nodes[p]['x'] * _parent_weight(sp): _parent_weight(sp)
                        for sp, p in enumerate(loop.parent_loops)
                        if p in data_graph.nodes}
    if len(parent_positions) == 0:
        return None
    return float(sum(parent_positions.keys())) / float(sum(parent_positions.values()))


def get_loop_x_by_yarn_neighbor_average(data_graph: DiGraph, loop: Loop, prior_space: int = 1, next_space: int = -1) -> float | None:
    """
    :param data_graph: Collection of loop nodes to assigned locations.
    :param loop: Loop to place.
    :param prior_space: Spacing from this loop to prior on yarn.
    :param next_space: Spacing from this loop to next on yarn.
    :return: None if no neighbors are placed or assign x position by neighbors on yarn.
    """
    x_neighbors = []
    prior_loop = loop.prior_loop_on_yarn()
    next_loop = loop.next_loop_on_yarn()
    if prior_loop is not None and prior_loop in data_graph.nodes:
        x_neighbors.append(data_graph.nodes[prior_loop]['x'] + prior_space)
    if next_loop is not None and next_loop in data_graph.nodes:
        x_neighbors.append(data_graph.nodes[next_loop]['x'] + next_space)
    if len(x_neighbors) == 0:
        return None
    return float(sum(x_neighbors)) / float(len(x_neighbors))


def re_balance_course(data_graph: DiGraph, course: Course, target_width: float | None,
                      left_side: float = 0, right_side: float | None = None) -> dict[Loop, float]:
    """
    :param target_width: Width to retarget to. Defaults to definition from right side value.
    :param data_graph:  Collection of loop nodes to assign locations.
    :param course: The course to re-balance.
    :param left_side: The minimum left position of the course.
    :param right_side: The maximum right position of the course. Defaults to right most loop position.
    :return: Dictionary of loops to rebalanced positions.
    Maintains original float proportions of each loop but assigns positions between left and right side values.
    """
    min_x, min_loop = min_x_in_course(course, data_graph)
    max_x, max_loop = max_x_in_course(course, data_graph)
    course_width = max_x - min_x
    if target_width is None:
        if right_side is None:
            right_side = max_x
        target_width = right_side - left_side

    def _target_float_size(u: Loop, v: Loop) -> float:
        current_size = abs(data_graph.nodes[u]['x'] - data_graph.nodes[v]['x'])
        return float((current_size * target_width)) / float(course_width)

    return {l: _target_float_size(min_loop, l) + left_side for l in course}


def max_x_in_course(course: Course, data_graph: DiGraph) -> tuple[float, Loop]:
    """
    :param course:
    :param data_graph:
    :return: right most x position in course, loop with right most x position
    """
    return max([(data_graph.nodes[l]['x'], l) for l in course], key=lambda tup: tup[0])


def min_x_in_course(course: Course, data_graph: DiGraph) -> tuple[float, Loop]:
    """
    :param course:
    :param data_graph:
    :return: left most x position in course, loop with left most x position
    """
    return min([(data_graph.nodes[l]['x'], l) for l in course], key=lambda tup: tup[0])


def get_loop_y_by_neighbor_floats(data_graph: DiGraph, loop: Loop, float_buffer: float = 0.25) -> float | None:
    """
    :param data_graph: Collection of loop nodes to assign locations.
    :param loop: Loop to assign y location by neighboring floats.
    :param float_buffer: Spacing between loop and its neighboring floats.
    :return: Y position of loop or None if loop has no neighboring floats.
    """
    positions = [data_graph.nodes[fl]['y'] + float_buffer for fl in loop.front_floats if fl in data_graph.nodes]
    positions.extend([data_graph.nodes[bl]['y'] - float_buffer for bl in loop.back_floats if bl in data_graph.nodes])
    if len(positions) == 0:
        return None
    return float(sum(positions) / len(positions))


def shift_purls(knit_graph: Knit_Graph, data_graph: DiGraph, purl_shift: float = 0.25) -> None:
    """
    Shifts the position of each stitch involved in purls to make the look of knit-purl patterns more distinct.
    Args:
        knit_graph: The Knit_Graph to visualize purls in.
        data_graph: The digraph of data used to create the visualization.
        purl_shift: The amount to shift the purl stitches vertically by.
    """
    shifted = set()
    for u, v in knit_graph.stitch_graph.edges:
        if v not in shifted:
            pull_direction = knit_graph.get_pull_direction(u, v)
            if pull_direction is Pull_Direction.FtB:
                data_graph.nodes[v]['x'] += purl_shift
                shifted.add(v)
                if len(u.parent_loops) == 0:  # purl coming from yarn over
                    data_graph.nodes[u]['x'] += purl_shift
                    shifted.add(u)


def visualize_stitches(knit_graph: Knit_Graph,
                       first_course_index: int = 0, top_course_index: int | None = None,
                       start_on_left: bool = True,
                       re_balance_to_course_width: bool = False,
                       re_balance_to_base_width: bool = False,
                       left_zero_align: bool = True,
                       graph_title: str = "knit_graph") -> None:
    """
    Generates a plotly visualization of the given knitgraph based on the given configuration.

    Args:
        knit_graph:
        first_course_index:
        top_course_index:
        start_on_left:
        re_balance_to_course_width (bool):
        re_balance_to_base_width (bool): If set to true, the visualization will be rebalanced to space nodes evenly according to the base-course width of the knit graph.
        left_zero_align (bool): If True, aligns the 0th position with the left of the figure. Defaults to True.
        graph_title (str): The name of the figure. Defaults to "knit_graph".

    """
    data_graph = position_loops(first_course_index, knit_graph, left_zero_align, re_balance_to_base_width, re_balance_to_course_width, start_on_left, top_course_index)

    yarn_loop_traces = collect_yarn_loop_traces(data_graph, knit_graph)

    yarn_float_traces = collect_yarn_float_traces(data_graph, knit_graph)

    def _new_edge_data() -> dict[str: list]:
        return {'x': [], 'y': [], 'edge': [], 'is_start': []}

    def _add_edge_data(edge_data: dict[str, list], u_loop: Loop, v_loop: Loop) -> None:
        data_graph.add_edge(u_loop, v_loop, pull_direction=pull_direction)
        edge_data['x'].append(data_graph.nodes[u_loop]['x'])
        edge_data['y'].append(data_graph.nodes[u_loop]['y'])
        edge_data['edge'].append((u_loop, v_loop))
        edge_data['is_start'].append(True)
        edge_data['x'].append(data_graph.nodes[v_loop]['x'])
        edge_data['y'].append(data_graph.nodes[v_loop]['y'])
        edge_data['edge'].append((u_loop, v_loop))
        edge_data['is_start'].append(False)
        edge_data['x'].append(None)
        edge_data['y'].append(None)

    top_knit_data = _new_edge_data()
    bot_knit_data = _new_edge_data()
    top_purl_data = _new_edge_data()
    bot_purl_data = _new_edge_data()
    no_cross_knit_data = _new_edge_data()
    no_cross_purl_data = _new_edge_data()

    for left_loop, right_loop in knit_graph.braid_graph.loop_crossing_graph.edges:
        crossing_direction = knit_graph.braid_graph.get_crossing(left_loop, right_loop)
        for left_parent in left_loop.parent_loops:
            pull_direction: Pull_Direction = knit_graph.stitch_graph[left_parent][left_loop]['pull_direction']
            data_graph.add_edge(left_parent, left_loop, pull_direction=pull_direction)
            if pull_direction is Pull_Direction.BtF:  # knit
                if crossing_direction is Crossing_Direction.Over_Right:
                    data = top_knit_data
                elif crossing_direction is Crossing_Direction.Under_Right:
                    data = bot_knit_data
                else:
                    data = no_cross_knit_data
            else:
                if crossing_direction is Crossing_Direction.Over_Right:
                    data = top_purl_data
                elif crossing_direction is Crossing_Direction.Under_Right:
                    data = bot_purl_data
                else:
                    data = no_cross_knit_data
            _add_edge_data(data, left_parent, left_loop)
        for right_parent in right_loop.parent_loops:
            pull_direction: Pull_Direction = knit_graph.stitch_graph[right_parent][right_loop]['pull_direction']
            data_graph.add_edge(right_parent, right_loop, pull_direction=pull_direction)
            if pull_direction is Pull_Direction.BtF:  # knit
                if crossing_direction is Crossing_Direction.Under_Right:
                    data = top_knit_data
                elif crossing_direction is Crossing_Direction.Over_Right:
                    data = bot_knit_data
                else:
                    data = no_cross_knit_data
            else:
                if crossing_direction is Crossing_Direction.Under_Right:
                    data = top_purl_data
                elif crossing_direction is Crossing_Direction.Over_Right:
                    data = bot_purl_data
                else:
                    data = no_cross_purl_data
            _add_edge_data(data, right_parent, right_loop)

    for u, v in knit_graph.stitch_graph.edges:
        if not data_graph.has_edge(u, v):
            pull_direction: Pull_Direction = knit_graph.stitch_graph[u][v]['pull_direction']
            if pull_direction is Pull_Direction.BtF:  # knit
                _add_edge_data(no_cross_knit_data, u, v)
            else:
                _add_edge_data(no_cross_purl_data, u, v)

    no_cross_knit_trace = go.Scatter(name="Knit Stitches (No Crossing)",
                                     x=no_cross_knit_data['x'], y=no_cross_knit_data['y'],
                                     line=dict(width=4, color='blue', dash='solid'),
                                     opacity=0.8,
                                     mode='lines')
    top_knit_trace = go.Scatter(name="Knit Stitches (Crossing Over)",
                                x=top_knit_data['x'], y=top_knit_data['y'],
                                line=dict(width=5, color='blue', dash='solid'),
                                opacity=1,
                                mode='lines')
    bot_knit_trace = go.Scatter(name="Knit Stitches (Crossing Under)",
                                x=bot_knit_data['x'], y=bot_knit_data['y'],
                                line=dict(width=3, color='blue', dash='dash'),
                                opacity=.5,
                                mode='lines')
    no_cross_purl_trace = go.Scatter(name="Purl Stitches",
                                     x=no_cross_purl_data['x'], y=no_cross_purl_data['y'],
                                     line=dict(width=4, color='red', dash='solid'),
                                     opacity=0.8,
                                     mode='lines')
    top_purl_trace = go.Scatter(name="Purl Stitches (Crossing Over)",
                                x=top_purl_data['x'], y=top_knit_data['y'],
                                line=dict(width=5, color='red', dash='solid'),
                                opacity=1,
                                mode='lines')
    bot_purl_trace = go.Scatter(name="Purl Stitches (Crossing Under)",
                                x=bot_purl_data['x'], y=bot_purl_data['y'],
                                line=dict(width=3, color='red', dash='dash'),
                                opacity=.5,
                                mode='lines')

    go_layout = go.Layout(title=graph_title,
                          showlegend=True,
                          hovermode='closest',
                          margin=dict(b=20, l=5, r=5, t=40)
                          )
    figure_data = [top_knit_trace, top_purl_trace,
                   no_cross_knit_trace, no_cross_purl_trace,
                   bot_knit_trace, bot_purl_trace]
    figure_data.extend(yarn_float_traces)
    figure_data.extend(yarn_loop_traces)
    fig = go.Figure(data=figure_data,
                    layout=go_layout
                    )
    fig.show()


def position_loops(first_course_index: int, knit_graph: Knit_Graph, left_zero_align: bool, re_balance_to_base_width: bool, re_balance_to_course_width: bool,
                   start_on_left: bool, top_course_index: int | None = None) -> DiGraph:
    """

    Args:
        first_course_index:
        knit_graph:
        left_zero_align:
        re_balance_to_base_width:
        re_balance_to_course_width:
        start_on_left:
        top_course_index:

    Returns:

    """
    data_graph = DiGraph()
    courses = knit_graph.get_courses()
    loops_to_course = {}
    if top_course_index is not None:
        courses = courses[:top_course_index]
    base_course = courses[first_course_index]
    for loop in base_course:
        loops_to_course[loop] = base_course
    if len(courses) > first_course_index + 1 and base_course.in_round_with(courses[first_course_index + 1]):
        front_positions, back_positions, min_x, max_x = get_base_round_course_positions(base_course, start_on_left)
        for loop, x in front_positions.items():
            data_graph.add_node(loop, x=x, y=0)
        for loop, x in back_positions.items():
            # y = get_loop_y_by_neighbor_floats(data_graph, loop)
            # if y is None:
            #     y = .25
            data_graph.add_node(loop, x=x, y=0)
    else:
        positions, min_x, max_x = get_base_row_course_positions(base_course, start_on_left)
        for loop, x in positions.items():
            data_graph.add_node(loop, x=x, y=0)
    base_width = max_x - min_x
    y = 1
    for course in courses[first_course_index + 1:]:
        need_x_placement = {}
        for x, loop in enumerate(course):
            loops_to_course[loop] = course
            parent_average_x = get_loop_x_by_parent_average(data_graph, loop)
            if parent_average_x is None:
                need_x_placement[loop] = x
            else:
                x = parent_average_x
            # float_placed_y = get_loop_y_by_neighbor_floats(data_graph, loop)
            # if float_placed_y is not None:
            #     y = float_placed_y
            data_graph.add_node(loop, x=x, y=y)
        for loop in need_x_placement.keys():
            neighbor_based_x = get_loop_x_by_yarn_neighbor_average(data_graph, loop)
            if neighbor_based_x is not None:
                data_graph.nodes[loop]['x'] = neighbor_based_x
        # swap x positions based on cable crossings
        for left_loop in course:
            for right_loop in knit_graph.braid_graph.left_crossing_loops(left_loop):
                crossing_direction = knit_graph.braid_graph.get_crossing(left_loop, right_loop)
                if crossing_direction is not Crossing_Direction.No_Cross:
                    left_x = data_graph.nodes[left_loop]['x']
                    data_graph.nodes[left_loop]['x'] = data_graph.nodes[right_loop]['x']
                    data_graph.nodes[right_loop]['x'] = left_x
        new_positions = {}
        left_side = 0.0
        if not left_zero_align:
            left_side, left_loop = min_x_in_course(course, data_graph)
        if re_balance_to_course_width:
            new_positions = re_balance_course(data_graph, course, len(course) - 1, left_side)
        elif re_balance_to_base_width:
            new_positions = re_balance_course(data_graph, course, base_width, left_side)
        for l, x in new_positions.items():
            data_graph.nodes[l]['x'] = x
        y += 1
    adjust_y_positions_by_float_alignment(data_graph, knit_graph, loops_to_course)
    shift_purls(knit_graph, data_graph)
    return data_graph


def adjust_y_positions_by_float_alignment(data_graph: DiGraph, knit_graph: Knit_Graph, loops_to_course: dict[Loop, Course], float_increment: float = 0.25) -> None:
    """

    Args:
        data_graph:
        knit_graph:
        loops_to_course:
        float_increment:
    """
    for yarn in knit_graph.yarns:
        for u, v, front_loops in yarn.loops_in_front_of_floats():
            for fl in front_loops:
                fl_course = loops_to_course[fl]
                if u in fl_course and v in fl_course:  # same course, adjust float position
                    data_graph.nodes[fl]['y'] -= float_increment
        for u, v, back_loops in yarn.loops_behind_floats():
            for bl in back_loops:
                bl_course = loops_to_course[bl]
                if u in bl_course and v in bl_course:  # same course, adjust float position
                    data_graph.nodes[bl]['y'] += float_increment


def collect_yarn_float_traces(data_graph: DiGraph, knit_graph: Knit_Graph) -> list[Any]:
    """
    :param data_graph: Collection of loop nodes to assign locations.
    :param knit_graph: The knit graph to derive loop data from.
    :return: The traces of the yarns-loop nodes for the graph
    """
    yarns_to_float_data = {}
    for y in knit_graph.yarns:
        float_data: dict[str, list[float]] = {'x': [], 'y': []}
        for u, v in y.loop_graph.edges:
            float_data['x'].append(data_graph.nodes[u]['x'])
            float_data['y'].append(data_graph.nodes[u]['y'])
            float_data['x'].append(data_graph.nodes[v]['x'])
            float_data['y'].append(data_graph.nodes[v]['y'])
        yarns_to_float_data[y] = float_data
    for y in knit_graph.yarns:
        float_data = {'x': [], 'y': []}
        for u in y.loop_graph.nodes:
            float_data['x'].append(data_graph.nodes[u]['x'])
            float_data['y'].append(data_graph.nodes[u]['y'])
        yarns_to_float_data[y] = float_data
    yarn_float_traces = [go.Scatter(name=y.yarn_id,
                                    x=fd['x'], y=fd['y'],
                                    line=dict(width=1,
                                              color=y.properties.color,
                                              shape='spline',
                                              smoothing=1.3),
                                    mode='lines')
                         for y, fd in yarns_to_float_data.items()]
    return yarn_float_traces


def collect_yarn_loop_traces(data_graph: DiGraph, knit_graph: Knit_Graph) -> list[Any]:
    """
    :param data_graph: Collection of loop nodes to assign locations.
    :param knit_graph: The knit graph to derive loop data from.
    :return: The traces of the yarns-float edges for the graph
    """
    yarns_to_loop_data = {y: {'x': [data_graph.nodes[l]['x'] for l in y],
                              'y': [data_graph.nodes[l]['y'] for l in y],
                              'loop_id': [l.loop_id for l in y]
                              }
                          for y in knit_graph.yarns
                          }
    yarn_loop_traces = [go.Scatter(name=f"Loops on {y.yarn_id}", x=yd['x'], y=yd['y'], text=yd['loop_id'],
                                   textposition='middle center',
                                   mode='markers+text',
                                   marker=dict(
                                       reversescale=True,
                                       color=y.properties.color,
                                       size=30,
                                       line_width=2, ))
                        for y, yd in yarns_to_loop_data.items()
                        ]
    return yarn_loop_traces
