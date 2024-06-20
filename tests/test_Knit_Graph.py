from unittest import TestCase

from knit_graphs.knit_graph_generators.basic_knit_graph_generators import kp_mesh_decrease_left_swatch, kp_mesh_decrease_right_swatch, twist_cable, jersey_tube, jersey_swatch, kp_rib_swatch, \
    seed_swatch


class TestKnit_Graph(TestCase):
    def test_mesh(self):
        generators = [kp_mesh_decrease_left_swatch, kp_mesh_decrease_right_swatch]
        width = 11
        height = 10
        for generator in generators:
            print(f"Mesh test of height {height}  and width {width} on {generator.__name__}")
            _knit_graph = generator(width, height)

    def test_twist_cable(self):
        generators = [twist_cable]
        width = 12
        height = 10
        for generator in generators:
            print(f"Twist Cable test of height {height}  and width {width} on {generator.__name__}")
            _knit_graph = generator(width, height)

    def test_tube_in_round(self):
        width = 4
        height = 4
        knit_graph = jersey_tube(width, height)
        courses = knit_graph.get_courses()
        assert len(courses) == height+1, f"Expected tube courses to be {height+1} but got {len(courses)}"
        for prior_course, next_course in zip(courses[:-1], courses[1:]):
            assert prior_course.in_round_with(next_course), f"{prior_course} not in round with {next_course}"

    def test_course_count(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        width = 10
        for generator in generators:
            height = 10
            print(f"Course test of height {height + 1} on {generator.__name__}")
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"

            height = 11
            print(f"Course test of height {height + 1} on {generator.__name__}")
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"
            knit_graph = generator(width, height)
            courses = knit_graph.get_courses()
            assert len(courses) == height + 1, f"Expected courses to be {height + 1} but got {len(courses)}"

    def test_wale_count(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        height = 10
        for generator in generators:
            width = 10
            print(f"Wale test of height {height} and width {width} on {generator.__name__}")
            knit_graph = generator(width, height)
            wale_groups = knit_graph.get_wale_groups()
            assert len(wale_groups) == width, f"Expected wale_groups to be {width} but got {len(wale_groups)}"

            width = 11
            print(f"Wale test of height {height} and width {width} on {generator.__name__}")
            knit_graph = generator(width, height)
            wale_groups = knit_graph.get_wale_groups()
            assert len(wale_groups) == width, f"Expected wale_groups to be {width} but got {len(wale_groups)}"

        width = 10
        print(f"Wale test of height {height} and tube width {width} on Jersey Tube")
        knit_graph = jersey_tube(width, height)
        wale_groups = knit_graph.get_wale_groups()
        assert len(wale_groups) == width * 2, f"Expected wale_groups to be {width * 2} but got {len(wale_groups)}"
